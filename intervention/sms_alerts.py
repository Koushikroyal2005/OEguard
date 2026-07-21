"""
SMS Alert Module using Twilio
Sends notifications to parents
"""

import os
from typing import Dict, Any
from datetime import datetime

class SMSAlerter:
    """Send SMS alerts to parents via Twilio"""
    
    def __init__(self, account_sid: str = None, auth_token: str = None, 
                 from_number: str = None):
        """
        Initialize SMS alerter
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            from_number: Twilio phone number
        """
        self.account_sid = account_sid or os.getenv('TWILIO_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_TOKEN')
        self.from_number = from_number or os.getenv('TWILIO_FROM')
        self.client = None
        self.test_mode = not all([self.account_sid, self.auth_token, self.from_number])
        
        if not self.test_mode:
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
            except ImportError:
                print("Twilio not installed. Running in test mode.")
                self.test_mode = True
    
    def send_alert(self, message: str, to_number: str = None) -> Dict[str, Any]:
        """
        Send SMS alert
        
        Args:
            message: Alert message
            to_number: Parent's phone number
            
        Returns:
            Status dictionary
        """
        to_number = to_number or os.getenv('PARENT_PHONE')
        
        if not to_number:
            return {
                "success": False,
                "error": "No parent phone number configured",
                "timestamp": datetime.now().isoformat()
            }
        
        if self.test_mode:
            # Test mode - log to console instead
            print(f"\n{'='*50}")
            print(f"📱 SMS ALERT (TEST MODE)")
            print(f"To: {to_number}")
            print(f"Message: {message}")
            print(f"{'='*50}\n")
            
            return {
                "success": True,
                "test_mode": True,
                "to": to_number,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "sid": "TEST_MODE"
            }
        
        try:
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            return {
                "success": True,
                "sid": twilio_message.sid,
                "to": to_number,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "status": twilio_message.status
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def send_daily_report(self, child_name: str, stats: Dict[str, Any], 
                          to_number: str = None) -> Dict[str, Any]:
        """Send daily summary report to parent"""
        
        message = f"""
📊 Daily Screen Report for {child_name}

Screen Time: {stats.get('total_screen_time', 'N/A')} minutes
Breaks Taken: {stats.get('breaks_taken', 'N/A')}
Warnings: {stats.get('warnings', 'N/A')}
Compliance Rate: {stats.get('compliance_rate', 'N/A')}%

{stats.get('recommendation', '')}

- Screen Time Guardian AI 🛡️
        """.strip()
        
        return self.send_alert(message, to_number)

# Test SMS alerter
if __name__ == "__main__":
    alerter = SMSAlerter()  # Will run in test mode without credentials
    
    # Test alert
    result = alerter.send_alert(
        "⚠️ Leo ignored 3 warnings and screen has been locked.",
        "+1234567890"
    )
    print(f"Alert result: {result}")
    
    # Test daily report
    report = alerter.send_daily_report(
        "Leo",
        {
            "total_screen_time": 120,
            "breaks_taken": 3,
            "warnings": 5,
            "compliance_rate": 60,
            "recommendation": "Try more engaging break activities"
        }
    )
    print(f"Report result: {report}")
