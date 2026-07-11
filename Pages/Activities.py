from PyQt6.QtWidgets import (QWidget, QPushButton, QScrollArea,
                             QVBoxLayout, QLabel, QRadioButton, QButtonGroup,
                             QHBoxLayout, QDialog, QDialogButtonBox, QGridLayout, QFrame, QLineEdit)
from PyQt6.QtCore import Qt
from Navigation.PageSelector import PageSelector
import qtawesome as qta
import json
from utils import resource_path

class Activities(QWidget):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.setLayout(QVBoxLayout())
        self.buildLayout()

    def buildLayout(self):
        #title
        page_label = QLabel("Activities")
        page_label.setStyleSheet("font-size: 40px; font-weight: bold;")

        #box layout
        box = QFrame()
        box.setFrameShape(QFrame.StyledPanel)
        box.setFrameShadow(QFrame.Raised) 
        box_layout = QVBoxLayout(box)

        #new button
        new_button = QPushButton(qta.icon('fa5s.plus'), "")
        new_button.clicked.connect(lambda : self.addActivity())
        new_button.setFixedSize(30, 30)

        #activities
        activity_widgets = []
        with open(resource_path('data.json')) as f:
            data = json.load(f)
            for activity in data["activity_list"]:
                activity_widgets.append(self.createActivityWidget(activity))

        #page selector
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        page_selector = PageSelector(self.mainWindow, 1) 

        #assign layout
        layout = self.layout()
        layout.addWidget(page_label, alignment=Qt.AlignTop | Qt.AlignCenter)
        layout.addWidget(new_button, alignment=Qt.AlignTop | Qt.AlignRight)
        layout.addSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        activity_container = QWidget()
        activity_layout = QVBoxLayout(activity_container)
        activity_layout.setAlignment(Qt.AlignTop)
        for widget in activity_widgets:
            activity_layout.addWidget(widget)
        scroll.setWidget(activity_container)
        box_layout.addWidget(scroll)

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

        min_max_text = "+ "
        if activity["min_max"] == "Minimize":
            min_max_text = "- "

        activity_name = QLabel(min_max_text + activity["name"])
        activity_name.setStyleSheet("font-size: 17px; border: none")
        activity_quantity = QLabel(str(activity["target"]) + "  " + activity["units"])
        activity_quantity.setStyleSheet("font-size: 17px; border: none")
        
        edit_button = QPushButton(qta.icon('fa5.edit'), "Edit")
        edit_button.clicked.connect(lambda : self.editClicked(activity_widget))
        delete_button = QPushButton(qta.icon('fa5.trash-alt'), "Delete")
        delete_button.clicked.connect(lambda : self.deleteClicked(activity_widget))
        
        activity_container.addWidget(activity_name)
        activity_container.addStretch()
        activity_container.addWidget(activity_quantity)
        activity_container.addStretch()
        activity_container.addWidget(edit_button)
        activity_container.addWidget(delete_button)
        activity_widget.setFixedHeight(40)

        return activity_widget

    def addActivity(self):
        with open(resource_path('data.json'), 'r+') as f:
            dlg = QDialog(self)
            dlg.setWindowTitle("Add an Activity")
            dlg.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            dlg.buttonBox.accepted.connect(dlg.accept)
            dlg.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)
            dlg.buttonBox.button(QDialogButtonBox.Ok).setAutoDefault(True)
            dlg.buttonBox.rejected.connect(dlg.reject)
            dlg_layout = QVBoxLayout()
            
            dlg_grid = QGridLayout()
            dlg_name = QLabel("Name:")
            new_name = QLineEdit()
            new_name.setMaximumHeight(35)
            dlg_quantity = QLabel("Quantity:")
            new_target_box = QLineEdit()
            new_target_box.setMaximumHeight(35)
            dlg_units = QLabel("Units:")
            new_units = QLineEdit()
            new_units.setMaximumHeight(35)

            radio_layout = QHBoxLayout()
            maximize_button = QRadioButton("Maximize")
            maximize_button.setChecked(True)
            minimize_button = QRadioButton("Minimize")
            radio_group = QButtonGroup()
            radio_group.addButton(maximize_button)
            radio_group.addButton(minimize_button)
            radio_layout.addWidget(maximize_button)
            radio_layout.addWidget(minimize_button)

            dlg_grid.addWidget(dlg_name, 1, 1)
            dlg_grid.addWidget(new_name, 1, 2)
            dlg_grid.addWidget(dlg_quantity, 2, 1)
            dlg_grid.addWidget(new_target_box, 2, 2)
            dlg_grid.addWidget(dlg_units, 3, 1)
            dlg_grid.addWidget(new_units, 3, 2)
            dlg_layout.addLayout(dlg_grid)
            dlg_layout.addLayout(radio_layout)
            dlg_layout.addWidget(dlg.buttonBox)
            dlg.setLayout(dlg_layout)
            if not dlg.exec(): return

            if new_name.text() == "": return
            try:
                new_target_text = new_target_box.text()
                new_target = float(new_target_text)
                if '.' not in new_target_text:
                    new_target = int(new_target_text)
            except Exception as e:
                print(e)
                return

            data = json.load(f)
            activity = {
                "name": new_name.text(),
                "units": new_units.text(),
                "target": new_target,
                "min_max": radio_group.checkedButton().text(),
                "current_quantity": 0,
                "total": 0,
                "start_date": data["date"],
                "days_tracked": 0,
                "historic_average_scores": [],
                "historic_daily_scores": []
            }
            data["activity_list"].append(activity)
            
            f.seek(0)
            data = json.dump(data, f, indent=4)
            f.truncate()

            self.clearLayout()
            self.buildLayout()

    def editClicked(self, activity_widget):
        name = activity_widget.children()[1].text().split()[1]
        with open(resource_path('data.json'), 'r+') as f:
            data = json.load(f)
            for i in range(len(data["activity_list"])):
                if data["activity_list"][i]["name"] == name:
                    quantity = str(data["activity_list"][i]["target"])
                    units = data["activity_list"][i]["units"]

                    dlg = QDialog(self)
                    dlg.setWindowTitle("Edit Activity")
                    dlg.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                    dlg.buttonBox.accepted.connect(dlg.accept)
                    dlg.buttonBox.rejected.connect(dlg.reject)
                    dlg_layout = QVBoxLayout()
                    
                    dlg_grid = QGridLayout()
                    dlg_name = QLabel("Name:")
                    new_name = QLineEdit(name)
                    new_name.setMaximumHeight(35)
                    dlg_quantity = QLabel("Quantity:")
                    new_target_box = QLineEdit(quantity)
                    new_target_box.setMaximumHeight(35)
                    dlg_units = QLabel("Units:")
                    new_units = QLineEdit(units)
                    new_units.setMaximumHeight(35)

                    radio_layout = QHBoxLayout()
                    maximize_button = QRadioButton("Maximize")
                    minimize_button = QRadioButton("Minimize")
                    if data["activity_list"][i]["min_max"] == "Maximize":
                        maximize_button.setChecked(True)
                    else:
                        minimize_button.setChecked(True)
                    radio_group = QButtonGroup()
                    radio_group.addButton(maximize_button)
                    radio_group.addButton(minimize_button)
                    radio_layout.addWidget(maximize_button)
                    radio_layout.addWidget(minimize_button)

                    dlg_grid.addWidget(dlg_name, 1, 1)
                    dlg_grid.addWidget(new_name, 1, 2)
                    dlg_grid.addWidget(dlg_quantity, 2, 1)
                    dlg_grid.addWidget(new_target_box, 2, 2)
                    dlg_grid.addWidget(dlg_units, 3, 1)
                    dlg_grid.addWidget(new_units, 3, 2)
                    dlg_layout.addLayout(dlg_grid)
                    dlg_layout.addLayout(radio_layout)

                    dlg_layout.addWidget(dlg.buttonBox)
                    dlg.setLayout(dlg_layout)
                    if not dlg.exec(): return

                    new_name_text = new_name.text()
                    new_units_text = new_units.text()
                    if new_name_text == "": new_name_text = name
                    if new_units_text == "": new_units_text = data["activity_list"][i]["units"]
                    data["activity_list"][i]["name"] = new_name_text
                    data["activity_list"][i]["units"] = new_units_text
                    data["activity_list"][i]["min_max"] = radio_group.checkedButton().text()

                    new_target_text = new_target_box.text()
                    try:
                        new_target = float(new_target_text)
                        if '.' not in new_target_text:
                            new_target = int(new_target_text)
                        data["activity_list"][i]["target"] = new_target
                    except Exception as e:
                        print(e)
                        pass

            f.seek(0)
            data = json.dump(data, f, indent=4)
            f.truncate()

            self.clearLayout()
            self.buildLayout()

    def deleteClicked(self, activity_widget):
        dlg = QDialog(self)
        dlg.setWindowTitle("Delete Activity")
        dlg.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dlg.buttonBox.accepted.connect(dlg.accept)
        dlg.buttonBox.rejected.connect(dlg.reject)
        dlg_layout = QVBoxLayout()
        dlg_message = QLabel("Are you sure you want to delete this activity?")
        dlg_layout.addWidget(dlg_message)
        dlg_layout.addWidget(dlg.buttonBox)
        dlg.setLayout(dlg_layout)
        if not dlg.exec(): return

        name = activity_widget.children()[1].text().split()[1]
        with open(resource_path('data.json'), 'r+') as f:
            data = json.load(f)
            for activity in data["activity_list"]:
                if activity["name"] == name: 
                    data["activity_list"].remove(activity)
            
            f.seek(0)
            data = json.dump(data, f, indent=4)
            f.truncate()

            self.clearLayout()
            self.buildLayout()
            