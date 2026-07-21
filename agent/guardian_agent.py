"""
Main Guardian Agent
Uses ReAct (Reasoning + Acting) loop for decision making
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import json

# For LLM integration (we'll use a simpler version first)
class GuardianAgent:
    """
    AI Agent that makes decisions about screen time management
    Uses rule-based logic initially, with LLM integration planned
    """
    
    def __init__(self, child_name: str = "Leo", favorite_character: str = "Sonic"):
        self.child_name = child_name
        self.favorite_character = favorite_character
        self.memory = None  # Will be set up later
        self.tools = None   # Will be set up later
        
        # Decision thresholds
        self.BLINK_NORMAL = 15  # Normal blink rate
        self.BLINK_WARNING = 10  # Warning threshold
        self.BLINK_CRITICAL = 5  # Critical threshold
        self.MAX_SESSION_MINUTES = 45  # Max session before break
        self.MAX_WARNINGS_BEFORE_LOCK = 3  # Escalation limit
        
        self.warning_count = 0
        self.last_action = None
        self.decision_log = []
        
    def setup(self, memory, tools):
        """Setup agent with memory and tools"""
        self.memory = memory
        self.tools = tools
        
    def think(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main decision-making method
        Implements simplified ReAct loop:
        1. Observe sensor data
        2. Check memory for patterns
        3. Decide on action
        4. Execute action
        5. Log decision
        """
        thought_process = []
        
        # Step 1: Observe
        blink_rate = sensor_data.get('blink_rate', 0)
        face_present = sensor_data.get('face_present', True)
        session_duration = sensor_data.get('session_duration', 0)
        defiance_score = sensor_data.get('defiance_score', 0.0)
        
        thought_process.append(f"Observing: Blink rate={blink_rate}/min, Face={face_present}, Session={session_duration}min")
        
        # Step 2: Check memory for patterns
        memory_context = "No historical data"
        if self.memory:
            recent_history = self.memory.get_recent_history(30)
            if recent_history:
                memory_context = f"Past 30min: {len(recent_history)} events, Last action: {recent_history[-1].get('action')}"
                thought_process.append(f"Memory: {memory_context}")
        
        # Step 3: Decide action
        decision = self._decide_action(
            blink_rate, face_present, session_duration, defiance_score
        )
        thought_process.append(f"Decision: {decision['action']} - {decision.get('reason', '')}")
        
        # Step 4: Generate appropriate message
        message = self._generate_message(decision['action'], blink_rate)
        
        # Step 5: Log decision
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data,
            "thought_process": thought_process,
            "decision": decision,
            "message": message
        }
        self.decision_log.append(log_entry)
        
        # Store in memory if available
        if self.memory:
            self.memory.store_event({
                "timestamp": datetime.now().isoformat(),
                "blink_rate": blink_rate,
                "action": decision['action'],
                "defiance_score": defiance_score,
                "session_duration": session_duration,
                "message": message
            })
        
        return {
            "action": decision['action'],
            "priority": decision['priority'],
            "message": message,
            "thought_process": thought_process,
            "blink_rate": blink_rate,
            "face_present": face_present,
            "defiance_score": defiance_score
        }
    
    def _decide_action(self, blink_rate: float, face_present: bool, 
                       session_duration: int, defiance_score: float) -> Dict[str, str]:
        """Decision logic for the agent"""
        
        # CRITICAL: No face detected for too long
        if not face_present and self.warning_count > 0:
            return {
                "action": "NOTIFY_PARENT",
                "priority": "critical",
                "reason": "Child disappeared during warning sequence"
            }
        
        # HIGH DEFIANCE: Child trying to cheat
        if defiance_score > 0.7:
            self.warning_count += 1
            return {
                "action": "LOCK",
                "priority": "high",
                "reason": f"Defiance detected (score: {defiance_score})"
            }
        
        # CRITICAL BLINK RATE: Very low
        if blink_rate < self.BLINK_CRITICAL and blink_rate > 0:
            self.warning_count += 1
            action = "LOCK" if self.warning_count >= self.MAX_WARNINGS_BEFORE_LOCK else "WARN"
            return {
                "action": action,
                "priority": "high",
                "reason": f"Critical eye strain (blink rate: {blink_rate}/min)"
            }
        
        # WARNING BLINK RATE: Below normal
        if blink_rate < self.BLINK_WARNING and blink_rate > 0:
            self.warning_count += 1
            if self.warning_count >= self.MAX_WARNINGS_BEFORE_LOCK:
                return {
                    "action": "LOCK",
                    "priority": "high",
                    "reason": f"Multiple warnings ignored ({self.warning_count} warnings)"
                }
            return {
                "action": "WARN",
                "priority": "medium",
                "reason": f"Low blink rate detected ({blink_rate}/min)"
            }
        
        # LONG SESSION: Time for a break
        if session_duration > self.MAX_SESSION_MINUTES:
            return {
                "action": "WARN",
                "priority": "medium",
                "reason": f"Session too long ({session_duration} minutes)"
            }
        
        # DEFAULT: Everything seems fine
        return {
            "action": "MONITOR",
            "priority": "low",
            "reason": "All metrics normal"
        }
    
    def _generate_message(self, action: str, blink_rate: float) -> str:
        """Generate appropriate messages based on action"""
        
        messages = {
            "MONITOR": f"Keep going {self.child_name}! Your eyes are doing great! 👀✨",
            
            "WARN": [
                f"Hey {self.child_name}! {self.favorite_character} says your eyes need a quick break! 🦔",
                f"Time for a 20-second eye rest! Look away from the screen, just like {self.favorite_character} would!",
                f"Your eyes are working hard! Let's do a quick blink exercise together! 😊",
                f"⚠️ Eye break time! Look at something far away for 20 seconds!"
            ][min(self.warning_count - 1, 3)],
            
            "LOCK": [
                f"🔒 Screen locked for 5 minutes! {self.favorite_character} wants you to rest your eyes!",
                f"⏸️ Break time! Screen will unlock in 5 minutes. Go stretch like {self.favorite_character}!",
                f"🚫 Screen time paused! Your eyes need to rest. See you in 5 minutes!"
            ][min(self.warning_count - 1, 2)],
            
            "NOTIFY_PARENT": f"⚠️ Alert! Parent has been notified. Please take a break, {self.child_name}."
        }
        
        return messages.get(action, "Keep up the good work!")
    
    def get_decision_history(self, last_n: int = 10) -> list:
        """Get recent decisions"""
        return self.decision_log[-last_n:]
    
    def get_status_report(self) -> Dict[str, Any]:
        """Generate a status report"""
        if not self.memory:
            return {"status": "Memory not configured"}
        
        patterns = self.memory.analyze_patterns()
        recent_decisions = self.get_decision_history(5)
        
        return {
            "current_warning_count": self.warning_count,
            "last_action": self.last_action,
            "behavior_patterns": patterns,
            "recent_decisions": [
                {
                    "time": d['timestamp'],
                    "action": d['decision']['action'],
                    "blink_rate": d['blink_rate']
                }
                for d in recent_decisions
            ]
        }

# Test the agent
if __name__ == "__main__":
    from memory import GuardianMemory
    from tools import GuardianTools
    
    # Setup
    agent = GuardianAgent(child_name="Leo", favorite_character="Sonic")
    memory = GuardianMemory()
    tools = GuardianTools()
    agent.setup(memory, tools)
    
    # Simulate sensor data
    test_scenarios = [
        {"blink_rate": 18, "face_present": True, "session_duration": 10, "defiance_score": 0.0},
        {"blink_rate": 8, "face_present": True, "session_duration": 20, "defiance_score": 0.0},
        {"blink_rate": 4, "face_present": True, "session_duration": 30, "defiance_score": 0.0},
        {"blink_rate": 4, "face_present": False, "session_duration": 35, "defiance_score": 0.8},
    ]
    
    for i, data in enumerate(test_scenarios):
        print(f"\n{'='*50}")
        print(f"Scenario {i+1}: {data}")
        decision = agent.think(data)
        print(f"Action: {decision['action']}")
        print(f"Message: {decision['message']}")
        print(f"Priority: {decision['priority']}")
