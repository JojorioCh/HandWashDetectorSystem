import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel, QSlider
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPalette, QColor, QFont
import firebase_admin
from firebase_admin import credentials, db
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def GetDataFromFirebase(JSON_DB_File:str="database-of-hwd-durations-firebase-adminsdk-d3yd8-a4a0833a8f.json",
                        ProjectID:str = "database-of-hwd-durations",
                        databaseURL:str = "database-of-hwd-durations.firebaseapp.com"):
    cred = credentials.Certificate(JSON_DB_File)
    Config = {
    "apiKey": "AIzaSyCHD9raTlgFp-OT64UP3wV-oIU-pXLAd54",
    "authDomain": databaseURL,
    "databaseURL": "https://database-of-hwd-durations-default-rtdb.firebaseio.com",
    "projectId": ProjectID,
    "storageBucket": "database-of-hwd-durations.appspot.com",
    "messagingSenderId": "359816228479",
    "appId": "1:359816228479:web:7606ca596bbb4678c2594a",
    "measurementId": "G-ZYKYSKCF8X"
    }

    firebase_admin.initialize_app(cred, Config)
    ref = db.reference("/")
    data = ref.get()
    df = pd.DataFrame(data)
    df = df.rename_axis('Time').reset_index()
    df.sort_values(by='Time', inplace=True)
    return df

class DataFrameViewer(QMainWindow):
    def __init__(self, dataframe):
        super().__init__()

        self.dataframe = dataframe
        self.filtered_dataframe = dataframe

        self.setWindowTitle("Database of Recorded Detections of Hand Washing")
        self.setGeometry(100, 100, 800, 400)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Set the application icon (logo)
        icon = QIcon("Logo.png")  # Replace "icon.png" with the path to your icon image
        self.setWindowIcon(icon)

        # # Create a Matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        # self.layout.addWidget(self.canvas)

        # Create a range slider and labels
        self.slider = QSlider()
        self.slider.setOrientation(1)  # Set the orientation to horizontal
        self.layout.addWidget(self.slider)

        self.range_label = QLabel("Selected Range of Plots: 0 - 100 (to avoid multiple data)")
        self.layout.addWidget(self.range_label)
        self.range_label.setStyleSheet("font-weight: bold;")

        # Create a button to trigger the plot
        self.plot_button = QPushButton("Plot your Data to See The Analysis", self)
        self.layout.addWidget(self.plot_button)
        self.plot_button.clicked.connect(self.plot_custom)
        self.plot_button.setStyleSheet("QPushButton { background-color: red; color: yellow; font-weight: bold;}"
                                        "QPushButton:hover { background-color: darkred; }")

        # Set the range slider values and labels
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setTickPosition(1)
        self.slider.setTickInterval(10)

        self.slider.valueChanged.connect(self.update_range_label)

        self.search_entry = QLineEdit(self)
        self.search_entry.setPlaceholderText("Search...")
        self.layout.addWidget(self.search_entry)
        self.search_entry.setStyleSheet("background-color: white; color: green; font-weight:bold;")

        self.search_button = QPushButton("Search (e.g. search for time 21:58)", self)
        self.search_button.clicked.connect(self.search)
        self.layout.addWidget(self.search_button)
        self.search_button.setStyleSheet("QPushButton { background-color: red; color: yellow; font-weight: bold;}"
                                        "QPushButton:hover { background-color: darkred; }")

        self.reset_button = QPushButton("Reset (reset the table as in the beginning form)", self)
        self.reset_button.clicked.connect(self.reset_data)
        self.layout.addWidget(self.reset_button)
        self.reset_button.setStyleSheet("QPushButton { background-color: red; color: yellow; font-weight: bold;}"
                                        "QPushButton:hover { background-color: darkred; }")

         # Set the background color of the central widget
        self.central_widget.setStyleSheet("background-color: darkgray")
        self.table = QTableWidget(self)

        self.layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(len(self.dataframe))
        self.table.setColumnCount(len(self.dataframe.columns))
        self.table.setHorizontalHeaderLabels(self.dataframe.columns)

        # Set headers
        for col, header in enumerate(self.dataframe.columns):
            item = QTableWidgetItem(header)
            self.table.setHorizontalHeaderItem(col, item)
        # Apply custom CSS style to change header background color
        self.table.horizontalHeader().setStyleSheet("color: darkblue; font-weight: bold;")

        for row in range(len(self.dataframe)):
            for col in range(len(self.dataframe.columns)):
                item = QTableWidgetItem(str(self.dataframe.iloc[row, col]))  
                item.setBackground(QColor(255, 0, 0))  # Set the background color to red
                font = QFont()
                font.setBold(True)  # Make the font bold
                font_color = QColor(0, 255, 0)  # Set font color to red
                item.setFont(font)
                item.setForeground(font_color)
                self.table.setItem(row, col, item)

    def search(self):
        query = self.search_entry.text().strip()
        if query:
            self.filtered_dataframe = self.dataframe[self.dataframe.apply(lambda row: any(query.lower() in str(cell).lower() for cell in row), axis=1)]
            self.load_filtered_data()
        else:
            self.filtered_dataframe = self.dataframe
            self.load_filtered_data()

    def reset_data(self):
        self.search_entry.clear()
        self.filtered_dataframe = self.dataframe
        self.load_filtered_data()

    def load_filtered_data(self):
        self.table.setRowCount(len(self.filtered_dataframe))
        self.table.setColumnCount(len(self.filtered_dataframe.columns))
        self.table.setHorizontalHeaderLabels(self.filtered_dataframe.columns)

        for row in range(len(self.filtered_dataframe)):
            for col in range(len(self.filtered_dataframe.columns)):
                item = QTableWidgetItem(str(self.filtered_dataframe.iloc[row, col]))
                self.table.setItem(row, col, item)
    
    def update_range_label(self):
        selected_range = self.slider.value()
        self.range_label.setText(f"Selected Number of Days to be shown: {selected_range} Day(s), starting from {self.dataframe.columns[1]}")

    def plot_custom(self):
        df = self.dataframe
        df_new = df.groupby("Time").sum()
        range = self.slider.value()
        if range != 0 :
            df_new = df_new[df_new.columns[:range]]

        plt.grid()
        sns.scatterplot(df_new)
        plt.xlabel("Time in Day (Hours : Minutes)")
        plt.ylabel("How much it appears")
        plt.show()
        self.canvas.draw()

if __name__ == "__main__":
    df = GetDataFromFirebase()
    app = QApplication(sys.argv)
    window = DataFrameViewer(df)
    window.show()
    sys.exit(app.exec_())
