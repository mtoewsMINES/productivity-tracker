from PyQt6.QtWidgets import (QWidget, QPushButton, QScrollArea,
                             QVBoxLayout, QLabel, QHBoxLayout, QStackedWidget, QFrame)
from PyQt6.QtCore import Qt
from Navigation.PageSelector import PageSelector
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import qtawesome as qta
import json
from datetime import datetime
from datetime import date, timedelta
import matplotlib.dates as mdates
from utils import resource_path

class Stats(QWidget):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.setLayout(QVBoxLayout())
        self.buildLayout()

    def buildLayout(self):
        #title
        page_label = QLabel("Stats")
        page_label.setStyleSheet("font-size: 40px; font-weight: bold;")

        #box layout
        box = QFrame()
        box.setFrameShape(QFrame.StyledPanel)
        box.setFrameShadow(QFrame.Raised) 
        box_layout = QVBoxLayout(box)

        #activities
        activity_label = QLabel("Lifetime Stats")
        activity_label.setStyleSheet("font-size: 20px; font-weight: bold")
        self.graphs = QStackedWidget()
        self.graphs.setFixedHeight(350)

        activity_widgets = []
        with open(resource_path('data.json'), 'r') as f:
            data = json.load(f)

            for activity in data["activity_list"]:
                activity_widget = self.createActivityWidget(activity)
                activity_widgets.append(activity_widget)

            #graphs
            dates = [datetime.strptime(data["start_date"], "%A, %m-%d-%Y") + timedelta(days=i) for i in range(len(data["historic_scores"]))]

            score_graph = QWidget()
            graph_container = QVBoxLayout(score_graph)

            fig = Figure()
            ax = fig.add_subplot()
            ax.plot(dates, data["historic_scores"], label="Daily")
            ax.plot(dates, data["historic_averages"], label="Average")
            ax.axhline(y=100, color='red', linestyle='--', linewidth=2, label='Target')
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(0, 1.0),
                borderaxespad=0
            )
            ax.set_title("Score")
            ax.set_ylabel("Percent", fontsize=14)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%Y"))
            fig.autofmt_xdate()
            fig.subplots_adjust(
                left=0.2,
                right=0.9,
                bottom=0.3,
                top=0.9
            )

            canvas = FigureCanvasQTAgg(fig)
            toolbar = NavigationToolbar2QT(canvas, self)
            graph_container.addWidget(canvas)
            graph_container.addWidget(toolbar)
            self.graphs.addWidget(score_graph)

            for activity in data["activity_list"]:
                dates = [datetime.strptime(activity["start_date"], "%A, %m-%d-%Y") + timedelta(days=i) for i in range(len(activity["historic_average_scores"]))]
                activity_graph = self.createGraph(dates, activity)
                self.graphs.addWidget(activity_graph)

        left_button = QPushButton(qta.icon('fa5s.arrow-circle-left'), '')
        left_button.setFixedSize(40, 25)
        left_button.clicked.connect(lambda : self.leftClicked())
        right_button = QPushButton(qta.icon('fa5s.arrow-circle-right'), '')
        right_button.setFixedSize(40, 25)
        right_button.clicked.connect(lambda : self.rightClicked())

        graph_nav = QWidget()
        graph_nav.setLayout(QHBoxLayout())
        graph_nav.layout().addWidget(left_button)
        graph_nav.layout().addStretch()
        graph_nav.layout().addWidget(right_button)

        #page selector
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        page_selector = PageSelector(self.mainWindow, 2) 

        #assign layout
        layout = self.layout()
        layout.addWidget(page_label, alignment=Qt.AlignTop | Qt.AlignCenter)

        box_layout.addWidget(activity_label, alignment=Qt.AlignCenter)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        activity_container = QWidget()
        activity_layout = QVBoxLayout(activity_container)
        for widget in activity_widgets:
            activity_layout.addWidget(widget)
        scroll.setWidget(activity_container)
        box_layout.addWidget(scroll)

        box_layout.addWidget(self.graphs)
        box_layout.addWidget(graph_nav)
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

        check_text = "\u2714"
        min_max_text = "+ "
        if activity["min_max"] == "Maximize":
            if activity["total"] / (activity["days_tracked"] if activity["days_tracked"] != 0 else 1) < activity["target"]:
                check_text = ""
        else:
            min_max_text = "- "
            if activity["total"] / (activity["days_tracked"] if activity["days_tracked"] != 0 else 1) > activity["target"]:
                check_text = ""

        activity_name = QLabel(min_max_text + activity["name"])
        activity_name.setStyleSheet("font-size: 17px; border: none")
        activity_total = QLabel(str(activity["total"]))
        activity_total.setStyleSheet("font-size: 17px; border: none")
        avg = activity["total"] / (activity["days_tracked"] if activity["days_tracked"] != 0 else 1)
        activity_quantity = QLabel(f"{avg:.2f} / {activity["target"]:.2f}")
        activity_quantity.setStyleSheet("font-size: 17px; border: none")
        activity_check = QLabel(check_text)
        activity_check.setStyleSheet("font-size: 17px; border: none")
        
        activity_container.addWidget(activity_name)
        activity_container.addStretch()
        activity_container.addWidget(activity_total)
        activity_container.addStretch()
        activity_container.addWidget(activity_quantity)
        activity_container.addStretch()
        activity_container.addWidget(activity_check)
        activity_widget.setFixedHeight(40)

        return activity_widget

    def createGraph(self, x, activity):
        graph_widget = QWidget()
        graph_container = QVBoxLayout(graph_widget)

        fig = Figure()
        ax = fig.add_subplot()
        ax.plot(x, activity["historic_daily_scores"], label="Daily")
        ax.plot(x, activity["historic_average_scores"], label="Average")
        ax.axhline(y=activity["target"], color='red', linestyle='--', linewidth=2, label='Target')
        ax.legend(
            loc="upper left",
            bbox_to_anchor=(0, 1.0),
            borderaxespad=0
        )
        ax.set_title(activity["name"])
        ax.set_ylabel(activity["units"], fontsize=14)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%Y"))
        fig.autofmt_xdate()
        fig.subplots_adjust(
            left=0.2,
            right=0.9,
            bottom=0.3,
            top=0.9
        )

        canvas = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar2QT(canvas, self)
        graph_container.addWidget(canvas)
        graph_container.addWidget(toolbar)

        return graph_widget

    def leftClicked(self):
        self.graphs.setCurrentIndex(self.graphs.currentIndex() - 1)

    def rightClicked(self):
        self.graphs.setCurrentIndex(self.graphs.currentIndex() + 1)