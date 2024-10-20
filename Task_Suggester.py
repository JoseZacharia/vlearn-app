
import Test_Generator as tg
import os
import json
import traceback
from datetime import *
import math
import Score_Percent_Predictor as sp
# import Input as ip

connection=None
cursor=None
cursor2=None

# ***FUNCTION FOR GUI***
def next_study_session_portion(cursor, exam_id):
    os.chdir('..\Text Files')
    if os.path.isfile('Learning Plans.json'):
        with open('Learning Plans.json', 'r') as f:
            learning_plans=json.load(f)

    # print("learning plans: ", learning_plans)
    study_plan=learning_plans[str(exam_id)]["study"]
    # print("Study Plan: ",study_plan)

    timer = 0
    study_session_plan=''
    for topic_id, time in list(study_plan.items()):
        # print("Current Timer: ",timer)
        if timer >= 25:
            break
        cursor.execute('select "Topic Name" from "Topic" where "TID"=%s', (topic_id,))
        topic_name=cursor.fetchone()[0]
        time_required=study_plan[str(topic_id)]
        if time_required >=5 and time_required < 25 - timer:
            timer+=time_required
            remainder=25-timer
            if remainder >= 5:
                session_plan=f'Study {topic_name.strip()} for {round(time_required)} minutes'
                # print(f'Study {topic_name.strip()} for {round(time_required)} minutes')
                # print(session_plan)
                study_session_plan=study_session_plan + '\n' + session_plan + '\n'
                time_studied=time_required
            else:
                # print(f'Study {topic_name.strip()} for {round(time_required+remainder)} minutes')
                session_plan=f'Study {topic_name.strip()} for {round(time_required+remainder)} minutes'
                # print(session_plan)
                study_session_plan = study_session_plan + '\n' + session_plan + '\n'
                time_studied=time_required+remainder
            del study_plan[str(topic_id)]
        else:
            remainder=25-timer
            if remainder >= 5:
                timer=25
                # print(f'Study {topic_name.strip()} for {round(remainder)} minutes')
                session_plan = f'Study \"{topic_name.strip()}\" for {round(remainder)} minutes'
                # print(session_plan)
                study_session_plan = study_session_plan + '\n' + session_plan + '\n'
                time_required-=remainder

    return study_session_plan


# ***FUNCTION FOR GUI***
def get_next_session(cursor, exam_id):
    cursor.execute('select "Study Test Ratio" from "Exam" where "EID" = %s', (exam_id,))
    xy = cursor.fetchone()[0]
    study_session_no = int(xy.split(":")[0])
    test_session_no = int(xy.split(":")[1])
    session_cycle_length = study_session_no + test_session_no
    cursor.execute('select "Current Session No" from "Exam" where "EID" = %s', (exam_id,))
    current_session_no = cursor.fetchone()[0]
    if current_session_no <= study_session_no:
        next_session='study'

    else:
        next_session = 'test'

    if current_session_no + 1 > session_cycle_length:
        current_session_no = 1
    else:
        current_session_no += 1

    # EXECUTE WHEN CURRENT SESSION FINISHES
    cursor.execute('update "Exam" set "Current Session No" = %s where "EID"=%s', (current_session_no, exam_id))

    return next_session

def calc_scores(cursor, entity): #called when content is added
    if entity == "module":
        calc_scores(cursor, "topic")
        cursor.execute('select "MID" from "Module"')
        for i in cursor.fetchall():
            module_id=i[0]
            ms=[]
            cursor.execute('select "Topic Score" from "Topic" where "Module ID" = %s',(module_id,))
            for j in cursor.fetchall():
                ms.append(j[0])
            ms=sum(ms)/len(ms)
            # print(f'module score: {ms}')
            cursor.execute('update "Module" set "Module Score"=%s where "MID"=%s', (ms, module_id))
        pass

    elif entity == "topic":
        calc_scores(cursor, "question")
        cursor.execute('select "TID", "Topic Weightage", "Topic Difficulty" from "Topic"')
        for i in cursor.fetchall():
            ts=i[1]/i[2]
            # print(f'Topic Score: {ts}')
            cursor.execute('update "Topic" set "Topic Score"=%s where "TID"=%s', (ts, i[0]))

    elif entity == "question":
        cursor.execute(
                'select "QID","Topic Weightage","Topic Difficulty", '
                '"Norm Duration", "Question Proficiency" from "Question" join "Topic" on "Question"."Topic ID"="Topic"."TID" ')
        for i in cursor.fetchall():
            qs = (3 * i[1]) / (i[2] + i[3] + i[4])
            # print(f'Question Score = {qs}')
            cursor.execute('update "Question" set "Question Score"=%s where "QID"=%s', (qs, i[0]))

def weighted_average_m1(distribution, weights):
    numerator = sum([distribution[i] * weights[i] for i in range(len(distribution))])
    denominator = sum(weights)
    # print(f'weighted average = {numerator}/{denominator}')
    return (numerator/denominator)


#uses difficulty to calculate proficiency instead of score
def calc_proficiencies(cursor, entity, exam_id = None):  # called after each test has been evaluated
    if entity == 'portion':
        calc_proficiencies(cursor, 'subject')
        os.chdir('..\Text Files')
        with open('Exam Portions.json', 'r') as f:
            exam_portions = json.load(f)
            # print(exam_portions)
        q_prof_list = []
        weights_list = []
        portion_ids = exam_portions[str(exam_id)]
        portion_tids = portion_ids['topics']
        # print(f'portion tids = {portion_tids}')
        for tid in portion_tids:
            # print(f'tid = {tid}')
            cursor.execute(
                'select "QID","Topic Weightage","Topic Difficulty", '
                '"Norm Duration", "Question Proficiency" from "Question" join "Topic" on "Question"."Topic ID"="Topic"."TID" where "TID" = %s',
                (tid,))

            for i in cursor.fetchall():
                weight = (2 * i[1]) / (i[2] + i[3]) * 10
                q_prof_list.append(i[4])
                weights_list.append(weight)

        portion_proficiency_percent = weighted_average_m1(q_prof_list, weights_list) * 10

        print(f'portion proficiency percent = {portion_proficiency_percent}')
        cursor.execute('Update "Exam" set "Portion Proficiency Percent" = %s where "EID" = %s', (portion_proficiency_percent, exam_id))

    if entity == "subject":
        calc_proficiencies(cursor, "module")
        cursor.execute('select "SID" from "Subject"')
        for i in cursor.fetchall():
            subject_id = i[0]
            module_proficiencies = []
            module_difficulties = []

            #CALCULATE MODULE DIFFICULTY AS AVERAGE TOPIC DIFFICULTY
            cursor.execute('select "Module Proficiency", "Module Difficulty" from "Module" where "Subject ID"=%s',
                           (subject_id,))
            for j in cursor.fetchall():
                module_proficiencies.append(j[0])
                module_difficulties.append(j[1])
            sp = weighted_average_m1(module_proficiencies, module_difficulties)
            cursor.execute('update "Subject" set "Subject Proficiency" = %s where "SID" = %s', (sp, subject_id,))

        pass
    elif entity == "module":
        calc_proficiencies(cursor, "topic")
        cursor.execute('select "MID" from "Module"')
        for i in cursor.fetchall():
            module_id = i[0]
            topic_proficiencies = []
            topic_difficulties = []
            cursor.execute('select "Topic Proficiency", "Topic Difficulty" from "Topic" where "Module ID"=%s', (module_id,))
            for j in cursor.fetchall():
                topic_proficiencies.append(j[0])
                topic_difficulties.append(j[1])
            mp = weighted_average_m1(topic_proficiencies, topic_difficulties)
            cursor.execute('update "Module" set "Module Proficiency" = %s where "MID" = %s', (mp, module_id,))

        pass
    elif entity == "topic":
        cursor.execute('select "TID" from "Topic"')
        for i in cursor.fetchall():
            question_proficiencies = []
            question_norm_durations = []
            topic_id = i[0]
            cursor.execute('select "Question Proficiency", "Norm Duration" from "Question" where "Topic ID"=%s',
                           (topic_id,))
            for j in cursor.fetchall():
                question_proficiencies.append(j[0])
                question_norm_durations.append(j[1])
            tp = weighted_average_m1(question_proficiencies, question_norm_durations)

            cursor.execute('update "Topic" set "Topic Proficiency" = %s where "TID" = %s', (tp, topic_id,))


def proportion(cursor,entity,portion_ids, total_duration, target_proficiency):
    portionwise_duration_split = {}
    portion_proportion_metric = {}

    if entity == "module":
        query = """
            select "Module Proficiency" from "Module" where "MID" =%s
            """
    elif entity == "topic":
        query = """
            select "Topic Score", "Topic Proficiency" from "Topic" where "TID" =%s
            """

    # print(f'portion ids: {portion_ids}')
    if len(portion_ids) > 1:
        for i in portion_ids:
            # print(f'Query: {query}')
            cursor.execute(query, (i,))
            result = cursor.fetchone()
            # print(result)
            if entity == "topic":
                portion_proportion_metric[i] = (result[0]+result[1]*2)/3
            elif entity == "module":
                portion_proportion_metric[i] = result[0] # because all modules have equal weightage
            # print(f'{entity} {i} score proficiency function result = {portion_score_proficiencies_products[i]}')
            # print("Score Proficiency Product: ",portion_score_proficiencies_products[i])

        # print(f'{entity} proportion metric : {portion_proportion_metric}')

        M = target_proficiency
        portion_gaps={}
        for i in portion_ids:
            portion_gaps[i] = abs((portion_proportion_metric[i]) - M)

        S=sum(portion_gaps.values())
        # print("Sum: ",S )
        # print("Max: ", M)

        for i in portion_ids:
            portionwise_duration_split[i] = (portion_gaps[i]/ S) * total_duration


    elif len(portion_ids) == 1:
        for i in portion_ids:
            portionwise_duration_split[i]=total_duration

    # print("Portionwise Duration Split:", portionwise_duration_split)
    return portionwise_duration_split


def sort_dictionary(unsorted_dict, desc=True):
    sorted_dict = sorted(unsorted_dict.items(), key=lambda x: x[1], reverse=desc)
    converted_dict = dict(sorted_dict)
    return converted_dict


def update_learning_plan(cursor,exam_id):
    calc_proficiencies(cursor, "portion", exam_id = exam_id)
    calc_scores(cursor, "module")
    update_proficiency_details(cursor, exam_id)
    cursor.execute(
        'select "Target Score Percent", "Learning Time Left", "Total Learning Time", "Exam Date", "Study Test Ratio" from "Exam" where "EID" = %s',
        (exam_id,))
    result = cursor.fetchone()
    target_percent = result[0]
    # target_percent = 50
    learning_time_left = result[1]
    total_learning_time = result[2]
    # print(f'original learning time left = {total_learning_time}')


    predicted_percent = sp.predictScore(cursor, exam_id)

    if learning_time_left <= 0:
        diff = (target_percent - predicted_percent) / 100
        learning_time_left = total_learning_time * (1+diff)

    exam_date = result[3]
    exam_date_formatted = datetime.strptime(exam_date, "%d-%m-%Y")
    time_left_till_deadline = (exam_date_formatted - datetime.now()).total_seconds() / 60  # minutes till deadline
    # print(f'minutes till deadline = {time_left_till_deadline}')

    if learning_time_left > time_left_till_deadline:
        learning_time_left = time_left_till_deadline

    print(f'new learning time left = {learning_time_left}')

    xy=result[4]
    x=int(xy.split(":")[0])
    y=int(xy.split(":")[1])
    total_studying_time=learning_time_left*(x/(x+y))

    os.chdir('..\Text Files')
    with open('Exam Portions.json', 'r') as f:
        exam_portions = json.load(f)
    # print(exam_portions)

    portion_ids=exam_portions[str(exam_id)]
    # print(portion_ids)


    #Study Plan Generation
    modulewise_duration_split={}
    topicwise_duration_split={}
    topicwise_duration_split_per_module={}
    cursor.execute('select "Target Score Percent" from "Exam" where "EID" = %s', (exam_id,))
    target_proficiency=cursor.fetchone()[0]/10

    if len(portion_ids["modules"])>0:
        modulewise_duration_split=proportion(cursor,"module", portion_ids["modules"], total_studying_time, target_proficiency)
        modulewise_duration_split=sort_dictionary(modulewise_duration_split, desc=True)
        print("Modulewise Duration Split: ",modulewise_duration_split)
        for i in portion_ids["modules"]:
            topic_ids=[]
            cursor.execute('select "TID" from "Topic" where "Module ID" = %s',(i,))
            for j in cursor.fetchall():
                if j[0] in portion_ids['topics']:
                    topic_ids.append(j[0])
            topicwise_duration_split_per_module=proportion(cursor, "topic", topic_ids,modulewise_duration_split[i], target_proficiency)

            for k in topicwise_duration_split_per_module:
                topicwise_duration_split[k]=topicwise_duration_split_per_module[k]

    topicwise_duration_split=sort_dictionary(topicwise_duration_split, desc=True)


    testing_plan = []
    print(f'Topicwise Duration Split: ', topicwise_duration_split)


    for i in topicwise_duration_split:
        if topicwise_duration_split[i] > 0:
            if i in portion_ids['topics']:
                qids = []
                durations = []
                question_scores = []
                cursor.execute('select "QID","Duration", "Question Score" from "Question" where "Topic ID" = %s', (i,))
                for result in cursor.fetchall():
                    qids.append(result[0])
                    durations.append((result[1]))
                    question_scores.append(result[2])
                # print(qids, durations, question_scores)
                selected_qids = knapsack_dp(durations, question_scores, round((topicwise_duration_split[i] * 60)*(y/x)), len(durations),  qids)
                testing_plan.extend(selected_qids)


    # print(f'Study Plan: {topicwise_duration_split}')
    print(f'Testing Plan: {testing_plan}')

    study_test_plans={"study":topicwise_duration_split, "test":testing_plan}


    learning_plans={}
    if os.path.isfile('Learning Plans.json'):
        with open('Learning Plans.json', 'r') as f:
            learning_plans=json.load(f)

    learning_plans[str(exam_id)]=study_test_plans
    with open('Learning Plans.json', 'w') as f:
        json.dump(learning_plans, f)

    #store testing plan in Testing Plan JSON file as exam_testing_plan[exam_id]


def update_proficiency_details(cursor, exam_id):
    cursor.execute('select "Portion Proficiency Percent", "Added Date" from "Exam" where "EID" = %s', (exam_id,))
    result = cursor.fetchone()
    proficiency = result[0]
    progress_details = {}
    os.chdir('..\Text Files')
    if os.path.isfile('Progress Details.json'):
        with open('Progress Details.json', 'r') as f:
            progress_details = json.load(f)

    if str(exam_id) not in progress_details:
        progress_details[str(exam_id)] = {'Proficiency': [], "Pomodoro": []}

    added_date = datetime.strptime(result[1], "%d-%m-%Y").date()

    today = date.today()
    days_difference = (today - added_date).days
    portion_prof_details_length = len(progress_details[str(exam_id)]['Proficiency'])
    if portion_prof_details_length <= days_difference:
        if len(progress_details[str(exam_id)]['Proficiency']) > 0:
            last_recorded_proficiency = progress_details[str(exam_id)]['Proficiency'][-1]
        else:
            last_recorded_proficiency = 0
        for i in range(days_difference - portion_prof_details_length):
            progress_details[str(exam_id)]['Proficiency'].append(last_recorded_proficiency)
        progress_details[str(exam_id)]['Proficiency'].append(proficiency)

    else:
        progress_details[str(exam_id)]['Proficiency'][-1] = proficiency

    print('Progress Details (Proficiency): ', progress_details[str(exam_id)]['Proficiency'])

    with open('Progress Details.json', 'w') as f:
        json.dump(progress_details, f)


def knapsack_dp(W, V, M, n, qids):
    # timer = 0
    selected_qids=[]
    B = [[0 for j in range(M + 1)] for i in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(M + 1):
            B[i][j] = B[i - 1][j]

            if j >= W[i - 1]:
                B[i][j] = max(B[i - 1][j], B[i - 1][j - W[i - 1]] + V[i - 1])

    while n != 0:
        if B[n][M] != B[n - 1][M]:
            # print("\tQuestion", qids[n-1], "with Duration =", W[n - 1], "and Question Score =", V[n - 1])
            selected_qids.append(qids[n-1])
            # timer += W[n - 1]
            M = M - W[n - 1]

        n -= 1
    return selected_qids


def main(cursor, exam_id):
    study_plans = {}
    os.chdir('..\Text Files')
    
    if os.path.isfile('Learning Plans.json'):
        with open('Learning Plans.json', 'r') as f:
            learning_plans = json.load(f)
    plan_exists_flag = False
    if str(exam_id) in study_plans.keys():
        if len(learning_plans[str(exam_id)]["study"]) > 0:
            plan_exists_flag = True

    try:
        if plan_exists_flag ==False:
            update_learning_plan(cursor, exam_id)
            print("Learning Plan Generated")
            cursor.execute('select "Learning Time Left", "Exam Date" from "Exam" where "EID" = %s', (exam_id,))
            i=cursor.fetchone()
            exam_date_formatted = datetime.strptime(i[1], "%d-%m-%Y")
            no_of_days_till_deadline = math.floor((exam_date_formatted - datetime.now()).total_seconds()/(60*60*24))
            no_of_pomodoro_sessions = i[0]/25
            no_of_pomodoro_session_per_day=math.ceil(no_of_pomodoro_sessions/no_of_days_till_deadline)
            print(f'Recommended Pomodoro Learning Sessions per day is {no_of_pomodoro_session_per_day}')

            plan_exists_flag = True

        return plan_exists_flag

    except Exception as e:
        # print(e)
        traceback.print_exc()


def update_pomo_details(cursor, exam_id):
    progress_details = {}
    os.chdir('..\Text Files')
    if os.path.isfile('Progress Details.json'):
        with open('Progress Details.json', 'r') as f:
            progress_details = json.load(f)

    if str(exam_id) not in progress_details:
        progress_details[str(exam_id)] = {'Proficiency': [], "Pomodoro": []}

    cursor.execute('select "Added Date" from "Exam" where "EID" = %s', (exam_id,))

    added_date = datetime.strptime(cursor.fetchone()[0], "%d-%m-%Y").date()
    today = date.today()
    days_difference = (today - added_date).days
    pomo_details_length = len(progress_details[str(exam_id)]['Pomodoro'])
    # print(f'days_difference = {days_difference}, pomo length = {pomo_details_length}')
    if pomo_details_length <= days_difference:
        for i in range(days_difference - pomo_details_length):
            progress_details[str(exam_id)]['Pomodoro'].append(0)
            # print(progress_details[str(exam_id)]['Pomodoro'])
        progress_details[str(exam_id)]['Pomodoro'].append(1)

    else:
        progress_details[str(exam_id)]['Pomodoro'][-1] += 1

    print("Progress Details (Pomo): ", progress_details[str(exam_id)]['Pomodoro'])

    with open('Progress Details.json', 'w') as f:
        json.dump(progress_details, f)

if __name__ == "__main__":
    main()