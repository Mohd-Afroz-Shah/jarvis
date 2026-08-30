"""
Optimization Module - Phase 10

Efficient screen/UI inspection for J1.
Prevents redundant calls to read_screen and read_ui.
"""

from datetime import datetime, timedelta


class UIState:
    """Track the current UI state to avoid redundant inspections."""
    
    def __init__(self):
        self.last_screenshot = None
        self.last_screenshot_time = None
        self.last_ui_dump = None
        self.last_ui_dump_time = None
        self.active_window = None
        self.cache_ttl = 5  # seconds
    
    def is_screenshot_fresh(self):
        """Check if we have a fresh screenshot."""
        if self.last_screenshot_time is None:
            return False
        
        age = (datetime.now() - self.last_screenshot_time).total_seconds()
        return age < self.cache_ttl
    
    def is_ui_dump_fresh(self):
        """Check if we have a fresh UI dump."""
        if self.last_ui_dump_time is None:
            return False
        
        age = (datetime.now() - self.last_ui_dump_time).total_seconds()
        return age < self.cache_ttl
    
    def update_screenshot(self, screenshot_data):
        """Update the cached screenshot."""
        self.last_screenshot = screenshot_data
        self.last_screenshot_time = datetime.now()
    
    def update_ui_dump(self, ui_data):
        """Update the cached UI dump."""
        self.last_ui_dump = ui_data
        self.last_ui_dump_time = datetime.now()
        
        if "window" in ui_data:
            self.active_window = ui_data["window"]
    
    def invalidate_all(self):
        """Invalidate all cached data (e.g., after significant action)."""
        self.last_screenshot = None
        self.last_screenshot_time = None
        self.last_ui_dump = None
        self.last_ui_dump_time = None
    
    def should_read_screen(self):
        """Determine if we should read the screen."""
        return not self.is_screenshot_fresh()
    
    def should_read_ui(self):
        """Determine if we should read the UI."""
        return not self.is_ui_dump_fresh()


class InspectionOptimizer:
    """Optimize screen and UI inspection patterns."""
    
    def __init__(self):
        self.ui_state = UIState()
        self.recent_actions = []
        self.significant_actions = [
            "open_app",
            "press_key",
            "hotkey",
            "click_ui",
            "tap",
        ]
    
    def log_action(self, action_name):
        """Log an action that might change UI state."""
        self.recent_actions.append({
            "action": action_name,
            "time": datetime.now()
        })
        
        # Keep only recent actions
        cutoff = datetime.now() - timedelta(seconds=10)
        self.recent_actions = [a for a in self.recent_actions if a["time"] > cutoff]
        
        # Invalidate cache if significant action was performed
        if action_name in self.significant_actions:
            self.ui_state.invalidate_all()
    
    def recommend_inspection(self, next_action):
        """
        Recommend whether to inspect before the next action.
        
        Args:
            next_action (str): The next planned action
        
        Returns:
            dict: Recommendation with 'should_read_screen' and 'should_read_ui'
        """
        
        recommendation = {
            "should_read_screen": False,
            "should_read_ui": False,
            "reason": ""
        }
        
        # For clicking, prefer UI inspection if fresh
        if next_action in ["click_ui", "type_ui"]:
            if not self.ui_state.is_ui_dump_fresh():
                recommendation["should_read_ui"] = True
                recommendation["reason"] = "UI information needed for precise clicking"
        
        # For coordinate-based clicks, need fresh screenshot
        elif next_action == "tap":
            if not self.ui_state.is_screenshot_fresh():
                recommendation["should_read_screen"] = True
                recommendation["reason"] = "Screenshot needed for coordinate selection"
        
        # For typing, make sure we're in the right context
        elif next_action == "type_text":
            if not self.ui_state.is_ui_dump_fresh():
                recommendation["should_read_ui"] = True
                recommendation["reason"] = "Verify focused element before typing"
        
        # After opening an app, always inspect
        if self.recent_actions and self.recent_actions[-1]["action"] == "open_app":
            recommendation["should_read_ui"] = True
            recommendation["reason"] = "Application just opened, need UI inspection"
        
        return recommendation
    
    def should_cache_result(self, tool_name):
        """Determine if tool result should be cached."""
        cacheable_tools = ["read_screen", "read_ui"]
        return tool_name in cacheable_tools
    
    def get_cached_result(self, tool_name):
        """Get cached result if available."""
        if tool_name == "read_screen" and self.ui_state.is_screenshot_fresh():
            return ("cached", self.ui_state.last_screenshot)
        elif tool_name == "read_ui" and self.ui_state.is_ui_dump_fresh():
            return ("cached", self.ui_state.last_ui_dump)
        
        return (None, None)


# Global optimizer instance
optimizer = InspectionOptimizer()


def get_optimizer():
    """Get the global optimizer instance."""
    return optimizer


def optimize_inspection_sequence(planned_actions):
    """
    Optimize a sequence of planned actions to reduce redundant inspections.
    
    Args:
        planned_actions (list): List of action names
    
    Returns:
        list: Optimized action sequence with inspection recommendations
    """
    
    optimized = []
    opt = get_optimizer()
    
    for i, action in enumerate(planned_actions):
        recommendation = opt.recommend_inspection(action)
        
        # Add inspection if recommended
        if recommendation["should_read_screen"]:
            optimized.append(("read_screen", recommendation["reason"]))
        if recommendation["should_read_ui"]:
            optimized.append(("read_ui", recommendation["reason"]))
        
        # Add the actual action
        optimized.append((action, None))
    
    return optimized
