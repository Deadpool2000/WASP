from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QHBoxLayout, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QFont
import platform
import json
import urllib.request
import os
import sys
from core import VERSION

class UpdateChecker(QThread):
    finished = pyqtSignal(dict)
    def run(self):
        try:
            url = "https://api.github.com/repos/Deadpool2000/WASP/releases/latest"
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    self.finished.emit({"success": True, "data": data})
                else:
                    self.finished.emit({"success": False, "error": f"Status code: {response.status}"})
        except Exception as e:
            self.finished.emit({"success": False, "error": str(e)})

class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        header_layout = QVBoxLayout()
        title = QLabel("WASP")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #3daee9;")
        header_layout.addWidget(title)
        subtitle = QLabel("Workplace Activity Simulation Program")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #aaaaaa; font-style: italic;")
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)

        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
            QLabel {
                padding: 5px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        def add_info_row(label_text, value_text, is_link=False):
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("color: #888888; font-weight: bold;")
            
            if is_link:
                value = QLabel(f'<a href="{value_text}" style="color: #3daee9; text-decoration: none;">{value_text}</a>')
                value.setOpenExternalLinks(True)
            else:
                value = QLabel(value_text)
                value.setStyleSheet("color: #ffffff;")
                
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            row.addWidget(label)
            row.addWidget(value)
            info_layout.addLayout(row)
        add_info_row("Version:", f"v{VERSION}")
        add_info_row("Author:", "Deadpool2000")
        add_info_row("OS:", f"{platform.system()} {platform.release()}")
        add_info_row("GitHub:", "https://github.com/Deadpool2000/WASP", is_link=True)
        layout.addWidget(info_frame)

        self.check_btn = QPushButton("Check for Updates")
        self.check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_btn.clicked.connect(self.check_updates)
        layout.addWidget(self.check_btn)

        license_label = QLabel("License")
        license_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(license_label)

        self.license_text = QTextEdit()
        self.license_text.setReadOnly(True)
        self.license_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 8pt;
                color: #cccccc;
            }
        """)
        try:
            license_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "LICENSE")
            if os.path.exists(license_path):
                with open(license_path, "r", encoding="utf-8") as f:
                    self.license_text.setText(f.read())
            else:
                self.license_text.setText("License file not found.")
        except Exception as e:
            self.license_text.setText(f"Error loading license: {str(e)}")
            
        layout.addWidget(self.license_text)

    def check_updates(self):
        self.check_btn.setText("Checking...")
        self.check_btn.setEnabled(False)
        self.checker = UpdateChecker()
        self.checker.finished.connect(self.on_check_finished)
        self.checker.start()

    def on_check_finished(self, result):
        self.check_btn.setEnabled(True)
        self.check_btn.setText("Check for Updates")
        
        if result["success"]:
            data = result["data"]
            latest_tag = data.get("tag_name", "").lstrip('v')
            current_version = VERSION.lstrip('v')
            if latest_tag and latest_tag != current_version:
                reply = QMessageBox.question(
                    self, 
                    "Update Available", 
                    f"A new version ({latest_tag}) is available.\n\nDo you want to visit the download page?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    QDesktopServices.openUrl(QUrl(data.get("html_url", "")))
            else:
                QMessageBox.information(self, "Up to Date", f"You are running the latest version (v{VERSION}).")
        else:
            QMessageBox.warning(self, "Check Failed", f"Could not check for updates.\nError: {result.get('error')}")
