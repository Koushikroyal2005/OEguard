"""
Desktop Popup Overlay System
Shows full-screen warnings to the child
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional

class WarningPopup:
    """Full-screen warning overlay"""
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.active = False
        self.countdown = 0
        
    def show_warning(self, message: str, urgency: str = "normal", 
                     duration: int = 10, callback=None):
        """
        Display a warning popup
        
        Args:
            message: Warning message
            urgency: 'gentle', 'normal', 'urgent'
            duration: Display duration in seconds
            callback: Function to call when popup closes
        """
        if self.active:
            return {"displayed": False, "reason": "Popup already active"}
        
        # Color schemes based on urgency
        colors = {
            "gentle": {"bg": "#E8F5E9", "fg": "#2E7D32", "border": "#4CAF50"},
            "normal": {"bg": "#FFF3E0", "fg": "#E65100", "border": "#FF9800"},
            "urgent": {"bg": "#FFEBEE", "fg": "#C62828", "border": "#F44336"}
        }
        
        theme = colors.get(urgency, colors["normal"])
        
        def create_popup():
            self.active = True
            self.root = tk.Tk()
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)
            self.root.configure(bg=theme["bg"])
            
            # Disable closing
            self.root.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # Main container
            container = tk.Frame(self.root, bg=theme["bg"], padx=40, pady=40)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            # Warning icon
            icons = {"gentle": "😊", "normal": "⚠️", "urgent": "🚨"}
            icon_label = tk.Label(
                container, 
                text=icons.get(urgency, "⚠️"),
                font=("Arial", 80),
                bg=theme["bg"]
            )
            icon_label.pack(pady=20)
            
            # Main message
            msg_label = tk.Label(
                container,
                text=message,
                font=("Arial", 24, "bold"),
                fg=theme["fg"],
                bg=theme["bg"],
                wraplength=800,
                justify="center"
            )
            msg_label.pack(pady=20)
            
            # Countdown timer
            self.countdown_label = tk.Label(
                container,
                text=f"Screen will return in {self.countdown} seconds",
                font=("Arial", 16),
                fg=theme["fg"],
                bg=theme["bg"]
            )
            self.countdown_label.pack(pady=10)
            
            # Progress bar
            self.progress = ttk.Progressbar(
                container,
                length=400,
                mode='determinate',
                maximum=duration
            )
            self.progress.pack(pady=20)
            
            # Start countdown
            self.countdown = duration
            self._update_countdown(duration, callback)
            
            self.root.mainloop()
        
        # Run in separate thread to not block main program
        thread = threading.Thread(target=create_popup, daemon=True)
        thread.start()
        
        return {"displayed": True, "message": message, "duration": duration}
    
    def _update_countdown(self, remaining: int, callback):
        """Update countdown timer"""
        if remaining > 0 and self.active:
            self.countdown = remaining
            self.countdown_label.config(
                text=f"Screen will return in {remaining} seconds"
            )
            self.progress['value'] = self.progress['maximum'] - remaining
            self.root.after(1000, self._update_countdown, remaining - 1, callback)
        else:
            self.close(callback)
    
    def close(self, callback=None):
        """Close the popup"""
        self.active = False
        if self.root:
            self.root.destroy()
            self.root = None
        if callback:
            callback()
    
    def show_break_complete(self):
        """Show break completion message"""
        if self.root:
            for widget in self.root.winfo_children():
                widget.destroy()
            
            tk.Label(
                self.root,
                text="🎉 Great job! Break complete!\nScreen unlocking...",
                font=("Arial", 30, "bold"),
                fg="#2E7D32",
                bg="#E8F5E9"
            ).place(relx=0.5, rely=0.5, anchor="center")
            
            self.root.after(3000, self.close)

# Test popup
if __name__ == "__main__":
    popup = WarningPopup()
    popup.show_warning(
        "Hey Leo! Sonic says your eyes need a break! 👀\nLook away for 10 seconds!",
        urgency="normal",
        duration=10
    )
    print("Popup displayed!")
