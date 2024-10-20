
from SQLConnect import connect, connect2
import Input as ip
def randomize_proficiencies(cursor):
    cursor.execute('select "QID" from "Question"')
    for i in cursor.fetchall():
        rand_num = 0
        cursor.execute('update "Question" set "Question Proficiency" = %s where "QID" = %s', (rand_num, i[0]))


def main():
    connection, cursor=connect()
    ip.reset_sequence(cursor, "Exam", "EID")
    # cursor.execute('select "Exam Name" where "Target Score Percent" - "Predicted Score Percent"  max("Target Score Percent" - "Predicted Score Percent")  from "Exam"')
    # print(cursor.fetchall())




if __name__ == "__main__":
        main()
        pass

