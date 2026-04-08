import psutil
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import QTimer
import numpy as np

class StatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cpu_history = [0] * 60
        self.mem_history = [0] * 60
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.cpu_label = QLabel("CPU: --%")
        self.mem_label = QLabel("Memory: --%")
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.cpu_label)
        top_layout.addWidget(self.mem_label)
        layout.addLayout(top_layout)

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Нагрузка за последние 60 секунд")
        self.ax.set_xlabel("секунды назад")
        self.ax.set_ylabel("использование %")
        self.ax.set_ylim(0, 100)
        self.cpu_line, = self.ax.plot([], [], label="CPU", color="#20B2AA")
        self.mem_line, = self.ax.plot([], [], label="Memory", color="#2F4F4F")
        self.ax.legend()

    def update_stats(self):
        cpu_percent = psutil.cpu_percent(interval=0.5)
        mem_percent = psutil.virtual_memory().percent
        self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
        self.mem_label.setText(f"Memory: {mem_percent:.1f}%")

        self.cpu_history.append(cpu_percent)
        self.mem_history.append(mem_percent)
        if len(self.cpu_history) > 60:
            self.cpu_history.pop(0)
            self.mem_history.pop(0)

        x = np.arange(len(self.cpu_history))
        self.cpu_line.set_data(x, self.cpu_history)
        self.mem_line.set_data(x, self.mem_history)
        self.ax.set_xlim(0, len(self.cpu_history) - 1)
        self.canvas.draw()