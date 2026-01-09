from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSpinBox, QGroupBox, 
                             QDoubleSpinBox, QTimeEdit, QCheckBox, QTextEdit,
                             QTabWidget, QGridLayout, QFrame, QSystemTrayIcon, QMenu, QApplication)
from PyQt6.QtCore import QTime, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction, QPixmap
import random
import os
from core.mouse_controller import MouseController
from core.scheduler import Scheduler
from core.hotkey_listener import HotkeyListener
from core.window_switcher import WindowSwitcher
from gui.about_tab import AboutTab

class MainWindow(QMainWindow):
    """Main application window with compact layout"""
    def __init__(self, app=None):
        super().__init__()
        self.mouse_controller = MouseController()
        self.scheduler = Scheduler()
        self.hotkey_listener = HotkeyListener()
        self.window_switcher = WindowSwitcher()
        self.is_active = False
        self.app = app
        self.tray_icon = None
        self.click_total = 0
        self.switch_total = 0
        self.start_time = QTime.currentTime()
        
        # Fixed window size
        self.setFixedSize(550, 650)
        
        # Random window title
        self.set_random_title()
        
        self.init_ui()
        self.connect_signals()
        
        # Start hotkey listener
        self.hotkey_listener.start()
        
        # Setup tray icon
        self.setup_tray()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Position window
        self.setGeometry(100, 100, 550, 650)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        self.create_header(main_layout)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_control_tab()
        self.create_scheduler_tab()
        self.create_window_switcher_tab()
        self.create_status_tab()
        self.create_about_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Footer with click counter
        self.create_footer(main_layout)
        
    def set_random_title(self):
        """Set random window title each time app starts"""
        random_titles = [
            "System Configuration",
            "Display Settings",
            "Volume Control",
            "Network Diagnostics",
            "Power Options",
            "Device Manager",
            "Windows Update",
            "Security Center",
            "Performance Monitor",
            "Task Scheduler"
        ]
        title = random.choice(random_titles)
        self.setWindowTitle(title)
        
    def setup_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            try:
                # Create tray icon
                self.tray_icon = QSystemTrayIcon(self)
                
                # Set icon if available
                icon_paths = [
                    "icon.ico",
                    "favicon.ico",
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon.ico")
                ]
                
                icon_set = False
                for path in icon_paths:
                    if os.path.exists(path):
                        try:
                            self.tray_icon.setIcon(QIcon(path))
                            self.setWindowIcon(QIcon(path))
                            icon_set = True
                            break
                        except:
                            continue
                
                if not icon_set:
                    # Create a simple default icon
                    pixmap = QPixmap(32, 32)
                    pixmap.fill(Qt.GlobalColor.transparent)
                    self.tray_icon.setIcon(QIcon(pixmap))
                
                # Create tray menu
                tray_menu = QMenu()
                
                show_action = QAction("Show", self)
                show_action.triggered.connect(self.show_normal)
                tray_menu.addAction(show_action)
                
                hide_action = QAction("Hide", self)
                hide_action.triggered.connect(self.hide_to_tray)
                tray_menu.addAction(hide_action)
                
                tray_menu.addSeparator()
                
                about_action = QAction("About", self)
                about_action.triggered.connect(self.show_about)
                tray_menu.addAction(about_action)
                
                tray_menu.addSeparator()
                
                exit_action = QAction("Exit", self)
                exit_action.triggered.connect(self.clean_exit)
                tray_menu.addAction(exit_action)
                
                self.tray_icon.setContextMenu(tray_menu)
                
                # Connect tray icon click
                self.tray_icon.activated.connect(self.tray_icon_activated)
                
                # Show tray icon
                self.tray_icon.show()
                
            except Exception as e:
                print(f"Tray setup error: {e}")
                self.tray_icon = None
        
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_normal()
            
    def show_normal(self):
        """Show window normally"""
        self.show()
        self.activateWindow()
        self.raise_()
        
    def hide_to_tray(self):
        """Hide window to system tray"""
        self.hide()
        
    def clean_exit(self):
        """Clean exit through tray"""
        self.close()
        
    def show_about(self):
        """Show about tab"""
        self.show_normal()
        self.tab_widget.setCurrentWidget(self.about_tab)
        
    def create_header(self, layout):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.NoFrame)
        header_layout = QVBoxLayout(header_frame)
        
        # Random Title Slogan
        slogans = [
            "Defending Your Right to Rest",
            "Because Surveillance Isn't Trust",
            "Reclaim Your Humanity at Work",
            "Work-Life Balance, Automated",
            "Fighting Micromanagement, One Break at a Time",
            "Dignity and Breaks for All Workers",
            "Because You're Human, Not a Metric",
            "Liberating Workers from Digital Chains",
            "Restoring Balance in the Age of Surveillance",
            "Your Well-Being Over Their Metrics"
        ]
        title = QLabel(f"WASP - {random.choice(slogans)}")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #3daee9;")
        
        # Hotkey info
        hotkey_info = QLabel("F9: Stop | ESC: Hide")
        hotkey_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hotkey_info.setStyleSheet("color: #f39c12; font-size: 10pt; padding: 2px;")
        
        # Runtime info
        self.runtime_label = QLabel("Runtime: 00:00:00")
        self.runtime_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.runtime_label.setStyleSheet("color: #888888; font-size: 9pt;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(hotkey_info)
        header_layout.addWidget(self.runtime_label)
        layout.addWidget(header_frame)
        
        # Start runtime timer
        self.runtime_timer = QTimer()
        self.runtime_timer.timeout.connect(self.update_runtime)
        self.runtime_timer.start(1000)  # Update every second
        
    def create_control_tab(self):
        """Create control tab"""
        control_tab = QWidget()
        layout = QVBoxLayout(control_tab)
        layout.setSpacing(8)
        
        # Control buttons
        control_group = QGroupBox("Mouse Activity")
        control_layout = QGridLayout()
        
        self.start_button = QPushButton("▶ Start")
        self.start_button.clicked.connect(self.start_activity)
        
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setStyleSheet("color: #fff;")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_activity)
        self.stop_button.setEnabled(False)
        
        control_layout.addWidget(self.start_button, 0, 0)
        control_layout.addWidget(self.stop_button, 0, 1)
        
        # Speed control
        speed_label = QLabel("Speed:")
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.1, 5.0)
        self.speed_spinbox.setValue(1.0)
        self.speed_spinbox.setSingleStep(0.1)
        self.speed_spinbox.setSuffix(" x")
        self.speed_spinbox.valueChanged.connect(self.update_speed)
        

        
        control_layout.addWidget(speed_label, 1, 0)
        control_layout.addWidget(self.speed_spinbox, 1, 1)
        
        # Click interval settings
        self.random_click_checkbox = QCheckBox("Random Interval")
        self.random_click_checkbox.stateChanged.connect(self.toggle_random_click)
        
        control_layout.addWidget(QLabel("Click Mode:"), 2, 0)
        control_layout.addWidget(self.random_click_checkbox, 2, 1)
        
        # Fixed interval UI
        self.fixed_label = QLabel("Interval:")
        self.fixed_spinbox = QSpinBox()
        self.fixed_spinbox.setRange(1, 300)
        self.fixed_spinbox.setValue(5)
        self.fixed_spinbox.setSuffix(" sec")
        self.fixed_spinbox.valueChanged.connect(self.update_click_fixed)
        
        control_layout.addWidget(self.fixed_label, 3, 0)
        control_layout.addWidget(self.fixed_spinbox, 3, 1)
        
        # Random interval UI (initially hidden)
        self.range_label = QLabel("Range (Min-Max):")
        
        range_layout = QHBoxLayout()
        self.min_click_spinbox = QSpinBox()
        self.min_click_spinbox.setRange(1, 300)
        self.min_click_spinbox.setValue(1)
        self.min_click_spinbox.setSuffix("s")
        self.min_click_spinbox.valueChanged.connect(self.update_click_range)
        
        self.max_click_spinbox = QSpinBox()
        self.max_click_spinbox.setRange(1, 300)
        self.max_click_spinbox.setValue(10)
        self.max_click_spinbox.setSuffix("s")
        self.max_click_spinbox.valueChanged.connect(self.update_click_range)
        
        range_layout.addWidget(self.min_click_spinbox)
        self.dash_label = QLabel("-")
        range_layout.addWidget(self.dash_label)
        range_layout.addWidget(self.max_click_spinbox)
        
        # Add to grid but keep reference to hide/show
        control_layout.addWidget(self.range_label, 3, 0)
        control_layout.addLayout(range_layout, 3, 1)
        
        # Initial state
        self.range_label.hide()
        self.min_click_spinbox.hide()
        self.max_click_spinbox.hide()
        self.dash_label.hide()
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Window switcher quick control
        switcher_group = QGroupBox("Quick Window Switcher")
        switcher_layout = QHBoxLayout()
        
        self.switcher_checkbox = QCheckBox("Enable")
        self.switcher_checkbox.stateChanged.connect(self.toggle_window_switcher)
        
        switcher_interval_label = QLabel("Interval:")
        self.switcher_interval_spinbox = QSpinBox()
        self.switcher_interval_spinbox.setRange(5, 300)
        self.switcher_interval_spinbox.setValue(30)
        self.switcher_interval_spinbox.setSuffix(" sec")
        self.switcher_interval_spinbox.valueChanged.connect(self.update_switcher_interval)
        
        switcher_layout.addWidget(self.switcher_checkbox)
        switcher_layout.addStretch()
        switcher_layout.addWidget(switcher_interval_label)
        switcher_layout.addWidget(self.switcher_interval_spinbox)
        
        switcher_group.setLayout(switcher_layout)
        layout.addWidget(switcher_group)
        layout.addStretch()
        
        self.tab_widget.addTab(control_tab, "🎯 Control")
        
    def create_scheduler_tab(self):
        """Create scheduler tab"""
        scheduler_tab = QWidget()
        layout = QVBoxLayout(scheduler_tab)
        layout.setSpacing(8)
        
        # Scheduler group
        scheduler_group = QGroupBox("Time Schedule")
        scheduler_layout = QVBoxLayout()
        
        # Enable checkbox
        self.scheduler_checkbox = QCheckBox("Enable Scheduler")
        self.scheduler_checkbox.stateChanged.connect(self.toggle_scheduler)
        scheduler_layout.addWidget(self.scheduler_checkbox)
        
        # Time settings in grid
        time_layout = QGridLayout()
        time_layout.setSpacing(5)
        
        start_label = QLabel("Start:")
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(9, 0))
        self.start_time_edit.setDisplayFormat("HH:mm")
        
        end_label = QLabel("End:")
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(17, 0))
        self.end_time_edit.setDisplayFormat("HH:mm")
        
        time_layout.addWidget(start_label, 0, 0)
        time_layout.addWidget(self.start_time_edit, 0, 1)
        time_layout.addWidget(end_label, 1, 0)
        time_layout.addWidget(self.end_time_edit, 1, 1)
        
        scheduler_layout.addLayout(time_layout)
        scheduler_group.setLayout(scheduler_layout)
        layout.addWidget(scheduler_group)
        
        # Current status
        status_group = QGroupBox("Current Status")
        status_layout = QVBoxLayout()
        
        self.scheduler_status = QLabel("Scheduler: Disabled")
        self.scheduler_status.setStyleSheet("font-weight: bold; color: #888888;")
        status_layout.addWidget(self.scheduler_status)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
        self.tab_widget.addTab(scheduler_tab, "⏰ Schedule")
        
    def create_window_switcher_tab(self):
        """Create window switcher tab"""
        switcher_tab = QWidget()
        layout = QVBoxLayout(switcher_tab)
        layout.setSpacing(8)
        
        # Main controls
        main_group = QGroupBox("Window Switcher Settings")
        main_layout = QVBoxLayout()
        
        # Enable switch
        enable_layout = QHBoxLayout()
        self.window_switcher_enable = QCheckBox("Enable Window Switching")
        self.window_switcher_enable.stateChanged.connect(self.toggle_window_switcher_full)
        enable_layout.addWidget(self.window_switcher_enable)
        enable_layout.addStretch()
        main_layout.addLayout(enable_layout)
        
        # Interval settings
        interval_group = QGroupBox("Switching Interval")
        interval_layout = QVBoxLayout()
        
        # Fixed or random interval
        self.random_interval_checkbox = QCheckBox("Random Interval")
        self.random_interval_checkbox.setChecked(True)
        self.random_interval_checkbox.stateChanged.connect(self.toggle_random_interval)
        interval_layout.addWidget(self.random_interval_checkbox)
        
        # Fixed interval
        fixed_layout = QHBoxLayout()
        self.ws_fixed_label = QLabel("Fixed interval:")
        self.fixed_interval_spinbox = QSpinBox()
        self.fixed_interval_spinbox.setRange(10, 300)
        self.fixed_interval_spinbox.setValue(30)
        self.fixed_interval_spinbox.setSuffix(" sec")
        self.fixed_interval_spinbox.valueChanged.connect(self.update_window_interval)
        fixed_layout.addWidget(self.ws_fixed_label)
        fixed_layout.addWidget(self.fixed_interval_spinbox)
        fixed_layout.addStretch()
        interval_layout.addLayout(fixed_layout)
        
        # Random range
        random_layout = QHBoxLayout()
        random_layout.setSpacing(10)
        
        self.ws_min_label = QLabel("Min:")
        self.min_interval_spinbox = QSpinBox()
        self.min_interval_spinbox.setRange(5, 200)
        self.min_interval_spinbox.setValue(15)
        self.min_interval_spinbox.setSuffix(" sec")
        self.min_interval_spinbox.valueChanged.connect(self.update_window_interval_range)
        
        self.ws_max_label = QLabel("Max:")
        self.max_interval_spinbox = QSpinBox()
        self.max_interval_spinbox.setRange(20, 600)
        self.max_interval_spinbox.setValue(60)
        self.max_interval_spinbox.setSuffix(" sec")
        self.max_interval_spinbox.valueChanged.connect(self.update_window_interval_range)
        
        random_layout.addWidget(self.ws_min_label)
        random_layout.addWidget(self.min_interval_spinbox)
        random_layout.addWidget(self.ws_max_label)
        random_layout.addWidget(self.max_interval_spinbox)
        random_layout.addStretch()
        
        interval_layout.addLayout(random_layout)
        interval_group.setLayout(interval_layout)
        main_layout.addWidget(interval_group)
        
        # Set initial state
        self.fixed_interval_spinbox.setEnabled(False)
        self.ws_fixed_label.setEnabled(False)
        self.min_interval_spinbox.setEnabled(True)
        self.ws_min_label.setEnabled(True)
        self.max_interval_spinbox.setEnabled(True)
        self.ws_max_label.setEnabled(True)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QVBoxLayout()
        
        self.ignore_system_checkbox = QCheckBox("Ignore system windows")
        self.ignore_system_checkbox.setChecked(True)
        self.ignore_system_checkbox.stateChanged.connect(self.toggle_system_windows)
        advanced_layout.addWidget(self.ignore_system_checkbox)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Window List")
        refresh_btn.clicked.connect(self.refresh_windows_list)
        refresh_btn.setMaximumWidth(150)
        advanced_layout.addWidget(refresh_btn)
        
        advanced_group.setLayout(advanced_layout)
        main_layout.addWidget(advanced_group)
        
        main_group.setLayout(main_layout)
        layout.addWidget(main_group)
        
        # Current window display
        current_group = QGroupBox("Last Switched Window")
        current_layout = QVBoxLayout()
        
        self.current_window_label = QLabel("None")
        self.current_window_label.setStyleSheet("""
            font-family: 'Consolas', monospace;
            color: #3daee9;
            padding: 5px;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            background-color: #1e1e1e;
        """)
        self.current_window_label.setWordWrap(True)
        current_layout.addWidget(self.current_window_label)
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)
        
        layout.addStretch()
        self.tab_widget.addTab(switcher_tab, "🪟 Windows")
        
    def create_status_tab(self):
        """Create status tab"""
        status_tab = QWidget()
        layout = QVBoxLayout(status_tab)
        
        status_group = QGroupBox("Activity Log")
        status_layout = QVBoxLayout()
        
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                min-height: 250px;
            }
        """)
        
        # Clear button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clear_status)
        clear_btn.setMaximumWidth(100)
        
        status_layout.addWidget(self.status_display)
        status_layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        self.tab_widget.addTab(status_tab, "📊 Status")
        
    def create_about_tab(self):
        """Create about tab"""
        self.about_tab = AboutTab()
        self.tab_widget.addTab(self.about_tab, "ℹ️ About")
        
    def create_footer(self, layout):
        """Create footer with click counter"""
        footer_frame = QFrame()
        footer_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        footer_layout = QHBoxLayout(footer_frame)
        
        self.click_counter = QLabel("Clicks: 0")
        self.click_counter.setStyleSheet("color: #3daee9; font-weight: bold;")
        
        self.switch_counter = QLabel("Switches: 0")
        self.switch_counter.setStyleSheet("color: #9b59b6; font-weight: bold;")
        
        footer_layout.addWidget(self.click_counter)
        footer_layout.addStretch()
        footer_layout.addWidget(self.switch_counter)
        
        layout.addWidget(footer_frame)
        
    def connect_signals(self):
        """Connect all signals and slots"""
        self.mouse_controller.status_update.connect(self.update_status)
        self.mouse_controller.activity_count.connect(self.update_click_count)
        
        self.scheduler.start_triggered.connect(self.start_activity)
        self.scheduler.stop_triggered.connect(self.stop_activity)
        self.scheduler.status_update.connect(self.update_scheduler_status)
        
        self.window_switcher.status_update.connect(self.update_status)
        self.window_switcher.window_switched.connect(self.update_window_switch_count)
        
        # Connect hotkey listener
        self.hotkey_listener.stop_triggered.connect(self.emergency_stop)
        
    def start_activity(self):
        """Start mouse activity"""
        if not self.is_active:
            self.is_active = True
            self.mouse_controller.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.update_status("Mouse activity started")
            
    def stop_activity(self):
        """Stop mouse activity"""
        if self.is_active:
            self.is_active = False
            self.mouse_controller.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.update_status("Mouse activity stopped")
            
    def emergency_stop(self):
        """Emergency stop triggered by hotkey"""
        if self.is_active:
            self.stop_activity()
            self.update_status("⚠️ Emergency stop - F9 pressed")
            
    def update_speed(self, value):
        """Update scroll speed"""
        self.mouse_controller.set_scroll_speed(value)
        
    def toggle_random_click(self, state):
        """Toggle between fixed and random click intervals"""
        is_random = state == Qt.CheckState.Checked.value
        
        self.fixed_label.setVisible(not is_random)
        self.fixed_spinbox.setVisible(not is_random)
        
        self.range_label.setVisible(is_random)
        self.min_click_spinbox.setVisible(is_random)
        self.max_click_spinbox.setVisible(is_random)
        self.dash_label.setVisible(is_random)
        
        # Re-trigger update to set correct mode
        if is_random:
            self.update_click_range()
        else:
            self.update_click_fixed()

    def update_click_fixed(self):
        """Update fixed click interval"""
        self.mouse_controller.set_click_interval(self.fixed_spinbox.value())
        
    def update_click_range(self):
        """Update random click range"""
        self.mouse_controller.set_random_click_interval(
            self.min_click_spinbox.value(),
            self.max_click_spinbox.value()
        )
        
    def update_switcher_interval(self, value):
        """Update quick switcher interval"""
        if self.switcher_checkbox.isChecked():
            self.window_switcher.set_interval(value)
        
    def toggle_scheduler(self, state):
        """Enable or disable scheduler"""
        enabled = state == Qt.CheckState.Checked.value
        self.scheduler.set_schedule(
            self.start_time_edit.time(),
            self.end_time_edit.time()
        )
        self.scheduler.enable_scheduler(enabled)
        status_text = f"Scheduler: {'Enabled' if enabled else 'Disabled'}"
        self.scheduler_status.setText(status_text)
        
    def toggle_window_switcher(self, state):
        """Toggle quick window switcher"""
        enabled = state == Qt.CheckState.Checked.value
        self.window_switcher.set_enabled(enabled)
        self.window_switcher.set_interval(self.switcher_interval_spinbox.value())
        self.window_switcher_enable.setChecked(enabled)
        
    def toggle_window_switcher_full(self, state):
        """Toggle full window switcher"""
        enabled = state == Qt.CheckState.Checked.value
        self.window_switcher.set_enabled(enabled)
        self.switcher_checkbox.setChecked(enabled)
        
        if enabled and not self.window_switcher.isRunning():
            self.window_switcher.start()
        elif not enabled and self.window_switcher.isRunning():
            self.window_switcher.stop()
            
    def toggle_random_interval(self, state):
        """Toggle random interval for window switching"""
        enabled = state == Qt.CheckState.Checked.value
        self.window_switcher.set_random_interval(enabled)
        
        # Enable/Disable controls
        self.fixed_interval_spinbox.setEnabled(not enabled)
        self.ws_fixed_label.setEnabled(not enabled)
        
        self.min_interval_spinbox.setEnabled(enabled)
        self.ws_min_label.setEnabled(enabled)
        
        self.max_interval_spinbox.setEnabled(enabled)
        self.ws_max_label.setEnabled(enabled)
        
    def update_window_interval(self):
        """Update window switching interval"""
        self.window_switcher.set_interval(self.fixed_interval_spinbox.value())
        
    def update_window_interval_range(self):
        """Update window switching interval range"""
        self.window_switcher.set_interval(
            self.fixed_interval_spinbox.value(),
            self.min_interval_spinbox.value(),
            self.max_interval_spinbox.value()
        )
        
    def toggle_system_windows(self, state):
        """Toggle ignoring system windows"""
        enabled = state == Qt.CheckState.Checked.value
        self.window_switcher.ignore_system_windows = enabled
        
    def refresh_windows_list(self):
        """Refresh the list of available windows"""
        windows = self.window_switcher.get_all_windows()
        count = len(windows)
        self.update_status(f"Found {count} available windows")
        
    def update_status(self, message):
        """Update status display"""
        timestamp = QTime.currentTime().toString("HH:mm:ss")
        self.status_display.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        self.status_display.verticalScrollBar().setValue(
            self.status_display.verticalScrollBar().maximum()
        )
        
    def update_click_count(self, count):
        """Update click counter"""
        self.click_total = count
        self.click_counter.setText(f"Clicks: {count}")
        
    def update_window_switch_count(self, window_title):
        """Update window switch counter and display"""
        self.current_window_label.setText(f"📋 {window_title}")
        # Update counter
        self.switch_total += 1
        self.switch_counter.setText(f"Switches: {self.switch_total}")
            
    def update_scheduler_status(self, message):
        """Update scheduler status"""
        self.update_status(message)
        
    def update_runtime(self):
        """Update runtime display"""
        current_time = QTime.currentTime()
        elapsed = self.start_time.secsTo(current_time)
        
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        
        self.runtime_label.setText(f"Runtime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
    def clear_status(self):
        """Clear status display"""
        self.status_display.clear()
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop all components
        self.hotkey_listener.stop()
        
        if self.is_active:
            self.mouse_controller.stop()
            
        if self.window_switcher.isRunning():
            self.window_switcher.stop()
            
        if self.runtime_timer.isActive():
            self.runtime_timer.stop()
            
        if self.tray_icon:
            self.tray_icon.hide()
            
        event.accept()
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_to_tray()
            event.accept()
        else:
            super().keyPressEvent(event)