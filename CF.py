from math import sqrt
from numpy import *
from numpy import linalg as la
import numpy as np
from decimal import Decimal
import math

def pearsSim(inA,inB):
    return 0.5 + 0.5 * np.corrcoef(inA, inB)[0][1]

def distEclud(vecA, vecB):
    return sqrt(sum(power(vecA - vecB, 2)))	
	
def distMan(vecA, vecB):
	return sum(abs(a-b) for a,b in zip(vecA,vecB))

def nth_root(value, n_root):
	root_value = 1/float(n_root)
	return round (Decimal(value) ** Decimal(root_value),3)
	
def distMink(vecA,vecB, p_value = 3):
	return nth_root(sum(pow(abs(a-b),p_value) for a,b in zip(vecA, vecB)),p_value)

def getsim(dataMat, simMeas = pearsSim):
	n = np.shape(dataMat)[1] # number of alarm types
	dat = dataMat.T # error-machine format
	simL = {}

	for item in range(n):
		temp = {}
		simL[item] = {}
		for j in range(n):
			test1 = np.nonzero(dat[item])[0]
			test2 = np.nonzero(dat[j])[0]
			
			items = []
			for i in test1:
				if i in test2: 
					items.append(i)
				
			to_calc_1 = np.array(dat[item][items])
			to_calc_2 = np.array(dat[j][items])

			if len(items) != 0:
				correlation = simMeas(to_calc_1, to_calc_2)
			else:
				correlation = 0
				
			if math.isnan(correlation): 
				correlation = 0
			
			temp[j] = correlation
				# returns r between item and j
			if item not in simL:
				simL[item] = temp
			else:
				simL[item].update(temp)

	return simL

def standEstTest(dataMat, user, similarity, item):
	n = np.shape(dataMat)[1] # number of items
	simTotal = 0.0
	ratSimTotal = 0.0
	item = str(item)
	for j in range(n):
		j = str(j)
		freq = dataMat[user, j]
		if freq == 0: 
			continue
		
		sim = similarity[item][j]
		if sim <= 0: sim = 0
		
		simTotal += sim
		ratSimTotal += sim * freq
		
	if simTotal == 0: 
		return 0
	else: 
		return ratSimTotal/simTotal

def recommend(dataMat, user, simMeas, N=3, estMethod=standEstTest):
    zerorecord = nonzero(np.matrix(dataMat[user,:]).A==0)[1]
    
    if len(zerorecord) == 0: return 'Need replacement'
    itemScores = []
    
    for item in zerorecord:
        estimatedScore = estMethod(dataMat, user, simMeas, item)
        itemScores.append((item, estimatedScore))
    
    return sorted(itemScores, key=lambda jj: jj[1], reverse=True)[:N]



