import os
import subprocess
import signal
import sys
from PyQt6.QtCore import QObject, QProcess, pyqtSignal

class ServerController(QObject):
    output_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.backend_process = None
        self.frontend_process = None
        self.docker_process = None
        self.running = False
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def start_all(self):
        if self.running:
            return
        self.status_signal.emit("Запуск серверов...")
        self.start_docker()
        self.start_frontend()
        self.running = True
        self.status_signal.emit("Серверы запущены")

    def stop_all(self):
        if not self.running:
            return
        self.status_signal.emit("Остановка серверов...")
        self.stop_docker()
        self.stop_frontend()
        self.running = False
        self.status_signal.emit("Серверы остановлены")

    def start_docker(self):
        backend_dir = os.path.join(self.project_root, "backend")
        self.docker_process = QProcess()
        self.docker_process.setWorkingDirectory(backend_dir)
        self.docker_process.readyReadStandardOutput.connect(self.handle_docker_output)
        self.docker_process.readyReadStandardError.connect(self.handle_docker_error)
        self.docker_process.start("docker-compose", ["up"])
        if not self.docker_process.waitForStarted():
            self.output_signal.emit("Ошибка запуска Docker Compose")

    def handle_docker_output(self):
        data = self.docker_process.readAllStandardOutput().data().decode()
        for line in data.splitlines():
            self.output_signal.emit(f"[Docker] {line}")

    def handle_docker_error(self):
        data = self.docker_process.readAllStandardError().data().decode()
        for line in data.splitlines():
            self.output_signal.emit(f"[Docker ERR] {line}")

    def stop_docker(self):
        if self.docker_process and self.docker_process.state() == QProcess.ProcessState.Running:
            backend_dir = os.path.join(self.project_root, "backend")
            stop_proc = QProcess()
            stop_proc.setWorkingDirectory(backend_dir)
            stop_proc.start("docker-compose", ["down"])
            stop_proc.waitForFinished()
            self.docker_process.terminate()
            self.docker_process.waitForFinished(5000)
            self.output_signal.emit("Docker контейнеры остановлены")

    def start_frontend(self):
        frontend_dir = os.path.join(self.project_root, "frontend")
        self.frontend_process = QProcess()
        self.frontend_process.setWorkingDirectory(frontend_dir)
        self.frontend_process.readyReadStandardOutput.connect(self.handle_frontend_output)
        self.frontend_process.readyReadStandardError.connect(self.handle_frontend_error)
        self.frontend_process.start("npm", ["run", "dev"])
        if not self.frontend_process.waitForStarted():
            self.output_signal.emit("Ошибка запуска frontend (npm run dev)")

    def handle_frontend_output(self):
        data = self.frontend_process.readAllStandardOutput().data().decode()
        for line in data.splitlines():
            self.output_signal.emit(f"[Frontend] {line}")

    def handle_frontend_error(self):
        data = self.frontend_process.readAllStandardError().data().decode()
        for line in data.splitlines():
            self.output_signal.emit(f"[Frontend ERR] {line}")

    def stop_frontend(self):
        if self.frontend_process and self.frontend_process.state() == QProcess.ProcessState.Running:
            self.frontend_process.terminate()
            self.frontend_process.waitForFinished(5000)
            self.output_signal.emit("Frontend процесс остановлен")