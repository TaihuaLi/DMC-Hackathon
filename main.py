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

# Test read data
#query = "MATCH (person1:Person)-[:KNOWS]->(person2:Person) RETURN person1.name AS name1, person2.name AS person2"
#query = "MATCH (person1:Person)-[r]->(person2:Person) RETURN person1, person2, r"
#query = "MATCH (person1:Person)-[r]->(person2:Person) RETURN person1, person2"
#query = "match(n:Fault) return n where n.severity = 'critical' return n"
#query = "match(f:Fault {message:'Hydraulics not on. Press hydraulic ON.'})-[:HAS_CORRECTIVE_ACTION]->(cA) return cA"
query = "match(n) return n"
machineQuery = "match (m:Machine) return m"
argusQuery = "match(m:Machine)-[]->(:Department)-[:BELONGS_TO]->(p:Plant {name:'Argus'}) return m"
suggestionQuery = "match  (cA:CorrectiveAction)<-[r]-(f:Fault)<-[:HAD_FAULT]-(m:Machine) return DISTINCT m.id, cA.suggestion"
machineStatusQuery = "match  (cA:CorrectiveAction)<-[r]-(f:Fault)<-[:HAD_FAULT]-(m:Machine) return DISTINCT m.id,m.maker,m.model,m.status,f.message,cA.suggestion ORDER BY m.id"

machine_Id_list = []
nextActionText = []
machine_ids = []
machine_makers = []
machine_models = []
machine_statuses = []
machine_messages = []
machine_suggestions = []

suggestions = graph.run(suggestionQuery)
for suggestion in suggestions:
    id = suggestion['m.id']
    nextActionText.append(suggestion['cA.suggestion'])

machines = graph.run(machineStatusQuery)
index = 0
currentMachineId = 0
for machine in machines:
    if(currentMachineId != machine['m.id']):
        currentMachineId = machine['m.id']
        machine_ids.append(machine['m.id'])
        machine_makers.append(machine['m.maker'])
        machine_models.append(machine['m.model'])
        machine_statuses.append(machine['m.status'])
        machine_messages.append(machine['f.message'])
        machine_suggestions.append(machine['cA.suggestion'])

#
# Load in predictive data
#
me_df = pd.read_csv("alarm_dat.csv", sep=",", index_col=0)
to_feed = np.array(me_df)
machine_list = list(me_df.index)
error_message = pd.read_csv("error_message.txt", sep=";")
errors = error_message.columns.values
simMat = json.load(open("simMat.txt"))

predictiveAlarmText1 = []
predictiveAlarmText2 = []
predictiveAlarmText3 = []
for i in machine_ids:
    machineId = i
    if machineId in machine_list:
        to_search = machine_list.index(machineId)
        rec_mes = ur.recommend(to_feed, to_search, simMat)
        mes_id_list = []
        for index in range(len(rec_mes)):
            o_id = rec_mes[index][0]
            mes_id_list.append(o_id)

        predictiveAlarmText1.append(errors[mes_id_list[0]])
        predictiveAlarmText2.append(errors[mes_id_list[1]])
        predictiveAlarmText3.append(errors[mes_id_list[2]])
    else:
        predictiveAlarmText1.append("Warning: no sufficient data for prediction.")
        predictiveAlarmText2.append("Warning: no sufficient data for prediction.")
        predictiveAlarmText3.append("Warning: no sufficient data for prediction.")

#
# data.out is used by DOME to link the
# variables back to the DOME model
#
with open('data.out', 'w') as f:
    f.write("MachineIdVector = [" + str(machine_ids[0]) + "\n" + str(machine_ids[1]) + "\n" + str(machine_ids[2]) + "\n" + str(machine_ids[3]) + "\n" + str(machine_ids[4]) + "]\n")
    counter = 0
    for message in machine_messages:
        counter = counter + 1
        f.write("AlarmText" + str(counter) + " = " + message + "\n")
        #    f.write("MachineStatusVector = [" + str(machineStatus1) + "\n" + str(machineStatus2) + "\n" + str(machineStatus3) + "\n" + str(machineStatus4) + "\n" + str(machineStatus5) + "]\n")
    f.write("MachineStatusVector = [" + str(machine_statuses[0]) + "\n" + str(machine_statuses[1]) + "\n" + str(machine_statuses[2]) + "\n" + str(machine_statuses[3]) + "\n" + str(machine_statuses[4]) + "]\n")
    for num in range(0,5):
        f.write("NextActionText" + str(num+1) + " = " + nextActionText[num] + "\n")
    f.write("MachineMaker1 = " + machine_makers[0] + "\n")
    f.write("MachineMaker2 = " + machine_makers[1] + "\n")
    f.write("MachineMaker3 = " + machine_makers[2] + "\n")
    f.write("MachineMaker4 = " + machine_makers[3] + "\n")
    f.write("MachineMaker5 = " + machine_makers[4] + "\n")
    f.write("MachineModel1 = " + machine_models[0] + "\n")
    f.write("MachineModel2 = " + machine_models[1] + "\n")
    f.write("MachineModel3 = " + machine_models[2] + "\n")
    f.write("MachineModel4 = " + machine_models[3] + "\n")
    f.write("MachineModel5 = " + machine_models[4] + "\n")
    f.write("PredictiveAlarmText1_1 = " + predictiveAlarmText1[0] + "\n")
    f.write("PredictiveAlarmText1_2 = " + predictiveAlarmText2[0] + "\n")
    f.write("PredictiveAlarmText1_3 = " + predictiveAlarmText3[0] + "\n")
    f.write("PredictiveAlarmText2_1 = " + predictiveAlarmText1[1] + "\n")
    f.write("PredictiveAlarmText2_2 = " + predictiveAlarmText2[1] + "\n")
    f.write("PredictiveAlarmText2_3 = " + predictiveAlarmText3[1] + "\n")
    f.write("PredictiveAlarmText3_1 = " + predictiveAlarmText1[2] + "\n")
    f.write("PredictiveAlarmText3_2 = " + predictiveAlarmText2[2] + "\n")
    f.write("PredictiveAlarmText3_3 = " + predictiveAlarmText3[2] + "\n")
    f.write("PredictiveAlarmText4_1 = " + predictiveAlarmText1[3] + "\n")
    f.write("PredictiveAlarmText4_2 = " + predictiveAlarmText2[3] + "\n")
    f.write("PredictiveAlarmText4_3 = " + predictiveAlarmText3[3] + "\n")
    f.write("PredictiveAlarmText5_1 = " + predictiveAlarmText1[4] + "\n")
    f.write("PredictiveAlarmText5_2 = " + predictiveAlarmText2[4] + "\n")
    f.write("PredictiveAlarmText5_3 = " + predictiveAlarmText3[4] + "\n")

#
# data.txt is used to populate the web interface
#
with open('/home/cameron/workspace/hackathon/models/domeModel/data.txt', 'w') as f:
    f.write("MachineIdVector1,MachineIdVector2,MachineIdVector3,MachineIdVector4,MachineIdVector5,AlarmText1,AlarmText2,AlarmText3,AlarmText4,AlarmText5,MachineStatusVector1,MachineStatusVector2,MachineStatusVector3,MachineStatusVector4,MachineStatusVector5,NextActionText1,NextActionText2,NextActionText3,NextActionText4,NextActionText5,MachineMaker1,MachineMaker2,MachineMaker3,MachineMaker4,MachineMaker5,MachineModel1,MachineModel2,MachineModel3,MachineModel4,MachineModel5,PredictiveAlarmText1_1,PredictiveAlarmText1_2,PredictiveAlarmText1_3,PredictiveAlarmText2_1,PredictiveAlarmText2_2,PredictiveAlarmText2_3,PredictiveAlarmText3_1,PredictiveAlarmText3_2,PredictiveAlarmText3_3,PredictiveAlarmText4_1,PredictiveAlarmText4_2,PredictiveAlarmText4_3,PredictiveAlarmText5_1,PredictiveAlarmText5_2,PredictiveAlarmText5_3\n")
    for num in range(0,5):
        f.write(str(machine_ids[num]))
        f.write(",")
    for num in range(0,5):
        f.write(machine_messages[num])
        f.write(",")
    for num in range(0,5):
        f.write(str(machine_statuses[num]))
        f.write(",")
    for num in range(0,5):
        f.write(machine_suggestions[num])
        f.write(",")
    for num in range(0,5):
        f.write(machine_makers[num])
        f.write(",")
    for num in range(0,5):
        f.write(machine_models[num])
        f.write(",")
    for num in range(0,5):
        f.write(predictiveAlarmText1[num])
        f.write(",")
        f.write(predictiveAlarmText2[num])
        f.write(",")
        f.write(predictiveAlarmText3[num])
        if num < 4:
            f.write(",")
