"""
Tool definitions for the Guardian Agent
These are the functions the agent can call
"""

from typing import Dict, Any
import time

class GuardianTools:
    """Collection of tools the AI agent can use"""
    
    def __init__(self, sensor_api=None, intervention_api=None):
        self.sensor_api = sensor_api
        self.intervention_api = intervention_api
        self.last_warning_time = 0
        self.warning_count = 0
        
    def check_current_blink_rate(self) -> Dict[str, Any]:
        """
        Get current blink rate and face detection status
        
        Returns:
            Dict with blink_rate, face_present, session_duration
        """
        # This will connect to the sensor API in production
        # For now, returns mock data for testing
        if self.sensor_api:
            return self.sensor_api.get_blink_metrics()
        
        return {
            "blink_rate": 0,
            "face_present": True,
            "session_duration": 0,
            "ear_left": 0.0,
            "ear_right": 0.0
        }
    
    def check_defiance_status(self) -> Dict[str, Any]:
        """
        Check if child is trying to cheat the system
        
        Returns:
            Dict with defiance_score, suspicious_activities
        """
        if self.sensor_api:
            return self.sensor_api.get_defiance_metrics()
        
        return {
            "defiance_score": 0.0,
            "face_disappeared": False,
            "rapid_movements": False
        }
    
    def show_warning_popup(self, message: str, urgency: str = "normal") -> Dict[str, Any]:
        """
        Display a warning message on screen
        
        Args:
            message: Warning message to display
            urgency: 'gentle', 'normal', or 'urgent'
        """
        current_time = time.time()
        
        # Rate limiting: Don't spam warnings
        if current_time - self.last_warning_time < 30 and urgency != "urgent":
            return {
                "success": False,
                "reason": "Too soon for another warning"
            }
        
        self.last_warning_time = current_time
        self.warning_count += 1
        
        if self.intervention_api:
            result = self.intervention_api.show_popup(message, urgency)
        else:
            result = {"displayed": True, "message": message}
        
        return {
            "success": True,
            "warning_count": self.warning_count,
            "message_displayed": message,
            "urgency": urgency
        }
    
    def lock_screen(self, reason: str, duration_minutes: int = 5) -> Dict[str, Any]:
        """
        Lock the computer screen for a break
        
        Args:
            reason: Why the screen is being locked
            duration_minutes: How long to lock (default 5 min)
        """
        if self.intervention_api:
            result = self.intervention_api.lock_system(reason, duration_minutes)
        else:
            result = {"locked": True, "reason": reason}
        
        return {
            "screen_locked": True,
            "reason": reason,
            "duration": duration_minutes,
            "warning_count": self.warning_count
        }
    
    def send_parent_alert(self, message: str) -> Dict[str, Any]:
        """
        Send SMS alert to parent
        
        Args:
            message: Alert message to send
        """
        if self.intervention_api:
            result = self.intervention_api.send_sms(message)
        else:
            result = {"sent": True, "message": message}
        
        return {
            "alert_sent": True,
            "message": message,
            "timestamp": time.time()
        }
    
    def reset_warning_count(self):
        """Reset warning counter (called after successful break)"""
        self.warning_count = 0
