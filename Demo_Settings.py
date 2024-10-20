from SQLConnect import connect, connect2
import random
import Input as ip
import Task_Suggester as ts
import Test_Generator as tg
import SuperMemo2 as sm2

from PySide6.QtWidgets import *

from pyuac import main_requires_admin
# import datetime
from datetime import *
import win32api
import random
from Reset_Database import reset_everything



cursor = None
def randomize_everything(cursor, exam_id):
    rand_num = random.randint(0,10)
    print("Random no  of session: ", rand_num)
    for i in range(rand_num):
        rand_num2 = random.randint(0,5)
        print("Random no:questions attempted: ", rand_num2)
        for j in range(rand_num2):
            qdata = tg.get_next_question(cursor, exam_id)
            if qdata != None:
                qid = qdata[0]
            else:
                break
            qp = random.uniform(0, 10)
            cursor.execute('update "Question" set "Question Proficiency" = %s where "QID" = %s', (qp, qid))
            q = random.randint(0,5)

            print(f'question: {qid}, proficiency: {qp}, response: {q}')
            sm2.calc_values(cursor, qid, q)
            ts.update_learning_plan(cursor, exam_id)
        cursor.execute('select "Learning Time Left" from "Exam" where "EID" = %s', (exam_id,))
        learning_time_left = cursor.fetchone()[0] - random.randint(0, 25)
        print("Learning Time Left after Random interval: ", learning_time_left)
        cursor.execute('update "Exam" set "Learning Time Left" = %s where "EID" = %s', (learning_time_left, exam_id))

        ts.update_pomo_details(cursor, exam_id)

class RandomizeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.exam_ids, exam_names = ip.print_list(cursor, "exam")
        print(f'returned exam ids = {self.exam_ids} and returned names = {exam_names}')
        exam_list = QComboBox()
        exam_list.addItems(exam_names)
        exam_list.currentIndexChanged.connect(self.selectionChange)
        self.selected_exam_id = self.exam_ids[0]

        layout.addWidget(exam_list)

        # Create the spinbox with label
        days_layout = QHBoxLayout()
        layout.addLayout(days_layout)
        days_label = QLabel("No. of Days:")
        self.days_spinbox = QSpinBox()
        self.days_spinbox.setMinimum(1)
        days_layout.addWidget(days_label)
        days_layout.addWidget(self.days_spinbox)

        # Create the randomize button
        randomize_button = QPushButton("Randomize")
        randomize_button.clicked.connect(self.randomize)
        layout.addWidget(randomize_button)


    def selectionChange(self, i):
        self.selected_exam_id=self.exam_ids[i]
        print("selected exam id: ",self.selected_exam_id)
    def randomize(self):
        # Retrieve selected exam and number of days
        no_of_days = self.days_spinbox.value()
        print(self.selected_exam_id, no_of_days)
        cursor.execute('select "Added Date", "Exam Date" from "Exam" where "EID" = %s', (self.selected_exam_id,))
        result = cursor.fetchone()
        added_date = datetime.strptime(result[0], "%d-%m-%Y").date()
        exam_date = datetime.strptime(result[1], "%d-%m-%Y").date()
        ts.update_learning_plan(cursor, self.selected_exam_id)

        for i in range(0, no_of_days):
            new_date = added_date + timedelta(days=i)
            if new_date == exam_date:
                break
            day = new_date.day
            month = new_date.month
            year = new_date.year
            change_date(day, month, year)
            print(f"CURRENT DATE = {date.today()}")

            randomize_everything(cursor, self.selected_exam_id)
        print("------------------RANDOMIZATION COMPLETE-------------------")



def change_date(day, month, year):
    tt = datetime.utcnow().time()
    win32api.SetSystemTime(year, month, 0, day,
    tt.hour, tt.minute, tt.second, tt.microsecond//1000)

@main_requires_admin
def main():
    # change_date(18, 5, 2023)
    actual_date = date.today()
    global cursor
    connection, cursor = connect()
    reset_everything(cursor)
    app = QApplication([])
    widget = RandomizeWidget()
    widget.show()
    app.exec()
    day = actual_date.day
    month = actual_date.month
    year = actual_date.year
    change_date(day, month, year)
    # print(current_date)

if __name__ == "__main__":
    main()



