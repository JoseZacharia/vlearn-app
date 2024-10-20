import datetime
import math
import os
import json


def updateAverage(old_average, new_score_diff, num_items):
    # print('Average Calculation')
    new_average = ((old_average * num_items) + new_score_diff) / (num_items + 1)
    # print(f'{new_average} = (({old_average} * {num_items}) + {new_score_diff}) / ({num_items} + 1)')
    return new_average


def predictScore(cursor = None, exam_id = None):
    # cur_average = Average Portion Score Difference per day from Exam db
    # num_items = current date - added date - 1
    # new_score_diff = latest portion score difference
    prof_list = []
    os.chdir('..\Text Files')
    if os.path.isfile('Progress Details.json'):
        with open('Progress Details.json', 'r') as f:
            progress_details = json.load(f)

        if str(exam_id) in progress_details:
            prof_list = progress_details[str(exam_id)]['Proficiency']

    # prof_list = [5, 0, 10, 0, 0, 8, 15, -3, 2]
    num_items = len(prof_list)

    if num_items == 0:
        return 0

    prof_diff_list = [prof_list[0]]
    for i in range(1, len(prof_list)):
        difference = prof_list[i] - prof_list[i - 1]
        prof_diff_list.append(difference)

    cur_average = sum(prof_diff_list)/num_items
    # print(f'avg = {cur_average}')

    # cur_average = 5
    # num_items = 7
    # new_score_diff = cur_average


    cursor.execute('select "Exam Date", "Portion Proficiency Percent" from "Exam" where "EID" = %s', (exam_id,))
    result = cursor.fetchone()
    # exam_date = result[0]
    #exam_date_str from Exam db
    # exam_date_str = '25-05-2023'
    exam_date = datetime.datetime.strptime(result[0], "%d-%m-%Y").date()
    current_date = datetime.date.today()
    # future_date = current_date - datetime.timedelta(days=x)
    # days_till_exam = current_date - exam_date - 1
    days_till_exam = (exam_date - current_date).days
    # print(f'days till exam = {days_till_exam}')

    current_proficiency_score_percent = result[1]



    predicted_score_percent = round(current_proficiency_score_percent + cur_average * days_till_exam, 2)

    print(f'predicted: {predicted_score_percent}')

    absolute_prediction = predicted_score_percent

    if predicted_score_percent > 100:
        predicted_score_percent = 100
    elif predicted_score_percent < 0:
        predicted_score_percent = 0


    cursor.execute('update "Exam" set "Predicted Score Percent" = %s where "EID" = %s', (predicted_score_percent, exam_id,))
    return absolute_prediction

    #
    # # current_proficiency_score_percent = Portion score percent from Exam db
    #
    # current_proficiency_score_percent = 5
    #
    #
    # # portion_complete_flag = 0
    # #
    # # target_score_percent = 50
    #
    # for i in range(0, days_till_exam):
    #
    #     # current_date = current_date + datetime.timedelta(days=1)
    #     # # print(current_date)
    #     # t = (exam_date - current_date).total_seconds() / 60
    #     # # print(t)
    #     # if t!=0:
    #     #     ebbinghaus_loss = (100 - (148 / (1.25 * math.log(t, 10) + 1.48))) / 100
    #     # else:
    #     #     ebbinghaus_loss = 0
    #     # # print(f'ebbinghaus loss = {ebbinghaus_loss}')
    #     #
    #     # # print(f'Latest portion score difference = {new_score_diff}')
    #     # new_score_diff = new_score_diff * (1 - ebbinghaus_loss)
    #     # # print(f'Latest portion score difference with ebb loss= {new_score_diff}')
    #
    #     cur_average = updateAverage(cur_average, new_score_diff, num_items)
    #     num_items=num_items+ 1
    #     # num_items=num_items+ 1
    #     # new_average = new_average*(1 - ebbinghaus_loss)
    #     # print(f'New Average = {cur_average}')
    #     new_score_diff = cur_average
    #
    #
    #
    #     current_proficiency_score_percent += cur_average
    #     # current_proficiency_score_percent = current_proficiency_score_percent * (1 - ebbinghaus_loss)
    #
    #     # if current_proficiency_score_percent == 100:
    #     #     if portion_complete_flag == 0:
    #     #         portion_complete_flag = 1
    #     #         print(f'Estimated Portion Complete Time : {i} days')
    #
    #     print(current_proficiency_score_percent)
    #     # if current_proficiency_score_percent >= target_score_percent:
    #     #     # current_proficiency_score_percent = 100
    #     #     if portion_complete_flag == 0:
    #     #         portion_complete_flag = 1
    #     #         print(f'Estimated Time to get to Target Score Percent : {round(i * (1 + ebbinghaus_loss))} days')
    #
    #     if current_proficiency_score_percent >= 100:
    #         current_proficiency_score_percent = 100
    #     elif current_proficiency_score_percent < 0:
    #         current_proficiency_score_percent = 0
    #
    #
    #     # print(f'{days_till_exam - i -1} days left, Portion Score = {current_proficiency_score_percent}')
    #
    # predicted_score_percent = round(current_proficiency_score_percent, 2)
    # print(f'Predicted Score = {predicted_score}')
    
    # x=target_score_percent
    # if x!=100:
    #     # x  = target score percent from exam db
    #     # x =  target percent
    #     pass
    # else:
    #     x = 99.99999999999999

    # y = 100
    # z = (y * y)/x
    # a = current_proficiency_score_percent

    # predicted_score_percent = round(x + (a - y) * (y - x) / (z - y),2)
    # if predicted_score_percent > 100:
    #     predicted_score_percent = 100

    # if predicted_score_percent < 0:
        # predicted_score_percent = 0
    #
    # print(f'Predicted Score Percent = {predicted_score_percent}')
    # return predicted_score_percent



if __name__ == "__main__":

    predictScore()





