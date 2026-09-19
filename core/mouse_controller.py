import pyautogui
import random
import time
import math
from PyQt6.QtCore import QThread, pyqtSignal

# Disable pyautogui's failsafe for smoother operation
pyautogui.FAILSAFE = False

class MouseController(QThread):    
    status_update = pyqtSignal(str)
    activity_count = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.scroll_speed = 1.0
        self.click_interval = 5
        self.min_click_interval = 1
        self.max_click_interval = 5
        self.random_click = False
        self.click_count = 0
        self.rest_enabled = False
        self.rest_duration = 2.0
        
    def set_scroll_speed(self, speed):
        """Set the scrolling speed (0.1 to 5.0)"""
        self.scroll_speed = max(0.1, min(5.0, speed))
        
    def set_click_interval(self, interval):
        """Set the fixed interval between clicks in seconds"""
        self.click_interval = max(1, interval)
        self.random_click = False
        
    def set_random_click_interval(self, min_interval, max_interval):
        """Set random interval range"""
        self.min_click_interval = max(1, min_interval)
        self.max_click_interval = max(self.min_click_interval, max_interval)
        self.random_click = True

    def set_rest_enabled(self, enabled):
        """Enable or disable rest between mouse movements."""
        self.rest_enabled = enabled

    def set_rest_duration(self, duration):
        """Set rest duration between mouse movements in seconds."""
        self.rest_duration = max(0.1, min(60.0, duration))

    def _wait_between_movements(self):
        """Wait before starting the next movement."""
        rest_duration = (
            self.rest_duration
            if self.rest_enabled
            else random.uniform(0.05, 0.15)
        )
        rest_end = time.monotonic() + rest_duration
        while self.running and time.monotonic() < rest_end:
            time.sleep(min(0.1, rest_end - time.monotonic()))

    def _bezier_point(self, t, start, c1, c2, end):
        """Calculate point on cubic Bezier curve"""
        x = (1-t)**3 * start[0] + 3 * (1-t)**2 * t * c1[0] + 3 * (1-t) * t**2 * c2[0] + t**3 * end[0]
        y = (1-t)**3 * start[1] + 3 * (1-t)**2 * t * c1[1] + 3 * (1-t) * t**2 * c2[1] + t**3 * end[1]
        return x, y

    def move_naturally(self, x, y, duration):
        """Move mouse with natural curves and acceleration"""
        start_x, start_y = pyautogui.position()
        dist = math.hypot(x - start_x, y - start_y)
        
        if dist < 5:
            pyautogui.moveTo(x, y)
            return

        # Randomize control points for natural arc
        # Vector from start to end
        dx = x - start_x
        dy = y - start_y
        
        # Perpendicular vector (for curve offset)
        px = -dy
        py = dx
        
        # Normalize perpendicular vector
        norm = math.hypot(px, py)
        if norm == 0:
            px, py = 0, 0
        else:
            px /= norm
            py /= norm
            
        # Offset magnitude (random curvature)
        # Use a random factor of the distance, e.g., +/- 20%
        arc_scale = random.uniform(-0.2, 0.2)
        offset_x = px * dist * arc_scale
        offset_y = py * dist * arc_scale
        
        # Control points:
        # C1: 25% of the way + offset
        # C2: 75% of the way + offset
        c1_x = start_x + dx * 0.25 + offset_x
        c1_y = start_y + dy * 0.25 + offset_y
        
        c2_x = start_x + dx * 0.75 + offset_x
        c2_y = start_y + dy * 0.75 + offset_y
        
        # Generate movement steps
        # Use 60 steps per second for smoothness
        steps = max(int(duration * 60), 10)
        dt = duration / steps
        
        # Save original pause setting
        original_pause = pyautogui.PAUSE
        pyautogui.PAUSE = 0
        
        try:
            for i in range(steps + 1):
                if not self.running:
                    break
                    
                t = i / steps
                
                # EaseInOutQuad Acceleration
                # Accelerate until halfway, then decelerate
                if t < 0.5:
                    alpha = 2 * t * t
                else:
                    alpha = -1 + (4 - 2 * t) * t
                    
                curr_x, curr_y = self._bezier_point(alpha, (start_x, start_y), (c1_x, c1_y), (c2_x, c2_y), (x, y))
                
                # Move
                pyautogui.moveTo(curr_x, curr_y)
                
                # Wait
                time.sleep(dt)
        finally:
            pyautogui.PAUSE = original_pause
        
    def stop(self):
        """Stop the mouse controller"""
        self.running = False
        
    def perform_human_click(self):
        """Perform a quick human-like click"""
        # Very short hold time for fluid feel
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.02, 0.05))
        pyautogui.mouseUp()

    def run(self):
        """Main execution loop"""
        self.running = True
        self.click_count = 0
        last_click_time = time.time()
        
        # Determine initial wait time
        if self.random_click:
            current_wait_time = random.uniform(self.min_click_interval, self.max_click_interval)
        else:
            current_wait_time = self.click_interval
        
        self.status_update.emit("Activity started")
        
        while self.running:
            try:
                # Get screen dimensions
                screen_width, screen_height = pyautogui.size()
                
                # Random mouse movement
                x = random.randint(100, screen_width - 100)
                y = random.randint(100, screen_height - 100)
                
                # Calculate duration based on speed (inverse relationship)
                duration = 0.5 / self.scroll_speed
                
                # Move mouse naturally
                self.move_naturally(x, y, duration)
                
                # Check if it's time to click
                current_time = time.time()
                if current_time - last_click_time >= current_wait_time:
                    self.perform_human_click()
                    
                    # Reset timer and calculate next wait time
                    last_click_time = time.time()
                    if self.random_click:
                        current_wait_time = random.uniform(self.min_click_interval, self.max_click_interval)
                    else:
                        current_wait_time = self.click_interval
                    self.click_count += 1
                    self.activity_count.emit(self.click_count)
                    self.status_update.emit(f"Clicked at ({x}, {y})")
                
                # Random scroll (wheel)
                if random.random() < 0.3:  # 30% chance to scroll
                    scroll_amount = random.randint(-5, 5) * 10
                    pyautogui.scroll(scroll_amount)
                
                # Rest before next movement
                self._wait_between_movements()
                
            except Exception as e:
                self.status_update.emit(f"Error: {str(e)}")
                break
        
        self.status_update.emit("Activity stopped")
