import os
import subprocess
from PyQt6.QtCore import QObject, QProcess, pyqtSignal

class TestRunner(QObject):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.current_process = None
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def run_backend_tests(self):
        backend_dir = os.path.join(self.project_root, "backend")
        self.current_process = QProcess()
        self.current_process.setWorkingDirectory(backend_dir)
        self.current_process.readyReadStandardOutput.connect(self.handle_output)
        self.current_process.readyReadStandardError.connect(self.handle_error)
        self.current_process.finished.connect(self.process_finished)
        self.current_process.start("pytest", ["-v", "tests/"])
        if not self.current_process.waitForStarted():
            self.output_signal.emit("Ошибка запуска pytest")

    def run_frontend_tests(self):
        frontend_dir = os.path.join(self.project_root, "frontend")
        self.current_process = QProcess()
        self.current_process.setWorkingDirectory(frontend_dir)
        self.current_process.readyReadStandardOutput.connect(self.handle_output)
        self.current_process.readyReadStandardError.connect(self.handle_error)
        self.current_process.finished.connect(self.process_finished)
        self.current_process.start("npm", ["run", "test:unit", "--", "--run"])
        if not self.current_process.waitForStarted():
            self.output_signal.emit("Ошибка запуска frontend тестов (vitest)")

    def handle_output(self):
        data = self.current_process.readAllStandardOutput().data().decode()
        for line in data.splitlines():
            self.output_signal.emit(line)

    def handle_error(self):
        data = self.current_process.readAllStandardError().data().decode()
        for line in data.splitlines():
            self.output_signal.emit(f"ERR: {line}")

    def process_finished(self, exit_code, exit_status):
        success = (exit_code == 0)
        self.finished_signal.emit(success)
        self.current_process = None