import json

import os
import traceback
import re
from psycopg2 import sql

def reset_sequence(cursor, table, column):
    # to restart sequence
    cursor.execute('SELECT column_default from information_schema.columns where table_name=%s and column_name=%s;',(table, column,))
    string = cursor.fetchone()[0]
    cursor.execute(
        sql.SQL('select max({column}) from {table}')
        .format(table=sql.Identifier(table), column=sql.Identifier(column)))
    result = cursor.fetchone()[0]
    if result != None:
        value=result+1
    else:
        value = 1

    match = re.search(r'"(.+?)"', string)
    if match:
        result = match.group(1)
        # print(result)
    cursor.execute(
        sql.SQL('ALTER SEQUENCE {} RESTART WITH %s')
        .format(sql.Identifier(result)), (value,))


#******FUNCTION FOR GUI******

def print_list(cursor, entity, id=0):
    if entity == "exam":
        exam_ids = []
        exam_names= []
        print("Exam List:-")
        cursor.execute('select "EID","Exam Name" from "Exam" order by "EID"')
        j = 1
        for i in cursor.fetchall():
            exam_ids.append((i[0]))
            exam_names.append(i[1])
            print(j, ". ", i[1].strip())
            j += 1
        return exam_ids, exam_names
    elif entity == "subject":
        subject_ids = []
        subject_names=[]
        print("Subject List:-")
        try:
            cursor.execute('select "SID","Subject Name" from "Subject" order by "SID"')
            j = 1
            for i in cursor.fetchall():
                # only display subject if not in portion_ids["subject"]
                subject_ids.append((i[0]))
                subject_names.append((i[1]))
                print(j, ". ", i[1].strip())
                j += 1
            return subject_ids, subject_names
        except Exception as e:
            print("No subjects")
            traceback.print_exc()

    elif entity == "module":
        module_ids = []
        module_names=[]
        print("Module List:-")
        try:
            cursor.execute(
                'select "MID","Module No","Module Name" from "Module" where "Subject ID" = %s order by "MID"', (id,))
            for i in cursor.fetchall():
                # only display module if not in portion_ids["module"]
                module_ids.append(i[0])
                module_names.append(f'Module {i[1]} - {i[2]}')
                print("Module ", i[1], " - ", i[2].strip())
            return module_ids, module_names
        except Exception as e:
            print("No modules")
            traceback.print_exc()

    elif entity == "topic":
        topic_ids = []
        topic_names=[]
        print("Topic List:-")
        try:
            cursor.execute('SELECT "TID","Topic Name" FROM "Topic" where "Module ID"=%s order by "TID"', (id,))
            j = 1
            for i in cursor.fetchall():
                # only display topic if not in portion_ids["topic"]
                topic_ids.append((i[0]))
                topic_names.append(i[1])
                print(j, ". ", i[1].strip())
                j += 1
            return topic_ids, topic_names
        except Exception as e:
            print("No topics")
            traceback.print_exc()

