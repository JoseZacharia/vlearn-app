
from datetime import date, datetime

def calc_values(cursor, qid, q):

    # GET current N=REPETITION NO, EF AND I FROM QUESTION DB USING QID`
    cursor.execute('select "Repetition No", "Ease Factor", "Interval" from "Question" where "QID" = %s', (qid,))
    result = cursor.fetchone()
    n = result[0]
    EF = result[1]
    I = result[2]

    if q >= 3:
        if n == 0:
            I = 1
        elif n == 1:
            I = 6
        else:
            I = round(I * EF)
        n += 1
    else:
        n = 0
        I = 1
    
    EF = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if EF < 1.3:
        EF = 1.3

    last_reviewed_date = datetime.strftime(date.today(), "%d-%m-%Y")
    cursor.execute('update "Question" set "Ease Factor" = %s, "Interval" = %s, "Last Reviewed Date" = %s, "Repetition No" = %s, "Last Evaluation Response" = %s where "QID" = %s',
        (EF, I, last_reviewed_date, n, q, qid))

