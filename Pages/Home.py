from PyQt6.QtWidgets import (QWidget, QPushButton, 
                             QVBoxLayout, QLabel, QGroupBox, QScrollArea,
                             QLineEdit, QHBoxLayout, QComboBox, QFrame, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt
from Navigation.PageSelector import PageSelector
import json
from datetime import datetime
from datetime import date, timedelta
from utils import resource_path, load_data
from PyQt6.QtGui import QKeySequence

class Home(QWidget):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.setLayout(QVBoxLayout())
        self.buildLayout()

    def buildLayout(self):
        #make sure we have correct score
        self.updateScore()

        with open(resource_path('data.json'), 'r') as f:
            data = json.load(f)
            activeActivities = [activity for activity in data["activity_list"] if activity["active"]]

            #title
            page_label = QLabel("Home")
            page_label.setStyleSheet("font-size: 40px; font-weight: bold;")

            #reset button
            reset_button = QPushButton("Reset")
            reset_button.clicked.connect(lambda : self.reset())
            reset_button.setFixedSize(65, 30)
            reset_button.setStyleSheet("font-size: 15px; font-weight: bold; background-color: red")

            #date label
            date_label = QLabel(data["date"])
            date_label.setStyleSheet("font-size: 15px")

            #percentage
            percent_label = QLabel(str(data["score"]) + "%")
            color = "red" if data["score"] < 40 else "yellow" if data["score"] < 80 else "green"
            percent_label.setStyleSheet(f"font-size: 25px; font-weight: bold; border: 4px solid {color}")

            #activities
            box = QFrame()
            box.setFrameShape(QFrame.StyledPanel)
            box.setFrameShadow(QFrame.Raised) 
            box_layout = QVBoxLayout(box)
            
            activity_label = QLabel("Current Day")
            activity_label.setStyleSheet("font-size: 20px; font-weight: bold")

            activity_widgets = []
            for activity in activeActivities:
                activity_widget = self.createActivityWidget(activity)
                activity_widgets.append(activity_widget)

            #report 
            report_container = QWidget()
            report_container.setLayout(QHBoxLayout())

            report_label = QLabel("Report an Activity")
            report_label.setStyleSheet("font-size: 20px; font-weight: bold")
            report_dropdown = QComboBox()
            for activity in activeActivities:
                report_dropdown.addItem(activity["name"])
            report_quantity = QLineEdit()
            report_quantity.setFixedSize(100, 32)

            report_container.layout().addWidget(report_dropdown)
            report_container.layout().addSpacing(50)
            report_container.layout().addWidget(report_quantity)
            report_container.layout().addSpacing(25)

            report_button = QPushButton("Submit")
            report_button.clicked.connect(lambda : self.reportActivity(report_container))
            report_button.setFixedSize(55, 30)
            report_button.setShortcut(QKeySequence("Return"))

            #page selector
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            page_selector = PageSelector(self.mainWindow, 0)

            #assign layouts
            layout = self.layout()
            layout.addWidget(reset_button, alignment=Qt.AlignTop | Qt.AlignRight)
            layout.addWidget(page_label, alignment=Qt.AlignTop | Qt.AlignCenter)

            box_layout.addWidget(date_label, alignment=Qt.AlignCenter)
            box_layout.addWidget(percent_label, alignment=Qt.AlignCenter)
            box_layout.addSpacing(35)

            box_layout.addWidget(activity_label, alignment=Qt.AlignCenter)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            activity_container = QWidget()
            activity_layout = QVBoxLayout(activity_container)
            for widget in activity_widgets:
                activity_layout.addWidget(widget)
            scroll.setWidget(activity_container)
            box_layout.addWidget(scroll)
            box_layout.addStretch()

            box_layout.addWidget(report_label, alignment=Qt.AlignCenter)
            box_layout.addWidget(report_container)
            box_layout.addWidget(report_button, alignment=Qt.AlignCenter)
            box_layout.addStretch()

            layout.addWidget(box)
            layout.addWidget(line)
            layout.addWidget(page_selector, alignment=Qt.AlignBottom) 

    def clearLayout(self):
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def createActivityWidget(self, activity):
        activity_widget = QWidget()
        activity_widget.setStyleSheet("border: 1px solid white")
        activity_container = QHBoxLayout(activity_widget)
        activity_container.setContentsMargins(4, 4, 4, 4)

        daily_target = activity["target"]
        if activity["timeline"] == "Weekly":
            current_date = datetime.strptime(activity["start_date"], "%A, %m-%d-%Y") + timedelta(days=activity["days_tracked"])
            daily_target = (activity["target"] - activity["weekly_total"]) / (7 - current_date.weekday())
        elif activity["timeline"] == "By Date":
            current_date = datetime.strptime(activity["start_date"], "%A, %m-%d-%Y") + timedelta(days=activity["days_tracked"])
            due_date = datetime.strptime(activity["due_date"], "%A, %m-%d-%Y")
            days_left = (due_date - current_date).days + 1
            daily_target = (activity["target"] - activity["total"]) / days_left

        check_text = "\u2714"
        min_max_text = "+ "
        if activity["min_max"] == "Maximize":
            if activity["current_quantity"] < daily_target:
                check_text = ""
        else:
            min_max_text = "- "
            if activity["current_quantity"] > daily_target:
                check_text = ""

        activity_name = QLabel(min_max_text + activity["name"])
        activity_name.setStyleSheet("font-size: 17px; border: none")
        activity_quantity = QLabel(f"{activity["current_quantity"]:.2f} / {daily_target:.2f}    {activity["units"]}")
        activity_quantity.setStyleSheet("font-size: 17px; border: none")
        activity_check = QLabel(check_text)
        activity_check.setStyleSheet("font-size: 17px; border: none")

        activity_container.addWidget(activity_name)
        activity_container.addStretch()
        activity_container.addWidget(activity_quantity)
        activity_container.addStretch()
        activity_container.addWidget(activity_check)
        activity_widget.setFixedHeight(40)

        return activity_widget

    def reset(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Reset History")
        dlg.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dlg.buttonBox.accepted.connect(dlg.accept)
        dlg.buttonBox.rejected.connect(dlg.reject)
        dlg_layout = QVBoxLayout()
        dlg_message = QLabel("Are you sure you want to reset your history?")
        dlg_layout.addWidget(dlg_message)
        dlg_layout.addWidget(dlg.buttonBox)
        dlg.setLayout(dlg_layout)
        if not dlg.exec(): return

        load_data(reset=True)
        self.clearLayout()
        self.buildLayout()

    def updateScore(self):
        TOTAL_POINTS = 1000
        FLEX = 0.35

        with open(resource_path('data.json'), 'r+') as f:
            data = json.load(f)
            activeActivities = [activity for activity in data["activity_list"] if activity["active"]]

            #sum diff
            sum = 0
            for activity in activeActivities:
                daily_total = activity["total"]
                
                daily_target = activity["target"]
                if activity["timeline"] == "Weekly":
                    daily_total = daily_total / 7
                    current_date = datetime.strptime(activity["start_date"], "%A, %m-%d-%Y") + timedelta(days=activity["days_tracked"])
                    daily_target = (activity["target"] - activity["weekly_total"]) / (7 - current_date.weekday())
                elif activity["timeline"] == "By Date":
                    current_date = datetime.strptime(activity["start_date"], "%A, %m-%d-%Y") + timedelta(days=activity["days_tracked"])
                    due_date = datetime.strptime(activity["due_date"], "%A, %m-%d-%Y")
                    start_date= datetime.strptime(activity["start_date"], "%A, %m-%d-%Y")
                    total_days = (due_date - start_date).days + 1
                    days_left = (due_date - current_date).days + 1
                    daily_total = daily_total / total_days
                    daily_target = (activity["target"] - activity["total"]) / days_left

                avg = daily_total / (activity["days_tracked"] if activity["days_tracked"] != 0 else 1)

                diff = 0 
                if activity["min_max"] == "Maximize":
                    diff = (daily_target - avg) / daily_target
                else:
                    diff = (avg - daily_target) / daily_target
                if diff > 0: sum += diff #positive diff means we have room for improvement

            #point distribution
            current_points = 0
            for activity in activeActivities:
                possible_points = 0

                daily_total = activity["total"]
                
                daily_target = activity["target"]
                if activity["timeline"] == "Weekly":
                    daily_total = daily_total / 7
                    current_date = datetime.strptime(activity["start_date"], "%A, %m-%d-%Y") + timedelta(days=activity["days_tracked"])
                    daily_target = (activity["target"] - activity["weekly_total"]) / (7 - current_date.weekday())
                elif activity["timeline"] == "By Date":
                    current_date = datetime.strptime(activity["start_date"], "%A, %m-%d-%Y") + timedelta(days=activity["days_tracked"])
                    due_date = datetime.strptime(activity["due_date"], "%A, %m-%d-%Y")
                    start_date= datetime.strptime(activity["start_date"], "%A, %m-%d-%Y")
                    total_days = (due_date - start_date).days + 1
                    days_left = (due_date - current_date).days + 1
                    daily_total = daily_total / total_days
                    daily_target = (activity["target"] - activity["total"]) / days_left

                if sum != 0:
                    static_points = (1-FLEX) * TOTAL_POINTS / len(activeActivities)
                    avg = daily_total / (activity["days_tracked"] if activity["days_tracked"] != 0 else 1)
                    diff = 0 
                    if activity["min_max"] == "Maximize":
                        diff = (daily_target - avg) / daily_target
                    else:
                        diff = (avg - daily_target) / daily_target
                    if diff < 0: diff = 0
                    flex_points = FLEX * TOTAL_POINTS * diff / sum
                    possible_points = static_points + flex_points
                else: #uniform distribution
                    possible_points = TOTAL_POINTS / len(activeActivities)
                #calculate points
                if activity["min_max"] == "Maximize":
                    if activity["current_quantity"] <= daily_target:
                        current_points += possible_points * activity["current_quantity"] / daily_target #linear growth
                    else:
                        current_points += possible_points * (activity["current_quantity"] / daily_target)**0.5 #sqrt cramp
                else:
                    if activity["current_quantity"] <= daily_target:
                        current_points += possible_points #flat line
                    else:
                        current_points += -(possible_points) * activity["current_quantity"] / daily_target + 2 * possible_points #linear decline

            score = int(float(current_points) / TOTAL_POINTS * 100)
            data["score"] = score

            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def reportActivity(self, report_container):
        try:
            name = report_container.children()[1].currentText()
            quantity_text = report_container.children()[2].text()
            quantity = float(quantity_text)
            if '.' not in quantity_text:
                quantity = int(quantity_text)
        except Exception as e:
            print(e)
            return

        with open(resource_path('data.json'), 'r+') as f:
            data = json.load(f)

            for i in range(len(data["activity_list"])):
                if data["activity_list"][i]["name"] == name:
                    data["activity_list"][i]["current_quantity"] += quantity
            
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

            self.clearLayout()
            self.buildLayout()