import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QLabel, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from server_controller import ServerController
from test_runner import TestRunner
from stats_widget import StatsWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fullstack Launcher")
        self.resize(1200, 800)
        
        self.server_controller = ServerController()
        self.test_runner = TestRunner()
        self.stats_widget = StatsWidget()
        
        self.setup_ui()
        self.apply_styles()
        self.init_connections()
        
        self.status_update_timer = QTimer()
        self.status_update_timer.timeout.connect(self.update_status)
        self.status_update_timer.start(1000)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.control_tab = QWidget()
        self.tabs.addTab(self.control_tab, "Управление")
        control_layout = QVBoxLayout(self.control_tab)

        self.run_button = QPushButton("▶")
        self.run_button.setFixedSize(120, 120)
        self.run_button.setCheckable(True)
        self.run_button.setStyleSheet("border-radius: 60px; font-size: 36px;")
        control_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Сервер не запущен")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.status_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        control_layout.addWidget(self.log_output)

        self.tabs.addTab(self.stats_widget, "Статистика и графики")

        self.tests_tab = QWidget()
        self.tabs.addTab(self.tests_tab, "Тесты")
        tests_layout = QVBoxLayout(self.tests_tab)

        self.run_backend_tests_btn = QPushButton("Запустить тесты бэкенда")
        self.run_frontend_tests_btn = QPushButton("Запустить тесты фронтенда")
        tests_layout.addWidget(self.run_backend_tests_btn)
        tests_layout.addWidget(self.run_frontend_tests_btn)

        self.tests_output = QTextEdit()
        self.tests_output.setReadOnly(True)
        tests_layout.addWidget(self.tests_output)

        self.progress_bar = QProgressBar()
        tests_layout.addWidget(self.progress_bar)

    def apply_styles(self):
        style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

    def init_connections(self):
        self.run_button.toggled.connect(self.on_run_toggled)
        self.run_backend_tests_btn.clicked.connect(self.run_backend_tests)
        self.run_frontend_tests_btn.clicked.connect(self.run_frontend_tests)
        self.server_controller.output_signal.connect(self.append_log)
        self.server_controller.status_signal.connect(self.update_server_status)
        self.test_runner.output_signal.connect(self.append_test_output)
        self.test_runner.finished_signal.connect(self.tests_finished)

    def on_run_toggled(self, checked):
        if checked:
            self.server_controller.start_all()
            self.run_button.setText("⏸")
        else:
            self.server_controller.stop_all()
            self.run_button.setText("▶")

    def append_log(self, text):
        self.log_output.append(text)

    def update_server_status(self, status):
        self.status_label.setText(status)

    def update_status(self):
        self.stats_widget.update_stats()

    def run_backend_tests(self):
        self.tests_output.clear()
        self.progress_bar.setValue(0)
        self.test_runner.run_backend_tests()

    def run_frontend_tests(self):
        self.tests_output.clear()
        self.progress_bar.setValue(0)
        self.test_runner.run_frontend_tests()

    def append_test_output(self, text):
        self.tests_output.append(text)

    def tests_finished(self, success):
        self.progress_bar.setValue(100)
        if success:
            self.tests_output.append("✅ Все тесты завершены успешно")
        else:
            self.tests_output.append("❌ Некоторые тесты завершились с ошибками")