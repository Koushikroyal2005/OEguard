"""
Defiance Detection Module
Detects when child tries to cheat the system
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DefianceMetrics:
    """Data class for defiance detection results"""
    timestamp: datetime
    face_disappeared: bool
    disappearance_duration: float
    rapid_movements: bool
    multiple_faces: bool
    defiance_score: float  # 0.0 to 1.0
    event_type: str  # 'normal', 'suspicious', 'defiance'

class DefianceDetector:
    """Monitors for cheating behaviors"""
    
    def __init__(self):
        self.face_present_history = []
        self.face_disappear_start = None
        self.last_face_position = None
        self.rapid_movement_counter = 0
        self.defiance_events = []
        
    def update(self, face_present: bool, face_position: Optional[tuple] = None):
        """
        Update detector with current frame data
        
        Args:
            face_present: Whether face is detected
            face_position: (x, y) center of face if present
        """
        current_time = time.time()
        metrics = DefianceMetrics(
            timestamp=datetime.now(),
            face_disappeared=False,
            disappearance_duration=0.0,
            rapid_movements=False,
            multiple_faces=False,
            defiance_score=0.0,
            event_type='normal'
        )
        
        # Track face presence history
        self.face_present_history.append({
            'time': current_time,
            'present': face_present,
            'position': face_position
        })
        
        # Keep only last 60 seconds of history
        self.face_present_history = [
            h for h in self.face_present_history 
            if current_time - h['time'] < 60
        ]
        
        # Check 1: Sudden face disappearance
        if not face_present and self.face_disappear_start is None:
            self.face_disappear_start = current_time
        
        if face_present and self.face_disappear_start is not None:
            disappearance_duration = current_time - self.face_disappear_start
            
            if disappearance_duration > 2.0:  # Suspicious if gone > 2 seconds
                metrics.face_disappeared = True
                metrics.disappearance_duration = disappearance_duration
                metrics.defiance_score = min(disappearance_duration / 10.0, 1.0)
                metrics.event_type = 'suspicious'
                
                if disappearance_duration > 5.0:
                    metrics.event_type = 'defiance'
            
            self.face_disappear_start = None
        
        # Check 2: Rapid movements (ducking under desk)
        if face_present and face_position and self.last_face_position:
            dx = face_position[0] - self.last_face_position[0]
            dy = face_position[1] - self.last_face_position[1]
            movement = (dx**2 + dy**2)**0.5
            
            if movement > 100:  # Large movement threshold
                self.rapid_movement_counter += 1
                
                if self.rapid_movement_counter > 5:
                    metrics.rapid_movements = True
                    metrics.defiance_score += 0.3
                    metrics.event_type = 'suspicious'
        
        if face_position:
            self.last_face_position = face_position
        
        # Reset rapid movement counter if no rapid movement
        if self.rapid_movement_counter > 0:
            self.rapid_movement_counter = max(0, self.rapid_movement_counter - 0.1)
        
        # Store defiance events
        if metrics.event_type in ['suspicious', 'defiance']:
            self.defiance_events.append(metrics)
        
        # Cap defiance score at 1.0
        metrics.defiance_score = min(metrics.defiance_score, 1.0)
        
        return metrics
    
    def get_defiance_history(self, minutes: int = 5):
        """Get recent defiance events"""
        cutoff_time = time.time() - (minutes * 60)
        return [
            event for event in self.defiance_events 
            if event.timestamp.timestamp() > cutoff_time
        ]
    
    def clear_history(self):
        """Clear defiance event history"""
        self.defiance_events = []
