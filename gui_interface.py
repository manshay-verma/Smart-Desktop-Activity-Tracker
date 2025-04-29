"""
GUI Interface Module
Creates a floating sidebar to display user activity in real-time
"""

import os
import time
import logging
import threading
import sys
from datetime import datetime
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QCheckBox, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QPoint, QEvent, QObject
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPalette

from utils import setup_logging
from config import CONFIG

# Setup logging
logger = setup_logging()

class FloatingSidebar(QWidget):
    """
    Floating sidebar UI that displays real-time user activity
    """
    def __init__(self, shared_data, main_app):
        """
        Initialize the floating sidebar
        
        Args:
            shared_data (dict): Shared data dictionary for inter-module communication
            main_app: Reference to the main application
        """
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.shared_data = shared_data
        self.main_app = main_app
        
        # UI State
        self.expanded = False
        self.moving = False
        self.offset = QPoint()
        self.activity_history = []
        self.max_history = 50
        
        # Load settings
        self.sidebar_width = CONFIG.get('sidebar_width', 350)
        self.sidebar_height = CONFIG.get('sidebar_height', 600)
        self.sidebar_opacity = CONFIG.get('sidebar_opacity', 0.85)
        self.auto_hide = CONFIG.get('sidebar_auto_hide', False)
        self.position = CONFIG.get('sidebar_position', 'right')  # 'left' or 'right'
        
        # Setup UI
        self._setup_ui()
        
        # Update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_content)
        self.update_timer.start(1000)  # Update every second
        
        # Auto-hide timer
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.timeout.connect(self.check_auto_hide)
        self.auto_hide_timer.start(5000)  # Check every 5 seconds
        
        logger.info("GUI Interface initialized")
    
    def _setup_ui(self):
        """Setup the sidebar UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # Title bar
        self.title_bar = QFrame(self)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setStyleSheet("""
            #titleBar {
                background-color: #2c3e50;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        self.title_bar_layout = QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(10, 5, 10, 5)
        
        # Title
        self.title_label = QLabel("Smart Desktop Tracker")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        self.title_bar_layout.addWidget(self.title_label)
        
        # Control buttons
        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setFlat(True)
        self.collapse_btn.setStyleSheet("color: white;")
        self.collapse_btn.clicked.connect(self.toggle_expand)
        self.title_bar_layout.addWidget(self.collapse_btn, 0, Qt.AlignRight)
        
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFlat(True)
        self.settings_btn.setStyleSheet("color: white;")
        self.settings_btn.clicked.connect(self.show_settings)
        self.title_bar_layout.addWidget(self.settings_btn, 0, Qt.AlignRight)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFlat(True)
        self.close_btn.setStyleSheet("color: white;")
        self.close_btn.clicked.connect(self.hide)
        self.title_bar_layout.addWidget(self.close_btn, 0, Qt.AlignRight)
        
        self.main_layout.addWidget(self.title_bar)
        
        # Content area
        self.content_frame = QFrame(self)
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setStyleSheet("""
            #contentFrame {
                background-color: #f5f5f5;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(15)
        
        # Current activity section
        self.activity_frame = QFrame()
        self.activity_frame.setObjectName("activityFrame")
        self.activity_frame.setStyleSheet("""
            #activityFrame {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.activity_layout = QVBoxLayout(self.activity_frame)
        
        self.activity_title = QLabel("Current Activity")
        self.activity_title.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.activity_layout.addWidget(self.activity_title)
        
        self.activity_label = QLabel("No activity detected yet...")
        self.activity_label.setWordWrap(True)
        self.activity_layout.addWidget(self.activity_label)
        
        self.content_layout.addWidget(self.activity_frame)
        
        # Applications section
        self.apps_frame = QFrame()
        self.apps_frame.setObjectName("appsFrame")
        self.apps_frame.setStyleSheet("""
            #appsFrame {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.apps_layout = QVBoxLayout(self.apps_frame)
        
        self.apps_title = QLabel("Detected Applications")
        self.apps_title.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.apps_layout.addWidget(self.apps_title)
        
        self.apps_label = QLabel("None detected yet")
        self.apps_label.setWordWrap(True)
        self.apps_layout.addWidget(self.apps_label)
        
        self.content_layout.addWidget(self.apps_frame)
        
        # Suggestions section
        self.suggestions_frame = QFrame()
        self.suggestions_frame.setObjectName("suggestionsFrame")
        self.suggestions_frame.setStyleSheet("""
            #suggestionsFrame {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.suggestions_layout = QVBoxLayout(self.suggestions_frame)
        
        self.suggestions_title = QLabel("Suggestions")
        self.suggestions_title.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.suggestions_layout.addWidget(self.suggestions_title)
        
        self.suggestions_label = QLabel("No suggestions yet")
        self.suggestions_label.setWordWrap(True)
        self.suggestions_layout.addWidget(self.suggestions_label)
        
        self.content_layout.addWidget(self.suggestions_frame)
        
        # Activity history section
        self.history_frame = QFrame()
        self.history_frame.setObjectName("historyFrame")
        self.history_frame.setStyleSheet("""
            #historyFrame {
                background-color: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.history_layout = QVBoxLayout(self.history_frame)
        
        self.history_title = QLabel("Recent Activity")
        self.history_title.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.history_layout.addWidget(self.history_title)
        
        # Scrollable history
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setFrameShape(QFrame.NoFrame)
        
        self.history_content = QWidget()
        self.history_scroll.setWidget(self.history_content)
        
        self.history_content_layout = QVBoxLayout(self.history_content)
        self.history_content_layout.setAlignment(Qt.AlignTop)
        
        self.history_layout.addWidget(self.history_scroll)
        
        self.content_layout.addWidget(self.history_frame)
        
        # Control buttons
        self.button_layout = QHBoxLayout()
        
        self.record_btn = QPushButton("Record Automation")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.button_layout.addWidget(self.record_btn)
        
        self.content_layout.addLayout(self.button_layout)
        
        # Add content to main layout
        self.main_layout.addWidget(self.content_frame)
        
        # Configure window
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(self.sidebar_opacity)
        self.setFixedSize(self.sidebar_width, self.sidebar_height)
        
        # Position the sidebar
        self._position_sidebar()
        
        # Enable mouse events for moving
        self.title_bar.mousePressEvent = self.title_bar_mouse_press
        self.title_bar.mouseMoveEvent = self.title_bar_mouse_move
        self.title_bar.mouseReleaseEvent = self.title_bar_mouse_release
    
    def _position_sidebar(self):
        """Position the sidebar on the screen"""
        screen_geo = QApplication.desktop().availableGeometry()
        screen_width = screen_geo.width()
        screen_height = screen_geo.height()
        
        if self.position == 'right':
            x = screen_width - self.sidebar_width - 10
        else:  # 'left'
            x = 10
        
        y = (screen_height - self.sidebar_height) // 2
        
        self.move(x, y)
    
    def update_content(self):
        """Update the sidebar content with the latest data"""
        try:
            # Update current activity
            current_activity = self.shared_data.get('current_activity', 'No activity detected')
            self.activity_label.setText(current_activity)
            
            # Add to history (if new)
            if current_activity and current_activity not in [item['activity'] for item in self.activity_history]:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.activity_history.append({
                    'timestamp': timestamp,
                    'activity': current_activity
                })
                
                # Limit history length
                if len(self.activity_history) > self.max_history:
                    self.activity_history = self.activity_history[-self.max_history:]
                
                # Update history display
                self._update_history_display()
            
            # Update detected applications
            detected_apps = self.shared_data.get('detected_apps', [])
            if detected_apps:
                self.apps_label.setText(", ".join(detected_apps))
            else:
                self.apps_label.setText("None detected")
            
            # Update suggestions
            suggestions = self.shared_data.get('automation_suggestions', [])
            if suggestions:
                # Clear previous suggestions
                for i in reversed(range(1, self.suggestions_layout.count())):
                    self.suggestions_layout.itemAt(i).widget().setParent(None)
                
                # Display new suggestions (limit to latest 3)
                for i, suggestion in enumerate(suggestions[-3:]):
                    # Create suggestion widget
                    suggestion_widget = QFrame()
                    suggestion_widget.setStyleSheet("background-color: #e8f4fc; border-radius: 5px; padding: 5px;")
                    suggestion_layout = QVBoxLayout(suggestion_widget)
                    
                    # Suggestion text
                    suggestion_text = QLabel(suggestion.get('description', 'No description'))
                    suggestion_text.setWordWrap(True)
                    suggestion_layout.addWidget(suggestion_text)
                    
                    # Action buttons
                    action_layout = QHBoxLayout()
                    
                    if suggestion.get('type', '').startswith('app_'):
                        # App suggestion - provide Open button
                        open_btn = QPushButton("Open")
                        open_btn.clicked.connect(lambda _, app=suggestion.get('app', ''): self.open_suggested_app(app))
                        action_layout.addWidget(open_btn)
                    
                    elif suggestion.get('type', '') == 'window_transition':
                        # Window transition suggestion
                        automate_btn = QPushButton("Automate")
                        automate_btn.clicked.connect(lambda _, s=suggestion: self.automate_suggestion(s))
                        action_layout.addWidget(automate_btn)
                    
                    elif suggestion.get('type', '') == 'click_pattern':
                        # Click pattern suggestion
                        automate_btn = QPushButton("Automate")
                        automate_btn.clicked.connect(lambda _, s=suggestion: self.automate_suggestion(s))
                        action_layout.addWidget(automate_btn)
                    
                    # Add dismiss button to all suggestions
                    dismiss_btn = QPushButton("Dismiss")
                    dismiss_btn.clicked.connect(lambda _, s=suggestion: self.dismiss_suggestion(s))
                    action_layout.addWidget(dismiss_btn)
                    
                    suggestion_layout.addLayout(action_layout)
                    
                    # Add to suggestions section
                    self.suggestions_layout.addWidget(suggestion_widget)
            else:
                # Clear suggestions and show default message
                for i in reversed(range(1, self.suggestions_layout.count())):
                    widget = self.suggestions_layout.itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                
                if self.suggestions_layout.count() == 1:
                    self.suggestions_label = QLabel("No suggestions yet")
                    self.suggestions_label.setWordWrap(True)
                    self.suggestions_layout.addWidget(self.suggestions_label)
            
            # Update recording button state
            is_recording = self.shared_data.get('recording_automation', False)
            if is_recording:
                self.record_btn.setText("Stop Recording")
                self.record_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            else:
                self.record_btn.setText("Record Automation")
                self.record_btn.setStyleSheet("")
        
        except Exception as e:
            logger.error(f"Error updating GUI content: {e}")
    
    def _update_history_display(self):
        """Update the history display with the latest activities"""
        try:
            # Clear previous history items
            for i in reversed(range(self.history_content_layout.count())):
                widget = self.history_content_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Add history items (latest first)
            for item in reversed(self.activity_history):
                history_item = QFrame()
                history_item.setStyleSheet("background-color: #f0f0f0; border-radius: 3px; padding: 5px;")
                item_layout = QVBoxLayout(history_item)
                
                # Timestamp
                timestamp_label = QLabel(item['timestamp'])
                timestamp_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
                item_layout.addWidget(timestamp_label)
                
                # Activity
                activity_label = QLabel(item['activity'])
                activity_label.setWordWrap(True)
                item_layout.addWidget(activity_label)
                
                self.history_content_layout.addWidget(history_item)
        
        except Exception as e:
            logger.error(f"Error updating history display: {e}")
    
    def toggle_expand(self):
        """Toggle between expanded and collapsed states"""
        if self.expanded:
            # Collapse
            self.setFixedWidth(50)
            self.content_frame.hide()
            self.collapse_btn.setText("▶")
            self.expanded = False
        else:
            # Expand
            self.setFixedWidth(self.sidebar_width)
            self.content_frame.show()
            self.collapse_btn.setText("◀")
            self.expanded = True
    
    def title_bar_mouse_press(self, event):
        """Handle mouse press event on the title bar"""
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()
    
    def title_bar_mouse_move(self, event):
        """Handle mouse move event on the title bar"""
        if self.moving and (event.buttons() & Qt.LeftButton):
            self.move(self.mapToParent(event.pos() - self.offset))
    
    def title_bar_mouse_release(self, event):
        """Handle mouse release event on the title bar"""
        if event.button() == Qt.LeftButton:
            self.moving = False
    
    def check_auto_hide(self):
        """Check if the sidebar should auto-hide"""
        if not self.auto_hide or not self.isVisible():
            return
        
        # Get mouse position
        mouse_pos = QApplication.desktop().cursor().pos()
        
        # Check if mouse is near the sidebar
        sidebar_geo = self.geometry()
        extended_geo = sidebar_geo.adjusted(-50, -50, 50, 50)
        
        if not extended_geo.contains(mouse_pos):
            # Mouse is far from sidebar, collapse it
            if not self.expanded:
                return
            
            self.toggle_expand()
        else:
            # Mouse is near sidebar, expand it
            if self.expanded:
                return
            
            self.toggle_expand()
    
    def show_settings(self):
        """Show settings dialog"""
        try:
            settings_dialog = QWidget(self, Qt.Dialog)
            settings_dialog.setWindowTitle("Settings")
            settings_dialog.setFixedSize(300, 200)
            
            settings_layout = QVBoxLayout(settings_dialog)
            
            # Opacity setting
            opacity_layout = QHBoxLayout()
            opacity_label = QLabel("Opacity:")
            opacity_layout.addWidget(opacity_label)
            
            opacity_input = QLineEdit(str(int(self.sidebar_opacity * 100)))
            opacity_input.setValidator(QIntValidator(10, 100))
            opacity_layout.addWidget(opacity_input)
            opacity_layout.addWidget(QLabel("%"))
            
            settings_layout.addLayout(opacity_layout)
            
            # Auto-hide setting
            auto_hide_check = QCheckBox("Auto-hide when mouse is away")
            auto_hide_check.setChecked(self.auto_hide)
            settings_layout.addWidget(auto_hide_check)
            
            # Position setting
            position_layout = QHBoxLayout()
            position_label = QLabel("Position:")
            position_layout.addWidget(position_label)
            
            left_radio = QRadioButton("Left")
            right_radio = QRadioButton("Right")
            
            if self.position == 'left':
                left_radio.setChecked(True)
            else:
                right_radio.setChecked(True)
            
            position_layout.addWidget(left_radio)
            position_layout.addWidget(right_radio)
            
            settings_layout.addLayout(position_layout)
            
            # Buttons
            button_layout = QHBoxLayout()
            save_btn = QPushButton("Save")
            cancel_btn = QPushButton("Cancel")
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            
            settings_layout.addStretch()
            settings_layout.addLayout(button_layout)
            
            # Connect buttons
            save_btn.clicked.connect(lambda: self._save_settings(
                opacity_input.text(),
                auto_hide_check.isChecked(),
                'left' if left_radio.isChecked() else 'right',
                settings_dialog
            ))
            cancel_btn.clicked.connect(settings_dialog.close)
            
            settings_dialog.show()
            
        except Exception as e:
            logger.error(f"Error showing settings: {e}")
    
    def _save_settings(self, opacity, auto_hide, position, dialog):
        """Save settings and apply them"""
        try:
            # Update settings
            self.sidebar_opacity = int(opacity) / 100
            self.auto_hide = auto_hide
            self.position = position
            
            # Apply settings
            self.setWindowOpacity(self.sidebar_opacity)
            self._position_sidebar()
            
            # Save to config
            CONFIG['sidebar_opacity'] = self.sidebar_opacity
            CONFIG['sidebar_auto_hide'] = self.auto_hide
            CONFIG['sidebar_position'] = self.position
            
            # Close dialog
            dialog.close()
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def toggle_recording(self):
        """Toggle automation recording"""
        try:
            is_recording = self.shared_data.get('recording_automation', False)
            
            if is_recording:
                # Stop recording
                automation_name, ok = QInputDialog.getText(self, "Automation Name", 
                                                          "Enter a name for this automation:")
                if ok and automation_name:
                    self.main_app.stop_recording_automation(automation_name)
                else:
                    self.main_app.stop_recording_automation()
                
                QMessageBox.information(self, "Recording Stopped", 
                                       "Automation recording has been stopped and saved.")
            else:
                # Start recording
                success = self.main_app.record_new_automation()
                if success:
                    QMessageBox.information(self, "Recording Started", 
                                           "Automation recording has started. Perform the actions you want to automate.")
                else:
                    QMessageBox.warning(self, "Recording Error", 
                                       "Failed to start automation recording.")
            
        except Exception as e:
            logger.error(f"Error toggling recording: {e}")
    
    def open_suggested_app(self, app_name):
        """Open a suggested application"""
        try:
            # This is a placeholder - in a real implementation, you would launch the app
            QMessageBox.information(self, "Launch App", 
                                   f"Would launch {app_name} here in a real implementation.")
            
            # Remove this suggestion from the list
            suggestions = self.shared_data.get('automation_suggestions', [])
            self.shared_data['automation_suggestions'] = [s for s in suggestions 
                                                         if not (s.get('type', '').startswith('app_') and 
                                                                s.get('app', '') == app_name)]
            
        except Exception as e:
            logger.error(f"Error opening suggested app: {e}")
    
    def automate_suggestion(self, suggestion):
        """Automate a suggested action"""
        try:
            suggestion_type = suggestion.get('type', '')
            
            if suggestion_type == 'window_transition':
                source = suggestion.get('source_window', '')
                dest = suggestion.get('destination_window', '')
                
                QMessageBox.information(self, "Automate Window Transition", 
                                       f"Would create automation to switch from '{source}' to '{dest}'.")
                
            elif suggestion_type == 'click_pattern':
                window = suggestion.get('window', '')
                position = suggestion.get('position', (0, 0))
                
                QMessageBox.information(self, "Automate Click", 
                                       f"Would create automation to click at {position} in '{window}'.")
            
            # Remove this suggestion from the list
            suggestions = self.shared_data.get('automation_suggestions', [])
            self.shared_data['automation_suggestions'] = [s for s in suggestions if s != suggestion]
            
        except Exception as e:
            logger.error(f"Error automating suggestion: {e}")
    
    def dismiss_suggestion(self, suggestion):
        """Dismiss a suggestion"""
        try:
            # Remove from suggestions list
            suggestions = self.shared_data.get('automation_suggestions', [])
            self.shared_data['automation_suggestions'] = [s for s in suggestions if s != suggestion]
            
        except Exception as e:
            logger.error(f"Error dismissing suggestion: {e}")

class GUIInterface:
    """
    GUI Interface controller that manages the floating sidebar
    """
    def __init__(self, shared_data, main_app):
        """
        Initialize the GUI interface
        
        Args:
            shared_data (dict): Shared data dictionary for inter-module communication
            main_app: Reference to the main application
        """
        self.shared_data = shared_data
        self.main_app = main_app
        self.app = None
        self.sidebar = None
        
        logger.info("GUI Interface initialized")
    
    def start(self):
        """Start the GUI interface"""
        logger.info("Starting GUI interface")
        
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        # Create sidebar
        self.sidebar = FloatingSidebar(self.shared_data, self.main_app)
        self.sidebar.show()
        
        # Start event loop if this is the main thread
        if threading.current_thread() is threading.main_thread():
            sys.exit(self.app.exec_())
    
    def stop(self):
        """Stop the GUI interface"""
        logger.info("Stopping GUI interface")
        if self.sidebar:
            self.sidebar.close()
    
    def update_display(self):
        """Update the sidebar display (called from main app)"""
        if self.sidebar:
            QTimer.singleShot(0, self.sidebar.update_content)
