"""
Screen Locker Module
Locks the operating system screen for break enforcement
"""

import os
import platform
import subprocess
import time
from typing import Dict, Any
from datetime import datetime, timedelta

class ScreenLocker:
    """OS-level screen locking"""
    
    def __init__(self):
        self.system = platform.system()
        self.locked = False
        self.lock_start_time = None
        self.lock_duration = 0
        
    def lock_screen(self, reason: str = "Eye break time!", 
                    duration_minutes: int = 5) -> Dict[str, Any]:
        """
        Lock the screen
        
        Args:
            reason: Why screen is being locked
            duration_minutes: How long to lock
            
        Returns:
            Status dictionary
        """
        if self.locked:
            return {
                "success": False,
                "reason": "Screen already locked",
                "remaining_time": self.get_remaining_lock_time()
            }
        
        try:
            self._execute_lock()
            self.locked = True
            self.lock_start_time = datetime.now()
            self.lock_duration = duration_minutes
            
            return {
                "success": True,
                "locked": True,
                "reason": reason,
                "duration_minutes": duration_minutes,
                "unlock_at": (self.lock_start_time + 
                             timedelta(minutes=duration_minutes)).isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_lock(self):
        """Execute OS-specific lock command"""
        if self.system == "Windows":
            # Windows lock
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            
        elif self.system == "Darwin":  # macOS
            # Mac lock
            subprocess.run([
                '/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession',
                '-suspend'
            ])
            
        elif self.system == "Linux":
            # Linux lock (multiple options)
            commands = [
                ['gnome-screensaver-command', '-l'],
                ['xdg-screensaver', 'lock'],
                ['loginctl', 'lock-session']
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, check=True)
                    break
                except:
                    continue
        else:
            raise OSError(f"Unsupported OS: {self.system}")
    
    def get_remaining_lock_time(self) -> int:
        """Get remaining lock time in seconds"""
        if not self.locked or not self.lock_start_time:
            return 0
        
        unlock_time = self.lock_start_time + timedelta(minutes=self.lock_duration)
        remaining = (unlock_time - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def should_unlock(self) -> bool:
        """Check if lock duration has expired"""
        return self.locked and self.get_remaining_lock_time() <= 0
    
    def reset_lock(self):
        """Reset lock status"""
        self.locked = False
        self.lock_start_time = None
        self.lock_duration = 0

class ScreenDimmer:
    """Dim screen instead of full lock (gentler approach)"""
    
    def __init__(self):
        self.original_brightness = None
        
    def dim_screen(self, level: int = 20) -> bool:
        """
        Dim screen to specified level
        
        Args:
            level: Brightness percentage (0-100)
        """
        system = platform.system()
        
        try:
            if system == "Windows":
                import screen_brightness_control as sbc
                self.original_brightness = sbc.get_brightness()
                sbc.set_brightness(level)
                
            elif system == "Darwin":
                # macOS brightness control
                subprocess.run(['brightness', str(level/100)])
                
            elif system == "Linux":
                # Linux brightness
                subprocess.run(['xbacklight', '-set', str(level)])
                
            return True
        except Exception as e:
            print(f"Failed to dim screen: {e}")
            return False
    
    def restore_brightness(self) -> bool:
        """Restore original brightness"""
        if self.original_brightness:
            system = platform.system()
            try:
                if system == "Windows":
                    import screen_brightness_control as sbc
                    sbc.set_brightness(self.original_brightness)
                return True
            except:
                return False
        return False

# Test screen locker
if __name__ == "__main__":
    print("⚠️  Screen Locker Test")
    print("This will lock your screen in 5 seconds!")
    print("Press Ctrl+C to cancel...")
    
    time.sleep(5)
    
    locker = ScreenLocker()
    result = locker.lock_screen("Test lock - eye break!", duration_minutes=1)
    print(f"Lock result: {result}")
