import os

from Input import *
import json
import Task_Suggester as ts
from datetime import date, datetime


connection=None
cursor=None
cursor2=None
connected=False

def practice_test(cursor,topic_id):

    cursor.execute('select "QID", "Question","Duration" from "Question" where "Topic ID" = %s order by RANDOM()',(topic_id,))
    timer = 0
    questions_chosen=[]
    for i in cursor.fetchall():
        try:
            duration = i[2] / 60
            if timer + duration <= 25:
                timer += duration
                print("Q", j, ". ", i[1], "\n")
                questions_chosen.append(i[0])
            j = j + 1
        except:
            break


    while timer <= 25:#use read test duration
        i = cursor.fetchone()
        try:
                duration = i[1] / 60
                if timer + duration <=25:
                    timer += duration
                    print("Q", j, ". ", i[0], "\n")
                j = j + 1
        except:
            break

#***FUNCTION FOR GUI***

def get_next_question(cursor, exam_id):

    os.chdir('..\Text Files')
    if os.path.isfile('Learning Plans.json'):
        with open('Learning Plans.json', 'r') as f:
            learning_plans = json.load(f)

    testing_plan = learning_plans[str(exam_id)]["test"]
    today_date=date.today()

    for qid in testing_plan:
        cursor.execute('select "Question", "Last Reviewed Date", "Interval" from "Question" where "QID" = %s', (qid,))
        result = cursor.fetchone()
        if result[1] != None:
            last_reviewed_date = datetime.strptime(result[1], "%d-%m-%Y").date()
            if (today_date - last_reviewed_date).days >= result[2]:
                return qid, result[0].strip()
            else:
                continue
        else:
            return qid, result[0].strip()

    for qid in testing_plan:
        cursor.execute('select "Question", "Last Evaluation Response" from "Question" where "QID" = %s', (qid,))
        result = cursor.fetchone()
        if result[1] < 4:
            return qid, result[0].strip()
        else:
            continue


    for qid in testing_plan:
        cursor.execute('select "Question" from "Question" where "QID" = %s', (qid,))
        return qid, cursor.fetchone()[0].strip()




