"""
Computer Vision Module - Eye Blink Detection
Uses MediaPipe Face Mesh for real-time blink monitoring
"""

import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import time

@dataclass
class EyeMetrics:
    """Data class for eye tracking results"""
    timestamp: datetime
    blink_rate: float  # Blinks per minute
    ear_left: float    # Eye Aspect Ratio - Left
    ear_right: float   # Eye Aspect Ratio - Right
    face_present: bool
    total_blinks: int

class EyeTracker:
    """Real-time eye blink detection using MediaPipe"""
    
    def __init__(self, camera_index=0):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks indices for MediaPipe
        # Left eye
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        # Right eye
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        self.camera = cv2.VideoCapture(camera_index)
        self.blink_counter = 0
        self.blink_start_time = time.time()
        self.last_blink_time = time.time()
        self.face_present = False
        
    def eye_aspect_ratio(self, eye_landmarks):
        """Calculate Eye Aspect Ratio (EAR)"""
        # Vertical distances
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal distance
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # EAR calculation
        ear = (v1 + v2) / (2.0 * h)
        return ear
    
    def get_eye_coordinates(self, face_landmarks, eye_indices, frame_shape):
        """Extract eye landmark coordinates"""
        h, w = frame_shape[:2]
        eye_points = []
        for index in eye_indices:
            point = face_landmarks.landmark[index]
            x, y = int(point.x * w), int(point.y * h)
            eye_points.append(np.array([x, y]))
        return eye_points
    
    def process_frame(self):
        """Process a single frame from camera"""
        success, frame = self.camera.read()
        if not success:
            return None, None
        
        frame = cv2.flip(frame, 1)  # Mirror effect
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        metrics = None
        annotated_frame = frame.copy()
        
        if results.multi_face_landmarks:
            self.face_present = True
            face_landmarks = results.multi_face_landmarks[0]
            
            # Get eye landmarks
            left_eye = self.get_eye_coordinates(
                face_landmarks, self.LEFT_EYE, frame.shape
            )
            right_eye = self.get_eye_coordinates(
                face_landmarks, self.RIGHT_EYE, frame.shape
            )
            
            # Calculate EAR
            ear_left = self.eye_aspect_ratio(left_eye)
            ear_right = self.eye_aspect_ratio(right_eye)
            
            # Blink detection threshold
            EAR_THRESHOLD = 0.25
            
            if ear_left < EAR_THRESHOLD and ear_right < EAR_THRESHOLD:
                if time.time() - self.last_blink_time > 0.2:  # Debounce
                    self.blink_counter += 1
                    self.last_blink_time = time.time()
            
            # Calculate blink rate (blinks per minute)
            elapsed_time = time.time() - self.blink_start_time
            blink_rate = (self.blink_counter / elapsed_time) * 60 if elapsed_time > 0 else 0
            
            # Create metrics
            metrics = EyeMetrics(
                timestamp=datetime.now(),
                blink_rate=round(blink_rate, 1),
                ear_left=round(ear_left, 3),
                ear_right=round(ear_right, 3),
                face_present=True,
                total_blinks=self.blink_counter
            )
            
            # Draw eye contours
            cv2.polylines(annotated_frame, [np.array(left_eye)], True, (0, 255, 0), 1)
            cv2.polylines(annotated_frame, [np.array(right_eye)], True, (0, 255, 0), 1)
            
            # Add text overlay
            cv2.putText(
                annotated_frame,
                f"Blinks: {self.blink_counter} | Rate: {blink_rate:.1f}/min",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
        else:
            self.face_present = False
        
        return metrics, annotated_frame
    
    def release(self):
        """Release camera resources"""
        self.camera.release()
        cv2.destroyAllWindows()

def test_camera():
    """Quick test function for camera setup"""
    print("📸 Testing camera...")
    tracker = EyeTracker()
    
    try:
        for _ in range(100):  # Test for 100 frames
            metrics, frame = tracker.process_frame()
            if frame is not None:
                cv2.imshow("Eye Tracker Test", frame)
                if metrics:
                    print(f"Blink Rate: {metrics.blink_rate}/min | Face: {metrics.face_present}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        tracker.release()

if __name__ == "__main__":
    test_camera()
