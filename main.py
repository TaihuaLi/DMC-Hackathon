#!/usr/bin/python

import pprint
import json
import datetime
import CF as ur
import pandas as pd
import numpy as np
from sklearn import preprocessing
#from py2neo import Graph, Path
from py2neo import Graph, Node, Relationship

graph = Graph("http://CPTDS:mYdw4Xq4vWHZZ0693BGj@cptds.sb10.stations.graphenedb.com:24789/db/data/")

# Test insert data
#a = Node("Person", name="Alice")
#tx.create(a)
#b = Node("Person", name="Bob")
#ab = Relationship(a, "KNOWS", b)
#tx.create(ab)
#tx.commit()
#graph.exists(ab)

# Test read data
#query = "MATCH (person1:Person)-[:KNOWS]->(person2:Person) RETURN person1.name AS name1, person2.name AS person2"
#query = "MATCH (person1:Person)-[r]->(person2:Person) RETURN person1, person2, r"
#query = "MATCH (person1:Person)-[r]->(person2:Person) RETURN person1, person2"
#query = "match(n:Fault) return n where n.severity = 'critical' return n"
#query = "match(f:Fault {message:'Hydraulics not on. Press hydraulic ON.'})-[:HAS_CORRECTIVE_ACTION]->(cA) return cA"
query = "match(n) return n"
machineQuery = "match (m:Machine) return m"
argusQuery = "match(m:Machine)-[]->(:Department)-[:BELONGS_TO]->(p:Plant {name:'Argus'}) return m"

data = graph.run(query)

nextActionText = ""

print(data)
for d in data:
    print(d)
#    print d[0]['suggestion']
#    nextActionText = d[0]['suggestion']

machines = graph.run(argusQuery)

for machine in machines:
    print(machine)
    machineId = machine[0]['id']
    machineMaker = machine[0]['maker']
    machineModel = machine[0]['model']

me_df = pd.read_csv("alarm_dat.csv", sep=",", index_col=0)
to_feed = np.array(me_df)
machine_list = list(me_df.index)
error_message = pd.read_csv("error_message.txt", sep=";")
errors = error_message.columns.values
simMat = json.load(open("simMat.txt"))

machineId = 72

if machineId in machine_list:
    to_search = machine_list.index(machineId)
    rec_mes = ur.recommend(to_feed, to_search, simMat)
    mes_id_list = []
    for index in range(len(rec_mes)):
        o_id = rec_mes[index][0]
        mes_id_list.append(o_id)

    predictiveAlarmText1 = errors[mes_id_list[0]]
    predictiveAlarmText2 = errors[mes_id_list[1]]
    predictiveAlarmText3 = errors[mes_id_list[2]]
else:
    predictiveAlarmText1 = "Error: no sufficient data for prediction."
    predictiveAlarmText2 = "Error: no sufficient data for prediction."
    predictiveAlarmText3 = "Error: no sufficient data for prediction."

with open('data.out', 'w') as f:
    f.write("MachineIdVector = [1\n2\n3\n4\n5]\n")
    f.write("AlarmText = Big problem\n")
    f.write("MachineStatusVector = [1\n2\n3\n4\n5]\n")
    f.write("NextActionText = " + nextActionText + "\n")
    f.write("MachineId = " + str(machineId) + "\n")
#    f.write("MachineMaker1 = " + machineMaker1 + "\n")
#    f.write("MachineMaker2 = " + machineMaker2 + "\n")
#    f.write("MachineMaker3 = " + machineMaker3 + "\n")
#    f.write("MachineMaker4 = " + machineMaker4 + "\n")
#    f.write("MachineMaker5 = " + machineMaker5 + "\n")
#    f.write("MachineModel1 = " + machineModel1 + "\n")
#    f.write("MachineModel2 = " + machineModel2 + "\n")
#    f.write("MachineModel3 = " + machineModel3 + "\n")
#    f.write("MachineModel4 = " + machineModel4 + "\n")
#    f.write("MachineModel5 = " + machineModel5 + "\n")
    f.write("PredictiveAlarmText1 = " + predictiveAlarmText1 + "\n")
    f.write("PredictiveAlarmText2 = " + predictiveAlarmText2 + "\n")
    f.write("PredictiveAlarmText3 = " + predictiveAlarmText3 + "\n")
