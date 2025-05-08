"""
Repetitive Task Suggestion Module
Detects patterns in user behavior and suggests automations
"""

import os
import time
import logging
import threading
import json
from datetime import datetime, timedelta
import re
from collections import defaultdict, Counter

from utils import setup_logging
from config import CONFIG

# Setup logging
logger = setup_logging()

class RepetitiveTaskSuggestion:
    """
    Analyzes user behavior to detect repetitive tasks and suggest automations
    """
    def __init__(self, data_dir, shared_data):
        """
        Initialize the repetitive task suggestion module
        
        Args:
            data_dir (str): Directory for suggestion data
            shared_data (dict): Shared data dictionary for inter-module communication
        """
        self.data_dir = data_dir
        self.shared_data = shared_data
        self.running = False
        
        # Create suggestions directory
        self.suggestions_dir = os.path.join(data_dir, "suggestions")
        if not os.path.exists(self.suggestions_dir):
            os.makedirs(self.suggestions_dir)
        
        # Pattern detection settings
        self.min_repetitions = CONFIG.get('min_repetitions_for_suggestion', 3)
        self.time_window = CONFIG.get('task_time_window', 24 * 60 * 60)  # 24 hours in seconds
        self.analysis_interval = CONFIG.get('suggestion_analysis_interval', 5 * 60)  # 5 minutes
        
        # Data structures for pattern detection
        self.activity_sequence = []
        self.window_sequences = defaultdict(list)
        self.click_patterns = defaultdict(int)
        self.app_usage_patterns = defaultdict(lambda: defaultdict(int))
        self.time_patterns = defaultdict(lambda: defaultdict(int))
        
        # Load historical data
        self._load_historical_data()
        
        logger.info("Repetitive Task Suggestion Module initialized")
    
    def start_monitoring(self):
        """Start pattern monitoring"""
        logger.info("Starting repetitive task suggestion monitoring")
        self.running = True
        
        # Main monitoring loop
        while self.running:
            try:
                # Analyze patterns periodically
                self._analyze_patterns()
                
                # Check for timing-based suggestions
                self._check_time_based_suggestions()
                
                # Update activity sequence with current activity
                self._update_activity_sequence()
                
                # Sleep before next analysis
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Error in task suggestion monitoring: {e}")
                time.sleep(60)  # Sleep longer on error
    
    def stop(self):
        """Stop monitoring"""
        logger.info("Stopping repetitive task suggestion monitoring")
        self.running = False
        
        # Save data before stopping
        self._save_pattern_data()
    
    def get_suggestions(self):
        """
        Get current automation suggestions
        
        Returns:
            list: List of automation suggestions
        """
        return self.shared_data.get('automation_suggestions', [])
    
    def _update_activity_sequence(self):
        """Update the activity sequence with current activity"""
        try:
            # Get current activity data
            current_window = self.shared_data.get('active_window', '')
            detected_apps = self.shared_data.get('detected_apps', [])
            mouse_pos = self.shared_data.get('mouse_position', (0, 0))
            
            # Record activity event
            activity = {
                'timestamp': time.time(),
                'window': current_window,
                'apps': detected_apps,
                'mouse_position': mouse_pos
            }
            
            # Add to sequence
            self.activity_sequence.append(activity)
            
            # Limit sequence length to avoid memory issues
            if len(self.activity_sequence) > 1000:
                self.activity_sequence = self.activity_sequence[-1000:]
            
            # Record window transition
            if len(self.activity_sequence) > 1:
                prev_window = self.activity_sequence[-2]['window']
                if prev_window != current_window:
                    # Record window transition sequence
                    self.window_sequences[prev_window].append(current_window)
                    
                    # Limit sequence length
                    if len(self.window_sequences[prev_window]) > 100:
                        self.window_sequences[prev_window] = self.window_sequences[prev_window][-100:]
            
            # Record app usage by hour of day
            hour = datetime.now().hour
            for app in detected_apps:
                self.app_usage_patterns[app][hour] += 1
            
        except Exception as e:
            logger.error(f"Error updating activity sequence: {e}")
    
    def _analyze_patterns(self):
        """Analyze collected data for patterns"""
        try:
            suggestions = []
            
            # Analyze window transition patterns
            window_suggestions = self._analyze_window_transitions()
            if window_suggestions:
                suggestions.extend(window_suggestions)
            
            # Analyze click patterns
            click_suggestions = self._analyze_click_patterns()
            if click_suggestions:
                suggestions.extend(click_suggestions)
            
            # Analyze app usage patterns
            app_suggestions = self._analyze_app_usage_patterns()
            if app_suggestions:
                suggestions.extend(app_suggestions)
            
            # Update shared data with suggestions
            self.shared_data['automation_suggestions'] = suggestions
            
            # Save suggestions to file
            self._save_suggestions(suggestions)
            
            logger.debug(f"Found {len(suggestions)} automation suggestions")
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
    
    def _analyze_window_transitions(self):
        """
        Analyze window transition patterns
        
        Returns:
            list: Window transition suggestions
        """
        suggestions = []
        
        for source, destinations in self.window_sequences.items():
            # Count frequency of transitions
            transition_counts = Counter(destinations)
            
            # Find common transitions (more than min_repetitions)
            for dest, count in transition_counts.items():
                if count >= self.min_repetitions:
                    # Check if the transition is within a workflow
                    # e.g., File Explorer -> Visual Studio Code -> Browser
                    suggestion = {
                        'type': 'window_transition',
                        'description': f"You often switch from '{source}' to '{dest}'",
                        'source_window': source,
                        'destination_window': dest,
                        'confidence': min(count / 10, 0.95),  # Cap at 95%
                        'count': count,
                        'suggestion': f"Would you like to automate opening '{dest}' after '{source}'?"
                    }
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _analyze_click_patterns(self):
        """
        Analyze mouse click patterns
        
        Returns:
            list: Click pattern suggestions
        """
        suggestions = []
        
        # Load click data from files
        clicks_file = os.path.join(self.data_dir, "mouse_clicks.json")
        if not os.path.exists(clicks_file):
            return suggestions
        
        try:
            with open(clicks_file, 'r') as f:
                clicks = json.load(f)
            
            # Group clicks by window
            clicks_by_window = defaultdict(list)
            for click in clicks:
                window = click.get('active_window', '')
                if window:
                    clicks_by_window[window].append(click)
            
            # Analyze common click patterns in each window
            for window, window_clicks in clicks_by_window.items():
                # Skip if too few clicks
                if len(window_clicks) < self.min_repetitions:
                    continue
                
                # Simplify by looking at regions of the screen (divide into grid)
                screen_width, screen_height = pyautogui.size()
                grid_size = 10
                cell_width = screen_width / grid_size
                cell_height = screen_height / grid_size
                
                # Map clicks to grid cells
                grid_clicks = []
                for click in window_clicks:
                    x, y = click.get('position', (0, 0))
                    cell_x = int(x / cell_width)
                    cell_y = int(y / cell_height)
                    grid_clicks.append((cell_x, cell_y))
                
                # Count frequency of grid cells
                cell_counts = Counter(grid_clicks)
                
                # Find common click locations
                for cell, count in cell_counts.items():
                    if count >= self.min_repetitions:
                        cell_x, cell_y = cell
                        center_x = int((cell_x + 0.5) * cell_width)
                        center_y = int((cell_y + 0.5) * cell_height)
                        
                        suggestion = {
                            'type': 'click_pattern',
                            'description': f"You often click in the same area in '{window}'",
                            'window': window,
                            'position': (center_x, center_y),
                            'confidence': min(count / 10, 0.9),  # Cap at 90%
                            'count': count,
                            'suggestion': f"Would you like to automate clicking this area in '{window}'?"
                        }
                        suggestions.append(suggestion)
        
        except Exception as e:
            logger.error(f"Error analyzing click patterns: {e}")
        
        return suggestions
    
    def _analyze_app_usage_patterns(self):
        """
        Analyze application usage patterns
        
        Returns:
            list: App usage pattern suggestions
        """
        suggestions = []
        
        # Analyze app usage by time of day
        for app, hours in self.app_usage_patterns.items():
            # Find peak usage hours
            peak_hour = max(hours.items(), key=lambda x: x[1], default=(0, 0))
            hour, count = peak_hour
            
            # If used at least min_repetitions times in this hour
            if count >= self.min_repetitions:
                # Format hour for display
                hour_str = f"{hour}:00"
                
                suggestion = {
                    'type': 'app_time_pattern',
                    'description': f"You often use '{app}' around {hour_str}",
                    'app': app,
                    'hour': hour,
                    'confidence': min(count / 10, 0.8),  # Cap at 80%
                    'count': count,
                    'suggestion': f"Would you like to automatically open '{app}' at {hour_str}?"
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def _check_time_based_suggestions(self):
        """Check for time-based suggestions"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            
            suggestions = []
            
            # Check app usage patterns for the current hour
            for app, hours in self.app_usage_patterns.items():
                count = hours.get(current_hour, 0)
                
                # If the app is commonly used at this hour but not currently open
                if count >= self.min_repetitions and app not in self.shared_data.get('detected_apps', []):
                    suggestion = {
                        'type': 'time_based_suggestion',
                        'description': f"You usually use '{app}' at this time",
                        'app': app,
                        'hour': current_hour,
                        'confidence': min(count / 10, 0.8),  # Cap at 80%
                        'count': count,
                        'suggestion': f"Would you like to open '{app}' now?"
                    }
                    suggestions.append(suggestion)
            
            # Add time-based suggestions to shared data
            if suggestions:
                current_suggestions = self.shared_data.get('automation_suggestions', [])
                # Add only new suggestions
                for suggestion in suggestions:
                    if suggestion not in current_suggestions:
                        current_suggestions.append(suggestion)
                self.shared_data['automation_suggestions'] = current_suggestions
            
        except Exception as e:
            logger.error(f"Error checking time-based suggestions: {e}")
    
    def _load_historical_data(self):
        """Load historical pattern data"""
        try:
            # Load pattern data file
            pattern_file = os.path.join(self.suggestions_dir, "pattern_data.json")
            if os.path.exists(pattern_file):
                with open(pattern_file, 'r') as f:
                    data = json.load(f)
                
                # Load window sequences
                if 'window_sequences' in data:
                    self.window_sequences = defaultdict(list)
                    for source, destinations in data['window_sequences'].items():
                        self.window_sequences[source] = destinations
                
                # Load click patterns
                if 'click_patterns' in data:
                    self.click_patterns = defaultdict(int)
                    for pattern, count in data['click_patterns'].items():
                        self.click_patterns[pattern] = count
                
                # Load app usage patterns
                if 'app_usage_patterns' in data:
                    self.app_usage_patterns = defaultdict(lambda: defaultdict(int))
                    for app, hours in data['app_usage_patterns'].items():
                        for hour, count in hours.items():
                            self.app_usage_patterns[app][int(hour)] = count
                
                # Load time patterns
                if 'time_patterns' in data:
                    self.time_patterns = defaultdict(lambda: defaultdict(int))
                    for day, hours in data['time_patterns'].items():
                        for hour, count in hours.items():
                            self.time_patterns[day][int(hour)] = count
                
                logger.info("Loaded historical pattern data")
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
    
    def _save_pattern_data(self):
        """Save pattern data for future use"""
        try:
            # Prepare data for saving
            data = {
                'window_sequences': {k: v for k, v in self.window_sequences.items()},
                'click_patterns': {k: v for k, v in self.click_patterns.items()},
                'app_usage_patterns': {
                    app: {str(hour): count for hour, count in hours.items()}
                    for app, hours in self.app_usage_patterns.items()
                },
                'time_patterns': {
                    day: {str(hour): count for hour, count in hours.items()}
                    for day, hours in self.time_patterns.items()
                }
            }
            
            # Save to file
            pattern_file = os.path.join(self.suggestions_dir, "pattern_data.json")
            with open(pattern_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Pattern data saved")
            
        except Exception as e:
            logger.error(f"Error saving pattern data: {e}")
    
    def _save_suggestions(self, suggestions):
        """
        Save current suggestions to file
        
        Args:
            suggestions (list): Current suggestions
        """
        try:
            if not suggestions:
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suggestion_file = os.path.join(self.suggestions_dir, f"suggestions_{timestamp}.json")
            
            with open(suggestion_file, 'w') as f:
                json.dump({
                    'timestamp': timestamp,
                    'suggestions': suggestions
                }, f, indent=2)
            
            logger.debug(f"Saved {len(suggestions)} suggestions to {suggestion_file}")
            
        except Exception as e:
            logger.error(f"Error saving suggestions: {e}")
