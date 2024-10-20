import sys
import os
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import numpy as np
from datetime import *
import math
import json

import Input as ip
from SQLConnect import connect
import Task_Suggester as ts
import Test_Generator as tg
import Question_Generator as qg
import Answer_Checker as ac
import SuperMemo2 as sm2
import matplotlib.pyplot as plt

from PyPDF2 import PdfReader

current_window_geometry=QRect(750,350,400,300)
window_width = 400
window_height = 300

connection=''
cursor=''
current_exam_id = 0

rest_duration = QTime(0, 0, 5)
original_rest_duration = QTime(0, 0, 5)
doubled_rest_duration = QTime(0,0,10)
starting_time_left = None

session_active = True
test_active = False

test_duration = QTime(0, 25, 0)
current_time_left = test_duration
current_qa_screen = None

test_timer = None


class AddContentScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.parent = parent
        self.setParent(None)
        self.parent.hide()
        self.setWindowTitle("Add Content")
        Geometry(self)
        back_button = QPushButton('Main Menu')
        back_button.clicked.connect(self.back_button_clicked)

        add_subject_btn = QPushButton("Add Subject")
        add_subject_btn.clicked.connect(self.add_subject_btn_clicked)
        add_topic_btn = QPushButton("Add Topic")
        add_topic_btn.clicked.connect(self.add_topic_btn_clicked)
        add_material_btn = QPushButton("Add Material")
        add_material_btn.clicked.connect(self.add_material_btn_clicked)

        layout = QVBoxLayout()
        layout.addWidget(add_subject_btn)
        layout.addWidget(add_topic_btn)
        layout.addWidget(add_material_btn)
        layout.addWidget(back_button, alignment=Qt.AlignLeft)

        self.setLayout(layout)

    def add_subject_btn_clicked(self):
        self.addSubjectScreen = addSubjectScreen(self)
        self.addSubjectScreen.show()

    def add_topic_btn_clicked(self):
        self.addTopicScreen = addTopicScreen(self)
        self.addTopicScreen.show()

    def add_material_btn_clicked(self):
        self.browse_file_screen = FileBrowse(self)
        self.browse_file_screen.show()

    def back_button_clicked(self):
        self.close()
        self.parent.show()


class addSubjectScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__()

        self.parent = parent
        self.setParent(None)
        self.parent.hide()

        Geometry(self)
        self.setWindowTitle("Add Subject")

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.back_button_clicked)

        subject_layout = QGridLayout()
        subject_name_label = QLabel("Subject Name:")
        self.subject_name_edit = QLineEdit()
        subject_layout.addWidget(subject_name_label, 0, 0)
        subject_layout.addWidget(self.subject_name_edit, 0, 1)

        modules_layout = QHBoxLayout()
        modules_label = QLabel("Number of Modules:")
        self.modules_edit = QLineEdit()

        add_module_btn = QPushButton("Add Module")
        add_module_btn.clicked.connect(self.add_module)


        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submit_input)
        self.submit_btn.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_module_btn)
        # button_layout.addWidget(add_material_btn)
        button_layout.addWidget(self.submit_btn)

        # create a layout for the labels and line edits
        self.layout = QVBoxLayout()
        # input_layout.addWidget(subject_name_label, 0,0)
        # input_layout.addWidget(self.subject_name_edit,0,1)
        # input_layout.addWidget(modules_label,1,0)
        # input_layout.addWidget(self.modules_edit,1,1)

        # self.layout.addWidget(back_button)
        self.layout.addLayout(subject_layout)
        # layout.addLayout(modules_layout)
        self.layout.addLayout(button_layout)
        self.layout.addWidget(back_button, alignment=Qt.AlignLeft)

        # create a layout for the buttons
        # btn_layout = QVBoxLayout()
        # # btn_layout.addWidget(add_topic_btn)
        # # btn_layout.addStretch()
        # btn_layout.addWidget(submit_btn)

        # # create a main layout and add the input and button layouts to it
        # main_layout = QVBoxLayout()
        # main_layout.addLayout(input_layout)
        # main_layout.addLayout(btn_layout)

        # set the main layout for the widget
        self.setLayout(self.layout)

    def add_module(self):

        self.submit_btn.setEnabled(True)
        # Create layout for new module inputs
        module_layout = QHBoxLayout()

        # Create widgets for module number and module name inputs
        # module_no_input = QLineEdit()
        # module_no_input.setPlaceholderText('Module No')
        module_spinbox = QSpinBox()
        module_spinbox.setRange(0, 9999)
        module_spinbox.setSpecialValueText('Module No')
        # subject_layout.addWidget(self.module_spinbox, 1, 1)
        module_name_input = QLineEdit()
        module_name_input.setPlaceholderText('Module Name')

        # Add widgets to module layout
        module_layout.addWidget(module_spinbox)
        module_layout.addWidget(module_name_input)

        # Add module layout to modules layout
        self.layout.addLayout(module_layout)

    def add_topic_clicked(self):
        self.add_topic_screen = addTopicScreen()
        self.add_topic_screen.show()
        self.close()
        self.parent.show()

    def get_module_inputs(self):
        module_inputs = []
        for i in range(2, self.layout.count()):
            module_layout = self.layout.itemAt(i).layout()
            if module_layout is not None:
                module_no_input = module_layout.itemAt(0).widget()
                module_name_input = module_layout.itemAt(1).widget()
                module_inputs.append((module_no_input.value(), module_name_input.text()))
        return module_inputs

    def submit_input(self):

        # num_modules = self.modules_edit.text()
        # num_modules = self.module_spinbox.value()
        # print(f"Subject Name: {subject_name}\nNumber of Modules: {num_modules}")

        # SEARCH IF SUBJECT EXISTS IN SUBJECT DB
        subject_name = self.subject_name_edit.text()
        cursor.execute('select count(*) from "Subject" where "Subject Name" like %s', (subject_name,))
        if cursor.fetchone()[0] != 0:
            self.msg = QMessageBox()
            self.msg.setText("Subject already exists! Try again.")
            self.msg.show()
            self.msg.setStandardButtons(QMessageBox.Ok)

        else:
            module_inputs = self.get_module_inputs()
            print(module_inputs)


        # insert subject name into subject db
        # UNCOMMENT
            cursor.execute('insert into "Subject" ("Subject Name") values (%s) ', (subject_name,))
            # get sid of newly inserted subject
            cursor.execute('select "SID" from "Subject" where "Subject Name" = %s', (subject_name,))
            # insert module no and module name into module db using sid
            sid = cursor.fetchone()[0]
            for i in module_inputs:
                cursor.execute('insert into "Module" ("Subject ID", "Module No", "Module Name") values (%s, %s, %s)',
                               (sid, i[0], i[1]))

            msg_box = QMessageBox()
            msg_box.setWindowTitle("Information")
            msg_box.setText("Subject and Modules added")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

            self.close()
            self.parent.show()

    def back_button_clicked(self):
        self.close()
        self.parent.show()


class addTopicScreen(QWidget):
    # min_time = 0
    # max_time = 0
    def __init__(self, parent = None):
        super().__init__()
        Geometry(self)
        self.setWindowTitle("Add Topic")

        self.parent = parent
        self.setParent(None)
        self.parent.hide()
        self.study_time_flag = 0


        back_button = QPushButton('Back')
        back_button.clicked.connect(self.back_button_clicked)

        # create dropdown menus to select subject and module no
        self.subject_ids, self.subject_names = ip.print_list(cursor, "subject")
        # print(f'returned subject ids = {self.subject_ids} and returned names = {self.subject_names}')
        subject_label = QLabel("Subject:")
        self.subject_list = QComboBox()
        self.subject_list.addItems(self.subject_names)
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(subject_label)
        subject_layout.addWidget(self.subject_list)
        self.subject_list.currentIndexChanged.connect(self.subjectSelectionChange)
        self.selected_subject_id = self.subject_ids[0]

        self.module_ids, self.module_names = ip.print_list(cursor, "module", self.selected_subject_id)
        # print(f'returned module ids = {self.module_ids} and returned names = {self.module_names}')
        module_label = QLabel("Module:")
        self.module_list = QComboBox()
        self.module_list.addItems(self.module_names)
        module_layout = QHBoxLayout()
        module_layout.addWidget(module_label)
        module_layout.addWidget(self.module_list)
        self.module_list.currentIndexChanged.connect(self.moduleSelectionChange)
        self.selected_module_id = self.module_ids[0]

        # create a field to input topic name
        topic_label = QLabel("Topic Name:")
        self.topic_edit = QLineEdit()
        topic_layout = QHBoxLayout()
        topic_layout.addWidget(topic_label)
        topic_layout.addWidget(self.topic_edit)

        # create a slider to select difficulty and weightage
        difficulty_label = QLabel("Difficulty:")
        self.difficulty_slider = QSlider(Qt.Horizontal)
        self.difficulty_slider.setMinimum(0)
        self.difficulty_slider.setMaximum(100)
        self.difficulty_value = QLabel('0.0')
        self.difficulty_slider.valueChanged.connect(
            lambda: self.difficulty_value.setText(str(float(self.difficulty_slider.value()) / 10)))
        slider_layout = QGridLayout()
        slider_layout.addWidget(difficulty_label, 0, 0)
        slider_layout.addWidget(self.difficulty_slider, 0, 1)
        slider_layout.addWidget(self.difficulty_value, 0, 2)

        weightage_label = QLabel("Weightage:")
        self.weightage_slider = QSlider(Qt.Horizontal)
        self.weightage_slider.setMinimum(0)
        self.weightage_slider.setMaximum(100)
        self.weightage_value = QLabel('0.0')
        self.weightage_slider.valueChanged.connect(
            lambda: self.weightage_value.setText(str(float(self.weightage_slider.value()) / 10)))
        # slider_layout=QHBoxLayout()
        slider_layout.addWidget(weightage_label, 1, 0)
        slider_layout.addWidget(self.weightage_slider, 1, 1)
        slider_layout.addWidget(self.weightage_value, 1, 2)

        # create a grid layout for the input elements
        # input_layout = QGridLayout()
        # input_layout.addWidget(subject_label, 0, 0)
        # input_layout.addWidget(self.subject_combo, 0, 1)
        # input_layout.addWidget(module_label, 1, 0)
        # input_layout.addWidget(self.module_combo, 1, 1)
        # input_layout.addWidget(topic_label, 2, 0)
        # input_layout.addWidget(self.topic_edit, 2, 1)
        # input_layout.addWidget(difficulty_label, 3, 0)
        # input_layout.addWidget(self.difficulty_slider, 3, 1)
        # input_layout.addWidget(self.difficulty_value, 3, 2)
        # input_layout.addWidget(weightage_label, 4, 0)
        # input_layout.addWidget(self.weightage_slider, 4, 1)
        # input_layout.addWidget(self.weightage_value, 4, 2)

        layout = QVBoxLayout()
        layout.addLayout(subject_layout)
        layout.addLayout(module_layout)
        layout.addLayout(topic_layout)
        layout.addLayout(slider_layout)
        # layout.addLayout(weightage_layout)

        # create a button to add a topic and reset the input fields
        add_topic_btn = QPushButton("Add Topic")
        add_topic_btn.clicked.connect(self.add_topic)
        # finish_btn = QPushButton("Finish")
        # finish_btn.clicked.connect(self.finish_btn_clicked)

        # create a layout for the button
        # btn_layout = QHBoxLayout()
        # btn_layout.addWidget(add_topic_btn)
        # btn_layout.addWidget(finish_btn)

        # create a label to display added topics and a list to store the added topics
        self.topics_label = QLabel("Added Topics:")
        self.topics_list = []

        # create a layout for the label and list
        topics_layout = QVBoxLayout()
        topics_layout.addWidget(self.topics_label)
        topics_layout.addStretch()

        # create a main layout and add the input, button, and topics layouts to it
        # main_layout = QVBoxLayout()
        # main_layout.addLayout(input_layout)
        # main_layout.addLayout(btn_layout)
        # main_layout.addLayout(topics_layout)

        # layout.addLayout(btn_layout)
        layout.addWidget(add_topic_btn)
        layout.addWidget(back_button, alignment=Qt.AlignLeft)
        layout.addLayout(topics_layout)

        # set the main layout for the widget
        self.setLayout(layout)

    def subjectSelectionChange(self, i):
        self.selected_subject_id = self.subject_ids[i]
        # print(f'selected subject id = {self.selected_subject_id}')
        self.module_list.clear()
        self.module_ids, self.module_names = ip.print_list(cursor, "module", self.selected_subject_id)
        # print(f'returned module ids = {self.module_ids} and returned names = {self.module_names}')
        self.module_list.addItems(self.module_names)
        # self.moduleSelectionChange(self, 0)

    def moduleSelectionChange(self, i):
        # print(f'i = {i}')
        self.selected_module_id = self.module_ids[i]
        # print(f'selected module id = {self.selected_module_id}')

    def add_topic(self):
        # SEARCH WHETHER TOPIC ALREADY EXISTS UNDER MODULE ID
        self.topic_name = self.topic_edit.text()
        cursor.execute('select count(*) from "Topic" where "Module ID" = %s and "Topic Name" like %s', (self.selected_module_id,self.topic_name))
        if cursor.fetchone()[0] != 0:
            self.msg = QMessageBox()
            self.msg.setText("Topic already exists! Try again.")
            self.msg.show()
            self.msg.setStandardButtons(QMessageBox.Ok)

        else:

            # get the input values and create a string to represent the topic
            subject = self.subject_list.currentText()
            module = self.module_list.currentText()

            difficulty = self.difficulty_slider.value()/10
            weightage = self.weightage_slider.value()/10
            topic_str = f"{subject} - {module}: {self.topic_name}"

            # add the topic string to the list and update the label
            self.topics_list.append(topic_str)
            self.topics_label.setText("Added Topics:\n" + "\n".join(self.topics_list))
            # reset the input fields
            self.topic_edit.setText("")
            self.difficulty_slider.setValue(0)
            self.weightage_slider.setValue(0)
            # self.subject_list.setCurrentIndex(0)
            # self.module_list.setCurrentIndex(0)



            # INSERT TOPIC NAME, WEIGHTAGE, DIFFICULTY ALONG WITH SELF.SELECTED_MODULE_ID
            # UNCOMMENT
            cursor.execute(
                'insert into "Topic" ("Module ID", "Topic Name", "Topic Difficulty", "Topic Weightage") values (%s, %s, %s, %s)',
                ((self.selected_module_id, self.topic_name, difficulty, weightage)))

            cursor.execute('select "TID" from "Topic" where "Module ID" = %s and "Topic Name" = %s', (self.selected_module_id, self.topic_name))
            self.topic_id = cursor.fetchone()[0]

            # msg_box = QMessageBox()
            # msg_box.setWindowTitle("Information")
            # msg_box.setText("Topic Added.")
            # msg_box.setStandardButtons(QMessageBox.Ok)
            # msg_box.exec()

            topic_difficulties = []
            cursor.execute('select "TID", "Topic Difficulty" from "Topic" where "Module ID" = %s', (self.selected_module_id,))
            for i in cursor.fetchall():
                topic_difficulties.append(i[1])
            module_difficulty  = sum(topic_difficulties)/len(topic_difficulties)
            print(f'Module Difficulty: {module_difficulty}')

            # UNCOMMENT
            cursor.execute('update "Module" set "Module Difficulty" = %s where "MID" = %s', (module_difficulty, self.selected_module_id))
            # CALCULATE MODULE DIFFICULTY

            self.calc_time_to_study()



    def calc_time_to_study(self):
        cursor.execute('select count(distinct("Study Time Required")) from "Topic"')
        count = cursor.fetchone()[0]
        print(f"count: {count}")
        if count >= 2:
            self.polyfit()

        elif count < 2:
            study_time, ok = QInputDialog.getInt(None, "Enter time", f'Enter time in minutes required to study {self.topic_name}:', 0,
                                            0, 9999999)
            # If the user clicked OK, show the value in a message box
            if ok:
                # QMessageBox.information(None, "Value entered", f"You entered: {value}")
                cursor.execute('update "Topic" set "Study Time Required" = %s where "TID" = %s', (study_time,self.topic_id))

                cursor.execute('select count(distinct("Study Time Required")) from "Topic"')
                count = cursor.fetchone()[0]
                if count == 2:
                    self.polyfit()


            # cursor.execute('select min("Topic Difficulty") from "Topic"')
            # self.min_diff = cursor.fetchone()[0]
            #
            # cursor.execute('select max("Topic Difficulty") from "Topic"')
            # self.max_diff = cursor.fetchone()[0]
            #
            # cursor.execute(
            #     'select "Topic Name" from "Topic" where "Topic Difficulty" = (select min("Topic Difficulty") from "Topic")')
            # min_diff_name = cursor.fetchone()[0]
            # print('min', min_diff_name)
            # # min_time = int(input(f'Enter time required to study {min_diff_name}:'))
            #
            # cursor.execute(
            #     'select "Topic Name" from "Topic" where "Topic Difficulty" = (select max("Topic Difficulty") from "Topic")')
            # max_diff_name = cursor.fetchone()[0]
            # print('max', max_diff_name)
            # # max_time = int(input(f'Enter time required to study {max_diff_name}:'))
            #
            # self.study_time_required_screen = studyTimeRequiredInput(min_diff_name, max_diff_name)
            # self.study_time_required_screen.show()
            # self.study_time_required_screen.values_submitted.connect(self.handle_values_submitted)

    def polyfit(self):
        cursor.execute(
            'select "Topic Difficulty", "Study Time Required" from "Topic" where "Study Time Required" != 0 and "Topic Difficulty"=(select min("Topic Difficulty") from "Topic")')

        cursor.execute('select "Study Time Required from Topic where study time required !=0 and TID in "')
        result = cursor.fetchone()
        self.min_diff = result[0]
        min_time = result[1]

        cursor.execute(
            'select "Topic Difficulty", "Study Time Required" from "Topic" where "Study Time Required" != 0 and "Topic Difficulty"=(select max("Topic Difficulty") from "Topic")')
        result = cursor.fetchone()
        self.max_diff = result[0]
        max_time = result[1]

        difficulty = np.array([self.min_diff, self.max_diff])
        time_to_study = np.array([min_time, max_time])
        m, b = np.polyfit(difficulty, time_to_study, 1)

        cursor.execute('select "TID", "Topic Difficulty" from "Topic" ')
        for i in cursor.fetchall():
            difficulty_new = i[1]
            time_to_study_new = m * difficulty_new + b
            print(f'TID: {i[0]}, Time to study = {time_to_study_new}')
            # UNCOMMENT
            cursor.execute('update "Topic" set "Study Time Required" = %s where "TID" = %s',
                           (time_to_study_new, i[0]))

        # QMessageBox.information(None, " ", "Study Time Updated")




    # def calc_time_to_study(self):
    #     # MAKE THIS OCCUR ONLY ONCE EVER......YTIME THE USER OPENS THE APP AND ADDS TOPIC THE FIRST TIME
    #     if self.study_time_flag == 0:
    #         self.study_time_flag = 1
    #         cursor.execute('select count("TID") from "Topic"')
    #         if cursor.fetchone()[0] >= 2:
    #             cursor.execute('select min("Topic Difficulty") from "Topic"')
    #             self.min_diff = cursor.fetchone()[0]
    #
    #             cursor.execute('select max("Topic Difficulty") from "Topic"')
    #             self.max_diff = cursor.fetchone()[0]
    #
    #             if self.min_diff != self.max_diff:
    #                 cursor.execute(
    #                     'select "Topic Name" from "Topic" where "Topic Difficulty" = (select min("Topic Difficulty") from "Topic")')
    #                 min_diff_name = cursor.fetchone()[0]
    #                 print('min', min_diff_name)
    #                 # min_time = int(input(f'Enter time required to study {min_diff_name}:'))
    #
    #                 cursor.execute(
    #                     'select "Topic Name" from "Topic" where "Topic Difficulty" = (select max("Topic Difficulty") from "Topic")')
    #                 max_diff_name = cursor.fetchone()[0]
    #                 print('max', max_diff_name)
    #                 # max_time = int(input(f'Enter time required to study {max_diff_name}:'))
    #
    #                 self.study_time_required_screen = studyTimeRequiredInput(min_diff_name, max_diff_name)
    #                 self.study_time_required_screen.show()
    #                 self.study_time_required_screen.values_submitted.connect(self.handle_values_submitted)
    #
    #     else:
    #         cursor.execute('select "Study Time Required" from Topic where "Topic Difficulty" = (select min("Topic Difficulty") from "Topic")')
    #         min_time = cursor.fetchone()[0]
    #
    #         cursor.execute('select "Study Time Required" from Topic where "Topic Difficulty" = (select max("Topic Difficulty") from "Topic")')
    #         max_time = cursor.fetchone()[0]
    #
    #         self.handle_values_submitted(min_time, max_time)

    # def handle_values_submitted(self, min_time, max_time):
    #     difficulty = np.array([self.min_diff, self.max_diff])
    #     time_to_study = np.array([min_time, max_time])
    #     m, b = np.polyfit(difficulty, time_to_study, 1)
    #
    #     cursor.execute('select "TID", "Topic Difficulty" from "Topic" ')
    #     for i in cursor.fetchall():
    #         difficulty_new = i[1]
    #         time_to_study_new = m * difficulty_new + b
    #         # print(f'TID: {i[0]}, Time to study = {time_to_study_new}')
    #
    #         cursor.execute('update "Topic" set "Study Time Required" = %s where "TID" = %s',
    #                        (time_to_study_new, i[0]))

        # msg_box = QMessageBox()
        # msg_box.setWindowTitle("Information")
        # msg_box.setText("Study Time Required calculated.")
        # msg_box.setStandardButtons(QMessageBox.Ok)
        # msg_box.exec()

    def back_button_clicked(self):
        self.close()
        self.parent.show()

# class studyTimeRequiredInput(QWidget):
#     # Define a signal with two integer arguments
#     values_submitted = Signal(int, int)
#
#
#     def __init__(self, min_diff_name, max_diff_name):
#         super().__init__()
#         self.setWindowTitle("Time Required to Study")
#
#         self.label1 = QLabel(f'Enter time in minutes required to study "{min_diff_name}":')
#         self.spinbox1 = QSpinBox()
#
#         self.label2 = QLabel(f'Enter time in minutes required to study "{max_diff_name}":')
#         self.spinbox2 = QSpinBox()
#
#         submit_button = QPushButton('Submit')
#         submit_button.clicked.connect(self.submit)
#
#         hbox1 = QVBoxLayout()
#         hbox1.addWidget(self.label1)
#         hbox1.addWidget(self.spinbox1)
#
#         hbox2 = QVBoxLayout()
#         hbox2.addWidget(self.label2)
#         hbox2.addWidget(self.spinbox2)
#
#         vbox = QVBoxLayout()
#         vbox.addLayout(hbox1)
#         vbox.addLayout(hbox2)
#         vbox.addWidget(submit_button)
#
#         self.setLayout(vbox)
#
#     def submit(self):
#         min_time = self.spinbox1.value()
#         max_time = self.spinbox2.value()
#
#         # Emit the values_submitted signal with the spinbox values as arguments
#         self.values_submitted.emit(min_time, max_time)
#         self.close()

class FileBrowse(QWidget):

    def __init__(self, parent = None):
        super().__init__()

        self.parent = parent
        self.setParent(None)
        self.parent.hide()

        self.setWindowTitle("Select Files")
        # self.resize(400, 300)
        # self.setGeometry(100, 100, 400, 300)

        self.uploaded_files_count = 0
        Geometry(self)

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.back_button_clicked)

        self.subject_ids, self.subject_names = ip.print_list(cursor, "subject")
        # print(f'returned subject ids = {self.subject_ids} and returned names = {self.subject_names}')
        subject_label = QLabel("Subject:")
        self.subject_list = QComboBox()
        self.subject_list.addItems(self.subject_names)
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(subject_label)
        subject_layout.addWidget(self.subject_list)
        self.subject_list.currentIndexChanged.connect(self.subjectSelectionChange)
        self.selected_subject_id = self.subject_ids[0]

        self.module_ids, self.module_names = ip.print_list(cursor, "module", self.selected_subject_id)
        # print(f'returned module ids = {self.module_ids} and returned names = {self.module_names}')
        module_label = QLabel("Module:")
        self.module_list = QComboBox()
        self.module_list.addItems(self.module_names)
        module_layout = QHBoxLayout()
        module_layout.addWidget(module_label)
        module_layout.addWidget(self.module_list)
        self.module_list.currentIndexChanged.connect(self.moduleSelectionChange)
        self.selected_module_id = self.module_ids[0]

        

        self.file_label = QLabel(self)
        self.file_label.setWordWrap(True)
        # file_label.setGeometry(50, 100, 1000, 500)
        self.file_label.setText("No files selected")
        self.file_label.setFixedWidth(300)
        # self.main_widget = QWidget(self)
        # self.setCentralWidget(self.main_widget)
        # self.main_layout = QVBoxLayout(self.main_widget)
        # self.main_layout.addWidget(self.add_button)
        # self.main_layout.addWidget(self.file_label)


        self.layout=QVBoxLayout()
        subject_layout=QHBoxLayout()
        subject_layout.addWidget(subject_label)
        subject_layout.addWidget(self.subject_list)

        module_layout=QHBoxLayout()
        module_layout.addWidget(module_label)
        module_layout.addWidget(self.module_list)
        
        button_layout=QHBoxLayout()

        add_files_button = QPushButton("Add File", self)
        add_files_button.clicked.connect(self.browse_files)
        
        # self.main_layout.addWidget(self.add_files_button)
        

        # add_topics_button = QPushButton("Add Topics", self)
        # add_topics_button.clicked.connect(self.add_topics_clicked)

        submit_button = QPushButton("Submit", self)
        submit_button.clicked.connect(self.submit_button_clicked)
        # self.main_layout.addWidget(self.add_files_button)

        button_layout.addWidget(add_files_button)
        # button_layout.addWidget(add_topics_button)
        button_layout.addWidget(submit_button)

        self.layout.addLayout(subject_layout)
        self.layout.addLayout(module_layout)
        self.layout.addLayout(button_layout)
        self.layout.addWidget(back_button, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.file_label)

        self.setLayout(self.layout)
        self.selected_files = []
        self.selected_file_names=[]
        self.show()

    def subjectSelectionChange(self, i):
        self.selected_subject_id = self.subject_ids[i]
        # print(f'selected subject id = {self.selected_subject_id}')
        self.module_list.clear()
        self.module_ids, self.module_names = ip.print_list(cursor, "module", self.selected_subject_id)
        # print(f'returned module ids = {self.module_ids} and returned names = {self.module_names}')
        self.module_list.addItems(self.module_names)
        # self.moduleSelectionChange(self, 0)

    def moduleSelectionChange(self, i):
        # print(f'i = {i}')
        self.selected_module_id = self.module_ids[i]
        


    # def add_topics_clicked(self):
    #     self.add_topics_screen=addTopicScreen()
    #     self.add_topics_screen.show()
    #     self.close()


    def browse_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("PDF files (*.pdf)")
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            for file_path in file_paths:
                # Add the file path to the list of selected files

                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    # Get just the file name from the path
                    file_name = os.path.basename(file_path)
                    self.selected_file_names.append(file_name)
                    self.uploaded_files_count+=1
        self.file_label.setText("Selected Files: \n" + "\n".join(self.selected_file_names))
        self.adjustSize()
        # self.layout.addWidget(self.file_label)

    def submit_button_clicked(self):
        #submit pdf to be concatenated and fed to pdf gpt to generate questions
        print(self.uploaded_files_count)
        extracted_text= ''
        for file_path in self.selected_files:
            reader=PdfReader(file_path)
            # raw_text = ''
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    extracted_text += text
            # full_text += raw_text

        extracted_text = ''.join(extracted_text.splitlines())
        print(self.selected_module_id, extracted_text)


        qa = qg.generate_questions(cursor, self.selected_module_id, extracted_text)
        self.close()
        self.question_feedback_screen = QuestionFeedback(self.parent, qa)
        self.question_feedback_screen.show()
        print("questions generated")

    def back_button_clicked(self):
        self.close()
        self.parent.show()


class QuestionFeedback(QWidget):
    def __init__(self, add_content_screen, qa):
        super().__init__()
        self.setWindowTitle("Generated Questions")
        self.layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.question_layout = QVBoxLayout()
        self.add_content_screen = add_content_screen
        self.qa = qa

        # Create a check box for each question name
        for i in self.qa:
            check_box = QCheckBox(f'Q.{i[1]} Ans. {i[2]}')
            self.question_layout.addWidget(check_box)

        self.submit_btn = QPushButton('Exclude Selected Questions')
        self.submit_btn.clicked.connect(self.get_selected_questions)

        # Create a group box to hold the questions and answers
        self.group_box = QGroupBox()
        self.group_box.setLayout(self.layout)

        self.scroll_area.setWidget(self.group_box)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)

        self.layout.addLayout(self.question_layout)
        main_layout.addWidget(self.submit_btn)

        self.selected_questions = {}

    def get_selected_questions(self):
        indexes_to_remove = []
        for i in range(self.question_layout.count()):
            widget = self.question_layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                indexes_to_remove.append(i)

        indexes_to_remove.sort(reverse=True)

        # print(selected_items)
        for i in indexes_to_remove:
            self.qa.pop(i)

        for i in self.qa:
            duration = len(i[2].split()) * 5
            cursor.execute(
                'insert into "Question" ("Topic ID", "Question", "Answer", "Duration") values (%s, %s, %s, %s);',
                (i[0], i[1], i[2], duration))

        self.calc_normalized_duration()

        QMessageBox.information(None, " ", "Questions stored in Database")
        self.close()
        self.add_content_screen.show()

    def calc_normalized_duration(self):
        cursor.execute('select min("Duration") from "Question"')
        min = cursor.fetchone()[0]
        cursor.execute('select max("Duration") from "Question"')
        max = cursor.fetchone()[0]

        cursor.execute('select count(*) from "Question"')
        no_q = cursor.fetchall()[0]
        # for i in range(no_q):
        cursor.execute('select "QID","Duration" from "Question"')
        for i in cursor.fetchall():
            qid = i[0]
            d = i[1]
            normalized_q_duration = ((d - min) / (max - min)) * 10
            cursor.execute('update "Question" set "Norm Duration"=%s where "QID"=%s', (normalized_q_duration, qid))


class AddExamScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        self.setParent(None)
        self.parent.hide()

        self.setWindowTitle("Add Exam")
        # self.setGeometry(100, 100, 400, 300)   
        Geometry(self) 
        # self.resize(400, 300)

        self.subject_ids, self.subject_names = ip.print_list(cursor, "subject")
        # print(f'returned subject ids = {self.subject_ids} and returned names = {self.subject_names}')
        subject_label = QLabel("Subject:")
        self.subject_list = QComboBox()
        self.subject_list.addItems(self.subject_names)
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(subject_label)
        subject_layout.addWidget(self.subject_list)
        self.subject_list.currentIndexChanged.connect(self.subjectSelectionChange)
        self.selected_subject_id = self.subject_ids[0]

        self.selected_module_ids=[]

        # DESIGN NEW PORTION SELECTOR UI

        module_label = QLabel("Module:")
        self.module_ids, self.module_names = ip.print_list(cursor, "module", self.selected_subject_id)
        self.module_layout = QVBoxLayout()

        # Create a check box for each module name
        for name in self.module_names:
            check_box = QCheckBox(name)
            self.module_layout.addWidget(check_box)

        # Create labels and input fields
        exam_label = QLabel("Exam Name:")
        self.exam_input = QLineEdit()
        exam_date_label = QLabel("Exam Date:")
        self.exam_date_input = QCalendarWidget()
        percent_label = QLabel("Target Percent:")
        # self.percent_input = QLineEdit()
        self.percent_spinbox = QSpinBox()
        self.percent_spinbox.setRange(0,100)


        study_test_ratio_label = QLabel("Study/Test Ratio:")
        # self.study_test_ratio_input = QLineEdit()
        self.study_label = QLabel('Study')
        self.study_label.setAlignment(Qt.AlignRight)
        self.study_label.setFixedHeight(30)

        self.spin_box_1 = QSpinBox()
        self.spin_box_1.setMinimum(1)
        self.spin_box_1.setFixedSize(40, 30)

        self.colon_label = QLabel(":")
        self.colon_label.setFixedSize(10, 30)
        self.colon_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(17)
        font.setBold(True)
        self.colon_label.setFont(font)

        self.spin_box_2 = QSpinBox()
        self.spin_box_2.setMinimum(1)
        self.spin_box_2.setFixedSize(40, 30)

        self.test_label = QLabel('Test')
        self.test_label.setAlignment(Qt.AlignLeft)
        self.test_label.setFixedHeight(30)

        ratio_layout = QGridLayout()
        ratio_layout.addWidget(self.study_label, 0,0)
        ratio_layout.addWidget(self.spin_box_1, 0,1)
        ratio_layout.addWidget(self.colon_label, 0,2)
        ratio_layout.addWidget(self.spin_box_2, 0,3)
        ratio_layout.addWidget(self.test_label, 0, 4)

        self.submit_button=QPushButton('Add')
        # self.submit_button.setFixedSize(100,50)
        self.submit_button.clicked.connect(self.submit_button_clicked)

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.back_button_clicked)

        # Create a layout to arrange the labels and input fields
        layout = QVBoxLayout()
        layout.addWidget(subject_label)
        layout.addWidget(self.subject_list)
        layout.addWidget(module_label)
        layout.addLayout(self.module_layout)
        layout.addWidget(exam_label)
        layout.addWidget(self.exam_input)
        layout.addWidget(exam_date_label)
        layout.addWidget(self.exam_date_input)
        layout.addWidget(percent_label)
        layout.addWidget(self.percent_spinbox)
        layout.addWidget(study_test_ratio_label)
        # layout.addWidget(self.study_test_ratio_input)
        layout.addLayout(ratio_layout)
        layout.addWidget(self.submit_button)
        layout.addWidget(back_button, alignment=Qt.AlignLeft)
        # Set the layout for the screen
        self.setLayout(layout)
        self.show()

    def submit_button_clicked(self):
        # CHECK IF EXAM NAME EXIST ALREADY
        self.exam_name = self.exam_input.text()
        cursor.execute('select count(*) from "Exam" where "Exam Name" like %s', (self.exam_name,))
        if cursor.fetchone()[0] != 0:
            self.msg = QMessageBox()
            self.msg.setText("Exam already exists! Try again.")
            self.msg.show()
            self.msg.setStandardButtons(QMessageBox.Ok)


        # self.msg = QMessageBox()
        # self.msg.setText("test")
        # self.msg.show()
        # self.msg.setStandardButtons(QMessageBox.Ok)

        else:
            portion_ids = {"subject": '', 'modules': [], "topics": []}
            portion_ids['subject'] = self.selected_subject_id
            self.selected_module_ids = self.get_selected_modules(self.module_layout)
            portion_ids['modules'] = self.selected_module_ids
            # GET TOPIC IDS IN SELECTED MODULES / PORTIONS
            for mid in self.selected_module_ids:
                cursor.execute('select "TID" from "Topic" where "Module ID" = %s', (mid,))
                for i in cursor.fetchall():
                    portion_ids['topics'].append(i[0])

            # Get the exam date
            self.exam_date = self.exam_date_input.selectedDate().toString('dd-MM-yyyy')

            # Get the target percent
            self.target_score_percent = self.percent_spinbox.value()

            # self.study_test_ratio = self.study_test_ratio_input.text()
            x = self.spin_box_1.value()
            y = self.spin_box_2.value()
            self.study_test_ratio = str(x) + ':' + str(y)

            print(self.exam_name, self.exam_date, self.target_score_percent, self.study_test_ratio)


            # create function calc_learning time(cursor, self.exam_date, self.study_test_ratio, portion_ids) in Task_Suggester


            # PROTECT AGAINST DIVISION BY ZERO BY PUTTING MINIMUM VALUE AS 1 IN STUDY TEST RATIO
            # study_test_ratio_number = int(self.study_test_ratio.split(":")[0]) / int(self.study_test_ratio.split(":")[1])
            study_test_ratio_number = x/y

            portion_study_time_sum = 0
            for i in portion_ids['topics']:
                cursor.execute('select "Study Time Required" from "Topic" where "TID" = %s', (i,))
                portion_study_time_sum += cursor.fetchone()[0]

            # # Calculating total studying time
            # exam_date_formatted = datetime.strptime(self.exam_date, "%d-%m-%Y")
            # t = (exam_date_formatted - datetime.now()).total_seconds() / 60  # minutes till deadline
            # ebbinghaus_loss = (100 - (148 / (1.25 * math.log(t, 10) + 1.48))) / 100
            # total_studying_time = portion_study_time_sum * (1 + ebbinghaus_loss)
            print("Total Studying Time: ", portion_study_time_sum)

            total_question_duration = 0
            for i in portion_ids['topics']:
                cursor.execute('select "Duration" from "Question" where "Topic ID" = %s', (i,))
                for j in cursor.fetchall():
                    if j != None:
                        total_question_duration += j[0]
            total_question_duration = round(total_question_duration / 60)

            #EVALUATE
            # total_testing_time = total_question_duration * (1 + ebbinghaus_loss)

            # Calculating total testing time
            total_testing_time = max(total_question_duration, round(portion_study_time_sum / study_test_ratio_number))
            # EVALUATE
            # total_testing_time = max(total_testing_time, total_studying_time / study_test_ratio_number)
            print("Total Testing Time: ", total_testing_time)

            # Calculating total learning time
            total_learning_time = portion_study_time_sum + total_testing_time
            print("Total Learning Time: ", total_learning_time)




            exam_date_formatted = datetime.strptime(self.exam_date, "%d-%m-%Y")
            time_left_till_deadline = (exam_date_formatted - datetime.now()).total_seconds() / 60  # minutes till deadline
            learning_time_available = math.floor(time_left_till_deadline * 0.7)  # max learning time available taken as 70% of all available minutes
            print(f'Available Learning Time = {learning_time_available}')

            # priority = round((total_learning_time / learning_time_available) * 100, 2)

            if total_learning_time > learning_time_available:
                total_learning_time = learning_time_available



            added_date = datetime.today().strftime('%d-%m-%Y')
            # UNCOMMENT
            cursor.execute('INSERT INTO "Exam" ("Exam Name", "Exam Date", "Target Score Percent", "Total Learning Time", "Learning Time Left", "Study Test Ratio", "Added Date")\
                VALUES (%s,%s,%s,%s,%s,%s,%s);',
                           (self.exam_name, self.exam_date, self.target_score_percent, total_learning_time, total_learning_time, self.study_test_ratio, added_date))

            exam_portions = {}
            # UNCOMMENT
            os.chdir('..\Text Files')
            if os.path.isfile('Exam Portions.json'):
                with open('Exam Portions.json', 'r') as f:
                    exam_portions = json.load(f)

            cursor.execute('select "EID" from "Exam" where "Exam Name" = %s', (self.exam_name,))
            exam_id = cursor.fetchone()[0]
            exam_portions[str(exam_id)] = portion_ids
            print(exam_portions)

            # UNCOMMENT
            with open('Exam Portions.json', 'w') as f:
                json.dump(exam_portions, f)

            # os.chdir('..\Text Files')

            progress_details = {}
            if os.path.isfile('Progress Details.json'):
                with open('Progress Details.json', 'r') as f:
                    progress_details = json.load(f)

            progress_details[str(exam_id)] = {'Proficiency': [0], "Pomodoro": [0]}
            print(progress_details)
            with open('Progress Details.json', 'w') as f:
                json.dump(progress_details, f)

            ts.update_learning_plan(cursor, exam_id)
            # print(self.selected_module_ids)
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Information")
            msg_box.setText("Exam added")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            self.close()
            self.parent.show()

    def subjectSelectionChange(self, i):
        self.selected_subject_id = self.subject_ids[i]
        # print(f'selected subject id = {self.selected_subject_id}')
        self.clear_layout(self.module_layout)
        self.module_ids, self.module_names = ip.print_list(cursor, "module", self.selected_subject_id)
        print(f'returned module ids = {self.module_ids} and returned names = {self.module_names}')
        # self.module_list.addItems(self.module_names)
        for name in self.module_names:
            check_box = QCheckBox(name)
            self.module_layout.addWidget(check_box)
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.clear_layout(self, item.layout())

    def get_selected_modules(self, layout):
        selected_items = []
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected_items.append(self.module_ids[i])
        return selected_items

    def back_button_clicked(self):
        self.close()
        self.parent.show()

class HeaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        self.label1 = QLabel("Exam Name")
        self.label1.setStyleSheet("font-weight: bold;")
        self.label2 = QLabel("Priority")
        self.label2.setStyleSheet("font-weight: bold;")

        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

class ItemWidget(QWidget):
    def __init__(self, exam_name, exam_priority):
        super().__init__()
        layout = QHBoxLayout()
        # self.button = QPushButton("Study")
        self.exam_name = QLabel(exam_name)
        self.exam_priority = QLabel(str(exam_priority))
        layout.addWidget(self.exam_name)
        layout.addWidget(self.exam_priority)
        # layout.addWidget(self.button)
        self.setLayout(layout)


class examPriorityList(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("List Widget Example")
        self.layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.header_widget = HeaderWidget()
        self.layout.addWidget(self.header_widget)
        self.layout.addWidget(self.list_widget)
        self.update_list()
        self.setLayout(self.layout)

    def update_list(self):
        self.list_widget.clear()
        cursor.execute('select "Exam Name", "Target Score Percent" - "Predicted Score Percent"  from "Exam"')
        items = cursor.fetchall()
        vals = []
        for i in items:
            vals.append(i[1])

        min_prio = min(vals)
        max_prio = max(vals)

        items = sorted(items, key=lambda x: x[1], reverse=True)


        for item in items:
            list_item = QListWidgetItem(self.list_widget)
            normalized_item = 100
            if max_prio != min_prio:
                normalized_item = round(((item[1] - min_prio) / (max_prio - min_prio)) * 100, 2)
            print(normalized_item)
            item_widget = ItemWidget(item[0], normalized_item)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.setItemWidget(list_item, item_widget)


class ExamListScreen(QWidget):
    pomo_sequence = 0
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        self.setParent(None)
        self.parent.hide()

        self.start_rest_timer_flag = 0
        self.setWindowTitle("Learning Module")
        Geometry(self)
        self.counter = 0
        self.select_exam_label = QLabel('Select Exam:')


        self.start_learning_button=QPushButton('Start Next Session')
        self.start_learning_button.clicked.connect(self.start_learning_button_clicked)
        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(self.exit_button_clicked)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_learning_button)
        button_layout.addWidget(self.exit_button)

        self.rest_timer_label = QLabel('Rest Timer:')
        self.start_button = QPushButton('Start')
        self.pause_button = QPushButton('Pause')
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.start_button.clicked.connect(self.startTimer)
        self.pause_button.clicked.connect(self.pauseTimer)

        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)
        self.lcd = QLCDNumber()
        self.lcd.setDigitCount(5)
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        self.lcd.setStyleSheet("color: black; background-color: white;")
        self.lcd.display(rest_duration.toString('mm:ss'))
        self.lcd.display("05:00")

        self.timer_layout = QHBoxLayout()
        self.timer_layout.addWidget(self.rest_timer_label)
        self.timer_layout.addWidget(self.lcd)
        self.timer_layout.addWidget(self.start_button)
        self.timer_layout.addWidget(self.pause_button)


        self.exam_ids, exam_names=ip.print_list(cursor, "exam")
        print(f'returned exam ids = {self.exam_ids} and returned names = {exam_names}')
        exam_list=QComboBox()
        exam_list.addItems(exam_names)
        exam_list.currentIndexChanged.connect(self.selectionChange)
        self.selected_exam_id=self.exam_ids[0]

        select_exam_layout = QGridLayout()
        select_exam_layout.addWidget(self.select_exam_label,0 ,0)
        select_exam_layout.addWidget(exam_list, 0, 1)

        layout = QVBoxLayout()
        self.exam_priority_list = examPriorityList()
        layout.addWidget(self.exam_priority_list)
        layout.addLayout(select_exam_layout)
        layout.addLayout(self.timer_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.show()

    def selectionChange(self, i):
        self.selected_exam_id=self.exam_ids[i]
        print("selected exam id: ",self.selected_exam_id)


    def start_learning_button_clicked(self):
        global current_exam_id, current_time_left, rest_duration
        if self.pomo_sequence == 0:
            rest_duration = original_rest_duration
        self.start_learning_button.setEnabled(False)
        if self.start_rest_timer_flag == 0:
            self.start_button.setEnabled(True)
            self.start_rest_timer_flag = 1
        plan_exists_flag = ts.main(cursor, self.selected_exam_id)
        current_exam_id = self.selected_exam_id
        print(self.selected_exam_id)
        if plan_exists_flag == True:
            next_session = ts.get_next_session(cursor, current_exam_id)
            if next_session == 'study':
                self.study_screen = Task(self)
                self.study_screen.show()
                self.pomo_sequence += 1
                # UNCOMMENT
                self.update_pomo_details()

            elif next_session == 'test':
                self.start_test_screen = startTestScreen(self)
                self.start_test_screen.show()
                self.pomo_sequence += 1
                self.update_pomo_details()

        if self.pomo_sequence == 4:
            rest_duration = doubled_rest_duration
            self.pomo_sequence = 0

        self.lcd.display(rest_duration.toString('mm:ss'))

    def update_pomo_details(self):
        exam_id = current_exam_id
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

        print("Progress Details (Pomo): ",progress_details[str(exam_id)]['Pomodoro'] )

        with open('Progress Details.json', 'w') as f:
            json.dump(progress_details, f)

    def startTimer(self):
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.start_learning_button.setEnabled(False)
        self.time_left = rest_duration
        self.timer.start(1000)

    def pauseTimer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setText("Resume")
        else:
            self.timer.start()
            self.pause_button.setText("Pause")

    def showTime(self):
        self.time_left = self.time_left.addSecs(-1)
        if self.time_left.minute() == 0 and self.time_left.second() == 0:
            self.timer.stop()
            self.time_left=rest_duration
            self.start_learning_button.setEnabled(True)
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
        self.lcd.display(self.time_left.toString('mm:ss'))

    def exit_button_clicked(self):
        self.close()
        self.parent.show()



class Task(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle("Study Session")
        self.parent = parent
        self.setParent(None)
        self.parent.hide()

        Geometry(self)
        # self.exam_id=exam_id
        self.exam_id=current_exam_id
        print(f'exam id at Task: {self.exam_id}')
        portion=ts.next_study_session_portion(cursor, self.exam_id)
        print("portion: ", portion)
        self.task_label = QLabel(portion)
        self.task_label.setWordWrap(True)

        self.start_button = QPushButton('Start')
        self.pause_button = QPushButton('Pause')
        self.finished_button=QPushButton('Back')
        self.pause_button.setEnabled(False)
        self.start_button.clicked.connect(self.startTimer)
        self.pause_button.clicked.connect(self.pauseTimer)
        self.finished_button.clicked.connect(self.finished_button_clicked)

        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)
        self.lcd = QLCDNumber()
        self.lcd.setDigitCount(5)
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        self.lcd.setStyleSheet("color: black; background-color: white;")
        self.lcd.display('25:00')


        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.pause_button)
        vbox.addWidget(self.task_label)
        vbox.addWidget(self.lcd)
        vbox.addLayout(hbox)
        vbox.addWidget(self.finished_button)
        self.setLayout(vbox)

        self.setWindowTitle('Study Session')
        self.show()
        self.time_left = QTime(0, 25, 0)

    def startTimer(self):
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.timer.start(1000)


    def pauseTimer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setText("Resume")
        else:
            self.timer.start()
            self.pause_button.setText("Pause")

    def showTime(self):
        self.time_left = self.time_left.addSecs(-1)
        if self.time_left.minute() == 0 and self.time_left.second() == 0:
            self.timer.stop()
            self.finished_button_clicked()
        self.lcd.display(self.time_left.toString('mm:ss'))

    def finished_button_clicked(self):
        cursor.execute('select "Learning Time Left" from "Exam" where "EID" = %s', (current_exam_id,))
        learning_time_left = cursor.fetchone()[0]
        learning_time_left -= 25 - math.floor((current_time_left.minute() * 60 + current_time_left.second())/60)
        if learning_time_left < 0:
            learning_time_left = 0
        print(f'learning time left: {learning_time_left}')
        cursor.execute('Update "Exam" set "Learning Time Left" = %s where "EID" = %s', (learning_time_left, current_exam_id))

        self.close()
        self.parent.show()


class startTestScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setParent(None)
        self.parent.hide()

        Geometry(self)
        self.setWindowTitle("Test Instructions")

        # Create label with multiline text
        label_text = "1. The following test will last 25 minutes.\n2. After submitting the answer, the answer accuracy will be shown\n3. Then, a self-evaluation will be conducted"
        label = QLabel(label_text)
        label.setWordWrap(True)

        # Create button to start test
        button = QPushButton("Start Test")
        button.clicked.connect(self.startTest)

        # Create layout and add label and button
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(button)

        # Set layout for widget
        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)
        self.time_left = current_time_left = test_duration

    def showTime(self):
        self.time_left = self.time_left.addSecs(-1)
        global current_time_left
        current_time_left = self.time_left
        print(self.time_left)

        if self.time_left.minute() == 0 and self.time_left.second() == 0:
            self.timer.stop()
            self.close()
            self.deactivate_qa_screen()
            self.parent.exam_priority_list.update_list()

    def startTest(self):
        global test_timer
        self.QAScreen = QuestionAnswerWidget(self.parent, self)
        self.hide()
        self.QAScreen.show()
        self.timer.start(1000)
        test_timer = self.timer

    def deactivate_qa_screen(self):
        global current_qa_screen
        current_qa_screen.answer_text.setText("Time Over")
        current_qa_screen.answer_text.setReadOnly(True)
        current_qa_screen.submit_button.hide()


class QuestionAnswerWidget(QWidget):
    def __init__(self,  session_screen=None, start_test_screen = None):
        global current_qa_screen
        current_qa_screen = self
        super().__init__()
        self.session_screen = session_screen
        self.start_test_screen = start_test_screen

        Geometry(self)
        self.setWindowTitle("Test")
        print("question answer widget started")

        self.qid, self.question = tg.get_next_question(cursor, current_exam_id)

        self.question_label = QLabel(self.question)
        self.question_label.setWordWrap(True)
        self.answer_text = QTextEdit()
        self.answer_text.setPlaceholderText("Type your answer here")
        self.answer_text.setFixedHeight(100)
        self.answer_text.setLineWrapMode(QTextEdit.WidgetWidth)
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_btn_clicked)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.back_button_clicked)

        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)
        self.lcd = QLCDNumber()
        self.lcd.setDigitCount(5)
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        self.lcd.setStyleSheet("color: black; background-color: white;")
        self.lcd.display(test_duration.toString('mm:ss'))
        self.lcd.setFixedSize(100, 50)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.lcd, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.question_label)
        self.layout.addWidget(self.answer_text)
        self.layout.addWidget(self.submit_button)
        self.layout.addWidget(self.back_button)

        self.timer.start(100)

        self.setLayout(self.layout)

    def showTime(self):
        global current_time_left
        self.lcd.display(current_time_left.toString('mm:ss'))

    def submit_btn_clicked(self):
        self.answer_text.setReadOnly(True)
        self.submit_button.hide()
        self.back_button.hide()
        self.answer_check_screen = answerCheckScreen(self.session_screen, self, self.qid, self.answer_text.toPlainText())#PASS GIVEN ANSWER
        self.layout.addWidget(self.answer_check_screen)
        self.answer_check_screen.show()


    def back_button_clicked(self):
        cursor.execute('select "Learning Time Left" from "Exam" where "EID" = %s', (current_exam_id,))
        learning_time_left = cursor.fetchone()[0]
        learning_time_left -= 25 - math.ceil((current_time_left.minute() * 60 + current_time_left.second()) / 60)
        if learning_time_left < 0:
            learning_time_left = 0
        print(f'learning time left: {learning_time_left}')
        cursor.execute('Update "Exam" set "Learning Time Left" = %s where "EID" = %s',
                       (learning_time_left, current_exam_id))
        self.close()
        # self.start_test_screen.timer.stop()
        test_timer.stop()
        self.session_screen.exam_priority_list.update_list()
        self.session_screen.show()


class answerCheckScreen(QWidget):
    def __init__(self, session_screen, qawidget, qid, given_answer):
        super().__init__()
        Geometry(self)
        self.session_screen = session_screen
        self.qawidget = qawidget
        self.qid = qid

        # Set up the widget's layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        # GET CORRECT ANSWER FROM DATABASE
        cursor.execute('select "Answer" from "Question" where "QID" = %s', (qid,))
        correct_answer = cursor.fetchone()[0]
        # Add labels for the given and correct answers
        given_answer_label = QLabel(f"Given answer: {given_answer}")
        given_answer_label.setWordWrap(True)

        question = ''  # get from database
        question_label = QLabel(f"Question: {question}")
        question_label.setWordWrap(True)

        correct_answer_label = QLabel(f"Correct answer: {correct_answer}")
        correct_answer_label.setWordWrap(True)

        next_btn = QPushButton('Self Evaluation')
        next_btn.clicked.connect(self.next_btn_clicked)
        layout.addWidget(correct_answer_label)

        accuracy_level_exact = ac.check_answer(given_answer, correct_answer)
        self.accuracy_level = round(accuracy_level_exact,2)  # GET ACCURACY LEVEL FROM ANSWER CHECKER
        # STORE ACCURACY LEVEL AS QUESTION PROFICIENCY IN QUESTION DATABASE

        cursor.execute('update "Question" set "Question Proficiency" = %s where "QID" = %s', (accuracy_level_exact/10,qid))

        # Add a label for the accuracy level
        accuracy_level_label = QLabel(f"Accuracy level: {self.accuracy_level}")

        layout.addWidget(accuracy_level_label)
        layout.addWidget(next_btn)
        self.show()

    def next_btn_clicked(self):
        cursor.execute('select "Target Score Percent" from "Exam" where "EID" = %s', (current_exam_id,))
        target_percent = cursor.fetchone()[0]  # GET TARGET PERCENT FROM EXAM DB USING CURRENT EXAM ID
        if self.accuracy_level >= target_percent:
            correct = True
        else:
            correct = False

        self.self_evaluation_screen = selfEvaluationScreen(self.session_screen, self.qawidget, self.qid, correct)
        self.self_evaluation_screen.show()

class selfEvaluationScreen(QWidget):
    def __init__(self, session_screen, qawidget, qid, correct=False):
        super().__init__()
        Geometry(self)
        self.setWindowTitle("Self Evaluation")
        self.session_screen = session_screen
        self.qawidget = qawidget
        self.qid = qid
        self.correct = correct
        self.evaluation_label = QLabel('Please evaluate your response from one of the following options:-')
        self.evaluation_label.setFixedSize(400, 15)
        if correct == False:
            options = ['Total blackout, complete failure to recall the answer',
                       'Upon seeing the answer, it felt familiar',
                       'Upon seeing the answer, it seemed easy to remember']
        else:
            options = ['Required significant effort to recall the answer',
                       'There was some hesitation in recalling the answer', 'Was able to perfectly recall the answer']
        # create the radio buttons
        self.radio1 = QRadioButton(options[0])
        self.radio2 = QRadioButton(options[1])
        self.radio3 = QRadioButton(options[2])

        self.next_btn = QPushButton('Next Question')
        self.next_btn.clicked.connect(self.next_btn_clicked)

        # create a layout and add the radio buttons to it
        layout = QVBoxLayout()
        layout.addWidget(self.evaluation_label)
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)
        layout.addWidget(self.radio3)
        layout.addWidget(self.next_btn)

        # set the layout for the widget
        self.setLayout(layout)

    def next_btn_clicked(self):
        global current_time_left
        for i in range(1, self.layout().count()):
            if self.layout().itemAt(i).widget().isChecked() == True:
                if self.correct == False:
                    q = i - 1
                else:
                    q = i + 2
        print(f'response = {q}')

        sm2.calc_values(cursor, self.qid, q)
        ts.update_learning_plan(cursor, current_exam_id)

        print(current_time_left)
        if current_time_left.minute() == 0 and current_time_left.second() == 0:
            cursor.execute('select "Learning Time Left" from "Exam" where "EID" = %s', (current_exam_id,))
            learning_time_left = cursor.fetchone()[0]
            learning_time_left -= 25 - math.floor((current_time_left.minute() * 60 + current_time_left.second()) / 60)
            if learning_time_left < 0:
                learning_time_left = 0
            print(f'learning time left: {learning_time_left}')
            cursor.execute('Update "Exam" set "Learning Time Left" = %s where "EID" = %s',
                           (learning_time_left, current_exam_id))
            self.qawidget.close()
            self.close()
            self.session_screen.show()
        else:
            self.qawidget.close()
            self.next_question_screen = QuestionAnswerWidget(self.session_screen)
            self.next_question_screen.show()
            self.close()


class ProgressWidget(QWidget):
    ax = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setParent(None)
        self.parent.hide()
        self.setWindowTitle("Progress Tracker")

        Geometry(self)
        self.exam_ids, exam_names = ip.print_list(cursor, "exam")
        print(f'returned exam ids = {self.exam_ids} and returned names = {exam_names}')
        exam_list = QComboBox()
        exam_list.addItems(exam_names)
        exam_list.currentIndexChanged.connect(self.selectionChange)
        self.selected_exam_id = self.exam_ids[0]

        self.target_percent = QLabel()
        self.target_percent.setFixedSize(150, 20)
        self.target_percent.hide()

        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.back_button_clicked)

        # Create "Show Progress" button
        self.show_progress_button = QPushButton('Show Progress')
        self.show_progress_button.clicked.connect(self.on_show_progress)

        self.show_details_button = QPushButton('Show Details')
        self.show_details_button.clicked.connect(self.on_show_details)
        self.show_details_button.hide()

        self.show_history_button = QPushButton('Show History')
        self.show_history_button.clicked.connect(self.on_show_history)
        self.show_history_button.hide()



        # Add widgets to layout
        layout = QVBoxLayout()
        layout.addWidget(exam_list)
        layout.addWidget(self.show_progress_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.target_percent)
        layout.addWidget(self.show_details_button)
        layout.addWidget(self.show_history_button)
        layout.addWidget(back_button)
        self.setLayout(layout)





    def selectionChange(self, i):
        self.selected_exam_id=self.exam_ids[i]
        print("selected exam id: ",self.selected_exam_id)
        self.show_progress_button.show()

    def on_show_progress(self):
        global current_exam_id
        current_exam_id = self.selected_exam_id
        cursor.execute('select "Target Score Percent", "Portion Proficiency Percent" from "Exam" where "EID" = %s', (self.selected_exam_id,))
        result = cursor.fetchone()
        self.target_percent.setText(f'Target Percent: {round(result[0])}%')
        self.target_percent.show()
        self.progress_bar.show()
        self.progress_bar.setValue(result[1])
        self.show_progress_button.hide()
        self.show_details_button.show()
        self.show_history_button.show()

        # ------------------------------------------------------
        exam_portions = {}
        os.chdir('..\Text Files')
        if os.path.isfile('Progress Details.json'):
            with open('Exam Portions.json', 'r') as f:
                exam_portions = json.load(f)

            if str(self.selected_exam_id) in exam_portions:
                self.portion_ids = exam_portions[str(self.selected_exam_id)]
                print(self.portion_ids)
                self.portion_tids = self.portion_ids['topics']

        if os.path.isfile('Progress Details.json'):
            with open('Progress Details.json', 'r') as f:
                progress_details = json.load(f)
            if str(self.selected_exam_id) in progress_details:
                self.exam_progress_details = progress_details[str(self.selected_exam_id)]


        # ------------------------------------------------------


    def on_show_details(self):
        self.exam_id = 0
        self.module_progress_chart()

    def on_show_history(self):
        self.progress_history()

    def on_click(self, event):
        if event.inaxes is not None:
            for bar in self.ax.containers[0]:
                if bar.contains(event)[0]:
                    module_id = int(bar.get_label())
                    print(f"You clicked on {module_id}")
                    self.topic_progress_chart(module_id)

    def module_progress_chart(self):
        sorted_mids = sorted(self.portion_ids['modules'])
        module_nos = []
        module_names = []
        y=[]

        for mid in sorted_mids:
            cursor.execute('select "Module No", "Module Name", "Module Proficiency" from "Module" where "MID" = %s', (mid,))
            result = cursor.fetchone()
            module_nos.append(f"Module {result[0]}")
            module_names.append(result[1])
            y.append(result[2]*10)


        x = np.array(module_nos)
        y = np.array(y)

        # Create a figure with one subplot
        fig, self.ax = plt.subplots(1, 1)
        self.ax.set_facecolor('#697391')

        # Plot the bar chart on the subplot
        bars = self.ax.bar(x, y, color='navy')

        cursor.execute('select "Exam Name" from "Exam" where "EID" = %s', (self.selected_exam_id,))
        exam_name = f'Exam - {cursor.fetchone()[0]}'
        self.ax.set_title(f'Module Proficiencies for {exam_name}')

        for i, bar in enumerate(bars):
            bars[i].set_label(sorted_mids[i])
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width() / 2, 3, module_names[i], ha='center', color='white', fontsize=10,
                         rotation=90)

        self.ax.set_ylim([0, 100])
        # Set the y-axis label for the subplot
        self.ax.set_ylabel('Proficiency', fontsize=12)

        # Add an event listener to the figure canvas to detect mouse clicks on the bars
        canvas = fig.canvas
        canvas.mpl_connect('button_press_event', self.on_click)
        fig.tight_layout()

        # Display the figure
        plt.show()

    def topic_progress_chart(self, module_id=None):
        sorted_tids = sorted(self.portion_ids['topics'])

        topic_names = []
        x = []

        for tid in sorted_tids:
            cursor.execute('select "Topic Name", "Topic Proficiency" from "Topic" where "TID" = %s',
                           (tid,))
            result = cursor.fetchone()
            topic_names.append(result[0])
            x.append(result[1]*10)

        y = np.arange(len(x))
        x = np.array(x)


        # Create a figure with one subplot
        fig, ax = plt.subplots(1, 1)
        ax.set_facecolor('black')

        # Plot the bar chart on the subplot
        bars = ax.barh(y, x, color='green')

        cursor.execute('select "Module No", "Module Name" from "Module" where "MID" = %s', (module_id,))
        result = cursor.fetchone()
        module_name = f'Module {result[0]} - {result[1]}'
        ax.set_title(f'Topic Proficiencies for {module_name}')

        for i, bar in enumerate(bars):
            ax.text(2, bar.get_y() + bar.get_height() / 2, topic_names[i], va='center', color='white', fontsize=8)

        ax.set_xlim([0, 100])
        # Set the x-axis label for the subplot
        ax.set_xlabel('Proficiency', fontsize=12)

        # Make the y-axis tick labels and ticks invisible
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.invert_yaxis()
        fig.tight_layout()

        # Display the figure
        plt.show()

    def progress_history(self):
        # Generate data
        y2 = np.array(self.exam_progress_details['Proficiency'])
        print(f'y for daily progress: {y2}')

        cursor.execute('select "Added Date", "Exam Date", "Exam Name" from "Exam" where "EID" = %s', (self.selected_exam_id,))
        result = cursor.fetchone()
        added_date = datetime.strptime(result[0], "%d-%m-%Y")
        exam_date = datetime.strptime(result[1], "%d-%m-%Y")
        exam_name = result[2]

        # dates = [date(2023, 5, 1) + timedelta(days=x) for x in range(30)]
        dates = [added_date + timedelta(days=x) for x in range(len(y2))]

        # Convert dates to strings in the required format
        x = [date.strftime('%d/%m') for date in dates]

        # Create figure and plot line
        fig, (ax3, ax2, ax1) = plt.subplots(1, 3, sharex=True, figsize=(14, 5))

        length = (exam_date - added_date).days
        dates2 = [added_date + timedelta(days=x) for x in range(length+1)]
        x2 = [date.strftime('%d/%m') for date in dates2]

        ax1.plot(x, y2, color='brown')
        ax1.scatter(x, y2, color='black', marker='o', s=5)

        cursor.execute('select "Target Score Percent", "Predicted Score Percent" from "Exam" where "EID" = %s', (self.selected_exam_id,))
        result = cursor.fetchone()
        target_percent = result[0]
        predicted_percent = result[1]

        ax1.axhline(y=target_percent, color='g', linestyle='--', label='Target Percent')
        ax1.text(x[-1], target_percent + 2, 'Target Percent', ha='right', va='center', color='g')

        ax1.axhline(y=predicted_percent, color='b', linestyle='--', label='Predicted Percent')
        ax1.text(x[-1], predicted_percent + 2, 'Predicted Percent', ha='right', va='center', color='b')

        # Format x-axis labels
        ax1.xaxis.set_tick_params(rotation=90, labelsize=6)

        # Set axis labels
        ax1.set_xlabel('Date', fontsize=10)
        ax1.set_ylabel('Overall Progress', fontsize=10)
        ax1.set_ylim([0, 100])


        y1 = [y2[0]]
        for i in range(1, len(y2)):
            difference = y2[i] - y2[i - 1]
            y1.append(difference)

        ax2.plot(x, y1, color='navy')
        ax2.scatter(x, y1, color='black', marker='o', s=10)


        ax2.xaxis.set_tick_params(rotation=90, labelsize=6)
        ax2.set_xlabel('Date', fontsize=10)
        ax2.set_ylabel('Daily Progress', fontsize=10)

        # -------------------------------------------------------------------------------

        y3 = np.array(self.exam_progress_details['Pomodoro'])
        print("x: ", x)
        print("y3: ",y3)
        ax3.plot(x, y3, color='darkgreen')
        ax3.scatter(x, y3, color='black', marker='o', s=10)
        ax3.xaxis.set_tick_params(rotation=90, labelsize=6)
        ax3.set_xlabel('Date', fontsize=10)
        ax3.set_ylabel('Pomo Sessions', fontsize=10)

        # ----------------------------------------------------------------------------------
        fig.tight_layout()

        # Get the current figure manager
        manager = plt.get_current_fig_manager()

        # Adjust the position and size of the plot window
        manager.window.setGeometry(150, 150, 1250, 600)

        plt.suptitle(f"Progress History for {exam_name}")

        plt.subplots_adjust(hspace=0.3, top=0.9)

        plt.show()

    def back_button_clicked(self):
        self.close()
        self.parent.show()

class DashboardScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        self.setParent(None)
        self.parent.hide()

        self.setWindowTitle("Dashboard")
        Geometry(self)

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.back_button_clicked)

        # Create progress bars
        math_progress = QProgressBar(self)
        math_progress.setValue(75)
        science_progress = QProgressBar(self)
        science_progress.setValue(60)
        english_progress = QProgressBar(self)
        english_progress.setValue(90)

        # Create a layout to arrange the progress bars
        layout = QGridLayout()
        layout.addWidget(QLabel("Math:"), 0, 0)
        layout.addWidget(math_progress, 0, 1)
        layout.addWidget(QLabel("Science:"), 1, 0)
        layout.addWidget(science_progress, 1, 1)
        layout.addWidget(QLabel("English:"), 2, 0)
        layout.addWidget(english_progress, 2, 1)
        layout.addWidget(back_button, 3, 0)

        # Set the layout for the screen
        self.setLayout(layout)
        self.show()

    def back_button_clicked(self):
        self.close()
        self.parent.show()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VLearn")
        Geometry(self) 

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.add_files_button = QPushButton("Add Content", self)
        self.add_files_button.clicked.connect(self.add_content_clicked)

        self.add_exam_button = QPushButton("Add Exam", self)
        self.add_exam_button.clicked.connect(self.add_exam_clicked)

        self.study_for_exam_button = QPushButton("Study for Exam", self)
        self.study_for_exam_button.clicked.connect(self.study_for_exam_clicked)

        self.progress_tracker_button = QPushButton("Progress Tracker", self)
        self.progress_tracker_button.clicked.connect(self.progress_tracker_clicked)

        layout = QVBoxLayout()

        title_label = QLabel("VLearn")
        title_label.setFixedHeight(50)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")

        layout.addWidget(title_label)
        layout.addWidget(self.add_files_button)
        layout.addWidget(self.add_exam_button)
        layout.addWidget(self.study_for_exam_button)
        layout.addWidget(self.progress_tracker_button)

        self.main_widget.setLayout(layout)
        self.show()

    def add_content_clicked(self):
        self.add_content_Screen = AddContentScreen(self)
        self.add_content_Screen.show()

    def add_exam_clicked(self):
        self.add_exam_screen = AddExamScreen(self)
        self.add_exam_screen.show()

    def study_for_exam_clicked(self):
        self.exam_list_screen = ExamListScreen(self)
        self.exam_list_screen.show()

    def dashboard_clicked(self):
        self.dashboard_screen = DashboardScreen(self)
        self.dashboard_screen.show()

    def progress_tracker_clicked(self):
        self.progress_tracker_screen= ProgressWidget(self)
        self.progress_tracker_screen.show()




class Geometry():
    def __init__(self, object):
        object.resize(window_width, window_height)
        screen_size = QScreen.availableGeometry(QApplication.primaryScreen())
        # Set X Position Center
        frmX = (screen_size.width() - object.width()) / 2
        # Set Y Position Center
        frmY = (screen_size.height() - object.height()) / 2
        # Set Form's Center Location
        object.move(frmX, frmY-100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    connection, cursor = connect()
    main_window = MainWindow()
    sys.exit(app.exec())