import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from gui.main_window import MainWindow
from gui.styles import MAIN_STYLE
import random

class WASP(QApplication):    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set random application name for process list
        self.setApplicationName(random.choice([
            "System Configuration",
            "Display Settings",
            "Volume Control",
            "Network Diagnostics"
            "Canva",
            "Adobe Photoshop 2025",
            "Adobe Acrobat Reader",
            "Visual Studio Code",
            "ChatGPT"
        ]))
        
        # Set random organization name
        self.setOrganizationName(random.choice([
            "Microsoft",
            "Apple",
            "Google",
            "Amazon",
            "Adobe",
            "Canva",
            "OpenAI",
        ]))
        self.setOrganizationDomain(random.choice([
            "microsoft.com",
            "apple.com",
            "google.com",
            "amazon.com",
            "adobe.com",
            "canva.com",
            "openai.com",
        ]))
        
    def event(self, event):
        # Hide to tray on Escape key
        if (event.type() == event.Type.KeyPress and 
            event.key() == Qt.Key.Key_Escape):
            for window in self.topLevelWindows():
                if isinstance(window, MainWindow):
                    window.hide_to_tray()
            return True
        return super().event(event)

def main():
    app = WASP(sys.argv)
    app.setStyleSheet(MAIN_STYLE)
    
    # Set application icon
    try:
        app.setWindowIcon(QIcon("icon.ico"))
    except:
        pass 
    
    window = MainWindow(app)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()