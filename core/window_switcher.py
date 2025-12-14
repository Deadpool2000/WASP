import random
import time
try:
    import pygetwindow as gw
except (ImportError, NotImplementedError):
    gw = None
import sys
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

class WindowSwitcher(QThread):
    """Thread for switching between windows"""
    
    status_update = pyqtSignal(str)
    window_switched = pyqtSignal(str)  
    ignore_system_windows = True
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.enabled = False
        self.use_random_timing = True
        self.fixed_interval = 60  # seconds between switches
        self.min_interval = 30
        self.max_interval = 120
        self.switch_counter = 0
        
    def set_enabled(self, enabled):
        """Enable or disable window switching"""
        self.enabled = enabled
        if enabled and not self.isRunning():
            self.start()
        
    def set_random_interval(self, use_random):
        """Set whether to use random or fixed timing"""
        self.use_random_timing = use_random
        
    def set_interval(self, fixed_interval=None, min_interval=None, max_interval=None):
        """Set the interval(s) between switches"""
        if fixed_interval is not None:
            self.fixed_interval = max(10, fixed_interval)
        if min_interval is not None:
            self.min_interval = max(5, min_interval)
        if max_interval is not None:
            self.max_interval = max(self.min_interval + 10, max_interval)
        
    def _get_windows_linux(self):
        """Get list of windows on Linux using wmctrl"""
        try:
            # wmctrl -l lists windows: ID Desktop Host Title
            output = subprocess.check_output(['wmctrl', '-l'], text=True)
            windows = []
            for line in output.splitlines():
                parts = line.split(maxsplit=3)
                if len(parts) > 3:
                    windows.append(parts[3])
            return windows
        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def get_all_windows(self):
        """Get list of all available windows"""
        if sys.platform.startswith('linux'):
            all_windows = self._get_windows_linux()
            if not all_windows and gw is None:
                return []
        elif gw is None:
            return []
        
        try:
            if not sys.platform.startswith('linux'):
                all_windows = gw.getAllTitles()
            # Filter out empty titles and system windows
            valid_windows = [w for w in all_windows 
                           if w and w.strip()]
            if self.ignore_system_windows:
                # Filter out common system window titles
                system_keywords = ['ProSlacker', 'System Configuration', 'Display Settings', 
                                 'Volume Control', 'Network Diagnostics', 'Power Options',
                                 'Device Manager', 'Windows Update', 'Security Center',
                                 'Performance Monitor', 'Task Scheduler']
                valid_windows = [w for w in valid_windows 
                               if not any(keyword in w for keyword in system_keywords)]
            return valid_windows
        except:
            return []
        
    def switch_to_random_window(self):
        """Switch to a random window"""
        windows = self.get_all_windows()
        
        if not windows:
            self.status_update.emit("No windows available to switch")
            return False
            
        try:
            # Select random window
            target_window = random.choice(windows)
            
            if sys.platform.startswith('linux'):
                # Activate window on Linux
                subprocess.run(['wmctrl', '-a', target_window])
            else:
                window = gw.getWindowsWithTitle(target_window)[0]
                
                # Activate the window
                window.activate()
            
            self.switch_counter += 1
            self.window_switched.emit(target_window)  # Emit the window title
            self.status_update.emit(f"Switched to: {target_window[:40]}...")
            return True
        except Exception as e:
            self.status_update.emit(f"Switch failed: {str(e)}")
            return False
    
    def stop(self):
        """Stop the window switcher"""
        self.running = False
        
    def run(self):
        """Main execution loop"""
        if gw is None and not sys.platform.startswith('linux'):
            self.status_update.emit("Error: pygetwindow not installed")
            return
            
        self.running = True
        self.switch_counter = 0
        last_switch_time = time.time()
        
        if self.enabled:
            self.status_update.emit("Window switching enabled")
        
        while self.running:
            try:
                if self.enabled:
                    current_time = time.time()
                    
                    # Determine interval
                    if self.use_random_timing:
                        interval = random.randint(self.min_interval, self.max_interval)
                    else:
                        interval = self.fixed_interval
                    
                    # Check if it's time to switch
                    if current_time - last_switch_time >= interval:
                        self.switch_to_random_window()
                        last_switch_time = current_time
                
                # Small delay
                time.sleep(1)
                
            except Exception as e:
                self.status_update.emit(f"Window switcher error: {str(e)}")
                break
        
        if self.enabled:
            self.status_update.emit("Window switching stopped")