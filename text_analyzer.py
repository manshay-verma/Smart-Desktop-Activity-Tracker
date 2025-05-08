<<<<<<< HEAD
"""
Text Analyzer Module
Analyzes screenshots using OCR and extracts text information
"""

import os
import time
import logging
import threading
import json
from datetime import datetime
import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
import requests
from bs4 import BeautifulSoup

from utils import setup_logging
from config import CONFIG

# Setup logging
logger = setup_logging()

class TextAnalyzer:
    """
    Analyzes screenshots to extract text and identify applications
    """
    def __init__(self, data_dir, shared_data):
        """
        Initialize the text analyzer
        
        Args:
            data_dir (str): Directory for analyzed data
            shared_data (dict): Shared data dictionary for inter-module communication
        """
        self.data_dir = data_dir
        self.shared_data = shared_data
        self.running = False
        
        # OCR and analysis settings
        self.analysis_interval = CONFIG.get('text_analysis_interval', 2)  # seconds
        
        # Configure pytesseract path if running on Windows
        if os.name == 'nt':
            pytesseract_path = CONFIG.get('pytesseract_path', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
            if os.path.exists(pytesseract_path):
                pytesseract.pytesseract.tesseract_cmd = pytesseract_path
        
        # Create analysis directory
        self.analysis_dir = os.path.join(data_dir, "text_analysis")
        if not os.path.exists(self.analysis_dir):
            os.makedirs(self.analysis_dir)
        
        # Application recognition
        self.known_apps = {
            "chrome": "Google Chrome",
            "firefox": "Mozilla Firefox",
            "edge": "Microsoft Edge",
            "word": "Microsoft Word",
            "excel": "Microsoft Excel",
            "powerpoint": "PowerPoint",
            "vscode": "Visual Studio Code",
            "notepad": "Notepad",
            "explorer": "File Explorer",
            "photoshop": "Adobe Photoshop",
            "outlook": "Microsoft Outlook",
            "spotify": "Spotify",
            "discord": "Discord",
            "slack": "Slack",
            "terminal": "Terminal/Command Prompt",
        }
        
        # Window detection for segmenting screenshots
        self.window_detection_enabled = CONFIG.get('window_detection_enabled', True)
        
        logger.info("Text Analyzer initialized")
    
    def start_analysis(self):
        """Start text analysis loop"""
        logger.info("Starting text analysis")
        self.running = True
        
        # Main analysis loop
        while self.running:
            try:
                # Wait for new screenshot
                screenshot_path = self.shared_data.get('last_screenshot_path')
                if screenshot_path and os.path.exists(screenshot_path):
                    # Analyze the screenshot
                    self._analyze_screenshot(screenshot_path)
                
                # Also check for click area if available
                click_area_path = self.shared_data.get('last_click_area_path')
                if click_area_path and os.path.exists(click_area_path):
                    # Analyze the click area (higher priority)
                    self._analyze_click_area(click_area_path)
                
                # Sleep before next analysis
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Error in text analysis: {e}")
                time.sleep(1)  # Sleep on error to avoid tight loops
    
    def stop(self):
        """Stop analysis"""
        logger.info("Stopping text analysis")
        self.running = False
    
    def _analyze_screenshot(self, screenshot_path):
        """
        Analyze a full screenshot to extract text and detect applications
        
        Args:
            screenshot_path (str): Path to the screenshot file
        """
        try:
            # Load the image
            image = cv2.imread(screenshot_path)
            if image is None:
                logger.error(f"Failed to load image: {screenshot_path}")
                return
            
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply some preprocessing to improve OCR
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # If window detection is enabled, try to segment the image
            if self.window_detection_enabled:
                window_regions = self._detect_window_regions(gray)
                results = []
                
                # Process each detected window region
                for i, region in enumerate(window_regions):
                    region_text = pytesseract.image_to_string(region)
                    results.append({
                        'region_id': f"window_{i+1}",
                        'text': region_text.strip(),
                        'detected_apps': self._detect_applications(region_text)
                    })
                
                # Check which region contains the mouse pointer
                mouse_pos = self.shared_data.get('mouse_position', (0, 0))
                active_region_id = self._find_region_with_mouse(window_regions, mouse_pos)
                
                # Find active region text
                active_region_text = "No text detected"
                active_region_apps = []
                for result in results:
                    if result['region_id'] == active_region_id:
                        active_region_text = result['text']
                        active_region_apps = result['detected_apps']
                
                # Update shared data with active region text
                self.shared_data['latest_ocr_text'] = active_region_text
                self.shared_data['detected_apps'] = active_region_apps
                
                # Generate natural language description
                description = self._generate_description(active_region_text, active_region_apps)
                self.shared_data['current_activity'] = description
                
            else:
                # Process the entire image if window detection is disabled
                text = pytesseract.image_to_string(gray)
                detected_apps = self._detect_applications(text)
                
                # Update shared data
                self.shared_data['latest_ocr_text'] = text.strip()
                self.shared_data['detected_apps'] = detected_apps
                
                # Generate natural language description
                description = self._generate_description(text, detected_apps)
                self.shared_data['current_activity'] = description
            
            # Save analysis results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = os.path.join(self.analysis_dir, f"analysis_{timestamp}.json")
            
            with open(result_file, 'w') as f:
                json.dump({
                    'timestamp': timestamp,
                    'screenshot': os.path.basename(screenshot_path),
                    'ocr_text': self.shared_data['latest_ocr_text'],
                    'detected_apps': self.shared_data['detected_apps'],
                    'description': self.shared_data['current_activity'],
                    'active_window': self.shared_data.get('active_window', '')
                }, f, indent=2)
            
            logger.debug(f"Screenshot analysis completed: {os.path.basename(screenshot_path)}")
            
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {e}")
    
    def _analyze_click_area(self, click_area_path):
        """
        Analyze an area around a mouse click
        
        Args:
            click_area_path (str): Path to the click area image
        """
        try:
            # Load the image
            image = cv2.imread(click_area_path)
            if image is None:
                logger.error(f"Failed to load click area image: {click_area_path}")
                return
            
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply some preprocessing to improve OCR
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # Run OCR on the click area
            text = pytesseract.image_to_string(gray)
            detected_apps = self._detect_applications(text)
            
            # Update shared data for the click area (higher priority)
            self.shared_data['click_area_text'] = text.strip()
            if detected_apps:
                self.shared_data['detected_apps'] = detected_apps
            
            # Generate specific description for what was clicked
            click_description = self._generate_click_description(text, detected_apps)
            self.shared_data['click_activity'] = click_description
            
            logger.debug(f"Click area analysis completed: {os.path.basename(click_area_path)}")
            
        except Exception as e:
            logger.error(f"Error analyzing click area: {e}")
    
    def _detect_window_regions(self, image):
        """
        Detect window regions in the screenshot
        
        Args:
            image (numpy.ndarray): Grayscale image
        
        Returns:
            list: List of detected window regions (numpy arrays)
        """
        try:
            # Apply edge detection
            edges = cv2.Canny(image, 50, 150)
            
            # Dilate to connect edges
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(edges, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size (to avoid small UI elements)
            min_area = image.shape[0] * image.shape[1] * 0.05  # Min 5% of screen
            large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
            
            # If no large contours found, use the whole image
            if not large_contours:
                return [image]
            
            # Extract regions for each contour
            regions = []
            for contour in large_contours:
                x, y, w, h = cv2.boundingRect(contour)
                region = image[y:y+h, x:x+w]
                regions.append(region)
            
            return regions
            
        except Exception as e:
            logger.error(f"Error detecting window regions: {e}")
            return [image]  # Return the whole image on error
    
    def _find_region_with_mouse(self, regions, mouse_pos):
        """
        Find which region contains the mouse pointer
        
        Args:
            regions (list): List of detected regions
            mouse_pos (tuple): Mouse position (x, y)
        
        Returns:
            str: Region ID containing the mouse
        """
        # Implementation would require tracking region coordinates
        # For now, return a default value
        return "window_1"
    
    def _detect_applications(self, text):
        """
        Detect applications from OCR text
        
        Args:
            text (str): OCR text
        
        Returns:
            list: List of detected applications
        """
        detected = []
        text_lower = text.lower()
        
        # Check for known application names in the text
        for key, app_name in self.known_apps.items():
            if key in text_lower or app_name.lower() in text_lower:
                detected.append(app_name)
        
        # Get application from active window title
        active_window = self.shared_data.get('active_window', '')
        for key, app_name in self.known_apps.items():
            if key in active_window.lower() or app_name.lower() in active_window.lower():
                if app_name not in detected:
                    detected.append(app_name)
        
        return detected
    
    def _generate_description(self, text, detected_apps):
        """
        Generate natural language description of current activity
        
        Args:
            text (str): OCR text
            detected_apps (list): Detected applications
        
        Returns:
            str: Natural language description
        """
        # Get active window
        active_window = self.shared_data.get('active_window', 'an application')
        
        # Extract active app from window title
        active_app = "an application"
        for app in detected_apps:
            if app.lower() in active_window.lower():
                active_app = app
                break
        
        # Simplify active window title (remove process info)
        if " (" in active_window:
            active_window = active_window.split(" (")[0]
        
        # Generate description based on context
        if "explorer" in active_window.lower() or "file explorer" in detected_apps:
            return f"You are browsing files in {active_window}"
        
        elif "chrome" in active_window.lower() or "firefox" in active_window.lower() or "edge" in active_window.lower():
            # Extract potential URL or web content
            url_match = re.search(r'https?://[^\s]+', text)
            if url_match:
                url = url_match.group(0)
                return f"You are visiting {url} in {active_app}"
            else:
                return f"You are browsing the web using {active_app}"
        
        elif "word" in active_window.lower() or "document" in active_window.lower():
            return f"You are editing a document in {active_app}"
        
        elif "excel" in active_window.lower() or "spreadsheet" in active_window.lower():
            return f"You are working with a spreadsheet in {active_app}"
        
        elif "powerpoint" in active_window.lower() or "presentation" in active_window.lower():
            return f"You are working on a presentation in {active_app}"
        
        elif "code" in active_window.lower() or "visual studio" in active_window.lower():
            # Try to detect programming language
            if "def " in text or "class " in text or "import " in text:
                return f"You are coding in Python using {active_app}"
            elif "function" in text or "const " in text or "var " in text or "let " in text:
                return f"You are coding in JavaScript/TypeScript using {active_app}"
            elif "public class" in text or "private void" in text:
                return f"You are coding in Java/C# using {active_app}"
            else:
                return f"You are coding using {active_app}"
        
        elif "terminal" in active_window.lower() or "cmd" in active_window.lower() or "powershell" in active_window.lower():
            return f"You are using the command line in {active_window}"
        
        elif "spotify" in active_window.lower() or "music" in active_window.lower():
            return f"You are listening to music in {active_app}"
        
        elif "outlook" in active_window.lower() or "mail" in active_window.lower():
            return f"You are checking your email in {active_app}"
        
        else:
            # Generic description
            apps_str = ", ".join(detected_apps) if detected_apps else "an application"
            return f"You are using {apps_str} - {active_window}"
    
    def _generate_click_description(self, text, detected_apps):
        """
        Generate description of what was clicked
        
        Args:
            text (str): OCR text from click area
            detected_apps (list): Detected applications
        
        Returns:
            str: Description of click action
        """
        # Simplify text by removing extra whitespace
        text = ' '.join(text.strip().split())
        
        # If text is too long, truncate it
        if len(text) > 50:
            text = text[:47] + "..."
        
        # Generate description based on content
        if not text or text.isspace():
            return "You clicked on an area with no text"
        
        # Try to identify common UI elements
        if any(button in text.lower() for button in ["ok", "cancel", "yes", "no", "submit", "save"]):
            button = next(b for b in ["ok", "cancel", "yes", "no", "submit", "save"] 
                        if b in text.lower())
            return f"You clicked the '{button.capitalize()}' button"
        
        elif "menu" in text.lower():
            return f"You clicked on a menu item: '{text}'"
        
        elif "tab" in text.lower():
            return f"You clicked on a tab: '{text}'"
        
        elif "file" in text.lower() and "folder" in text.lower():
            return f"You clicked on a file or folder: '{text}'"
        
        else:
            return f"You clicked on: '{text}'"
=======
import os
import json
import cv2
import numpy as np
import pytesseract
import threading
import time
from datetime import datetime
import pyautogui
import re
import win32gui
import win32process
import psutil
from PIL import Image
import logging
from collections import deque

# === CONFIG ===
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='text_analyzer.log'
)
logger = logging.getLogger('TextAnalyzer')

class TextAnalyzer:
    def __init__(self, screen_logger=None, keyboard_listener=None, log_dir="screen_logs", output_dir="text_analysis"):
        """Initialize the text analyzer with connections to keyboard and screen loggers"""
        self.screen_logger = screen_logger
        self.keyboard_listener = keyboard_listener
        self.log_dir = log_dir
        self.output_dir = output_dir
        self.running = False
        self.analysis_thread = None
        
        # Activity tracking
        self.activity_history = deque(maxlen=50)
        self.current_activity = "Starting text analyzer..."
        self.last_analyzed_file = None
        self.last_window_title = ""
        self.last_application = ""
        self.processed_files = set()
        
        # Window handling
        self.known_applications = {
            "chrome.exe": "Google Chrome",
            "firefox.exe": "Firefox",
            "explorer.exe": "File Explorer",
            "notepad.exe": "Notepad",
            "code.exe": "Visual Studio Code",
            "cmd.exe": "Command Prompt",
            "powershell.exe": "PowerShell",
            "outlook.exe": "Outlook",
            "excel.exe": "Excel",
            "winword.exe": "Word",
            "mspaint.exe": "Paint",
            "taskmgr.exe": "Task Manager",
            "control.exe": "Control Panel"
        }
        
        # Common interface elements to detect
        self.ui_elements = [
            "file", "edit", "view", "search", "help", "tools", "settings",
            "save", "open", "close", "new", "folder", "document", "this pc", 
            "local disk", "c:", "desktop", "downloads", "back", "forward", 
            "refresh", "home", "bookmark", "history"
        ]
        
        # Create necessary directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def set_screen_logger(self, screen_logger):
        """Set or update the screen logger reference"""
        self.screen_logger = screen_logger
    
    def set_keyboard_listener(self, keyboard_listener):
        """Set or update the keyboard listener reference"""
        self.keyboard_listener = keyboard_listener
    
    def start(self):
        """Start the text analyzer in a background thread"""
        if self.running:
            logger.warning("Text analyzer is already running")
            return
            
        self.running = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        logger.info("Text analyzer started")
        
    def stop(self):
        """Stop the text analyzer"""
        self.running = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=2)
        logger.info("Text analyzer stopped")
    
    def get_current_activity(self):
        """Get the current activity description (for UI display)"""
        return self.current_activity
    
    def get_activity_history(self, count=10):
        """Get recent activity history"""
        return list(self.activity_history)[-count:]
    
    def _get_active_window_info(self):
        """Get detailed information about the currently active window"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process information
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                app_name = self.known_applications.get(process_name, process_name)
            except:
                process_name = "unknown"
                app_name = "Unknown Application"
                
            return {
                "window_title": window_title,
                "process_name": process_name,
                "application": app_name,
                "pid": pid
            }
        except Exception as e:
            logger.error(f"Error getting window info: {e}")
            return {
                "window_title": "Unknown",
                "process_name": "unknown",
                "application": "Unknown Application",
                "pid": None
            }
    
    def _find_newest_screenshot(self):
        """Find the most recent screenshot file that hasn't been processed"""
        try:
            files = [f for f in os.listdir(self.log_dir) if f.endswith('.jpg') and 
                     os.path.join(self.log_dir, f) not in self.processed_files]
            
            if not files:
                return None
                
            files.sort(reverse=True)  # Sort by filename (which includes timestamp)
            newest_file = files[0]
            return os.path.join(self.log_dir, newest_file) 
        except Exception as e:
            logger.error(f"Error finding newest screenshot: {e}")
            return None
    
    def _get_screenshot_metadata(self, screenshot_path):
        """Get metadata for a screenshot from the JSON log if available"""
        try:
            filename = os.path.basename(screenshot_path)
            json_path = os.path.join(self.log_dir, "activity_log.json")
            
            if not os.path.exists(json_path):
                return None
                
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            return data.get(filename, None)
        except Exception as e:
            logger.error(f"Error loading screenshot metadata: {e}")
            return None
    
    def _extract_text_from_image(self, image_path, dpi=300):
        """Extract text from an image using OCR"""
        try:
            # Read image using OpenCV
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to load image: {image_path}")
                return ""
            
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing to improve OCR accuracy
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            gray = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Run OCR
            text = pytesseract.image_to_string(gray)
            
            # Clean up the text
            text = text.strip()
            text = re.sub(r'\s+', ' ', text)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def _extract_text_near_mouse(self, image_path, mouse_x, mouse_y, window_size=300):
        """Extract text from region around mouse pointer"""
        try:
            if mouse_x is None or mouse_y is None:
                return ""
                
            img = cv2.imread(image_path)
            if img is None:
                return ""
                
            height, width = img.shape[:2]
            
            # Calculate region boundaries
            left = max(0, mouse_x - window_size//2)
            top = max(0, mouse_y - window_size//2)
            right = min(width, mouse_x + window_size//2)
            bottom = min(height, mouse_y + window_size//2)
            
            # Crop image to region around mouse
            region = img[top:bottom, left:right]
            
            # Save cropped image for debugging (optional)
            debug_path = os.path.join(self.output_dir, "mouse_region.jpg")
            cv2.imwrite(debug_path, region)
            
            # Extract text using OCR
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            gray = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            text = pytesseract.image_to_string(gray)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text near mouse: {e}")
            return ""
    
    def _detect_ui_elements(self, text):
        """Detect common UI elements in the extracted text"""
        detected = []
        text_lower = text.lower()
        
        for element in self.ui_elements:
            if element in text_lower:
                detected.append(element)
                
        return detected
    
    def _analyze_window_interaction(self, window_title, app_name, extracted_text, mouse_region_text):
        """Analyze what the user is doing based on window title and extracted text"""
        try:
            # Normalize text for easier matching
            window_lower = window_title.lower()
            full_text_lower = extracted_text.lower()
            mouse_text_lower = mouse_region_text.lower()
            
            # Common patterns
            file_explorer_pattern = any(x in window_lower for x in ['file explorer', 'this pc', 'documents', 'c:', 'downloads'])
            web_browser_pattern = any(x in app_name.lower() for x in ['chrome', 'firefox', 'edge'])
            text_editor_pattern = any(x in app_name.lower() for x in ['notepad', 'word', 'code'])
            
            action = None
            object_name = None
            location = None
            
            # Detect file explorer actions
            if file_explorer_pattern:
                if 'c:' in full_text_lower or 'c:' in window_lower:
                    location = 'C: drive'
                elif 'this pc' in full_text_lower or 'this pc' in window_lower:
                    location = 'This PC'
                elif 'documents' in full_text_lower or 'documents' in window_lower:
                    location = 'Documents folder'
                elif 'downloads' in full_text_lower or 'downloads' in window_lower:
                    location = 'Downloads folder'
                
                # Try to find selected file or folder
                if 'search' in mouse_text_lower:
                    action = 'searching in'
                elif any(x in mouse_text_lower for x in ['.txt', '.doc', '.pdf', '.jpg', '.png']):
                    action = 'viewing files in'
                    # Try to extract file name
                    file_match = re.search(r'([a-zA-Z0-9_\-]+\.(txt|doc|pdf|jpg|png))', mouse_text_lower)
                    if file_match:
                        object_name = file_match.group(1)
            
            # Detect browser actions
            elif web_browser_pattern:
                if 'search' in mouse_text_lower:
                    action = 'searching the web'
                    # Try to extract search term
                    search_match = re.search(r'search[:\s]+([a-zA-Z0-9\s]+)', mouse_text_lower)
                    if search_match:
                        object_name = search_match.group(1)
                elif 'http' in full_text_lower or 'www.' in full_text_lower:
                    action = 'browsing website'
                    # Try to extract domain
                    domain_match = re.search(r'(https?://|www\.)([a-zA-Z0-9\-\.]+)', full_text_lower)
                    if domain_match:
                        object_name = domain_match.group(2)
            
            # Detect text editing actions
            elif text_editor_pattern:
                action = 'editing document'
                if '.' in window_title:
                    # Try to extract document name from window title
                    object_name = window_title.split(' - ')[0] if ' - ' in window_title else window_title
            
            # Generate description based on detected elements
            if action and location and object_name:
                return f"{action} {object_name} in {location}"
            elif action and location:
                return f"{action} {location}"
            elif action and object_name:
                return f"{action} {object_name}"
            elif action:
                return action
            else:
                return f"Using {app_name}"
                
        except Exception as e:
            logger.error(f"Error analyzing window interaction: {e}")
            return f"Using {app_name}"
    
    def _generate_activity_description(self, screenshot_path, metadata, keyboard_buffer):
        """Generate a natural language description of user activity"""
        try:
            # Extract all available information
            window_info = self._get_active_window_info()
            window_title = window_info['window_title']
            app_name = window_info['application']
            
            # Extract text from screenshot
            full_text = self._extract_text_from_image(screenshot_path)
            
            # Extract text near mouse if coordinates available
            mouse_x = metadata.get('x') if metadata else None
            mouse_y = metadata.get('y') if metadata else None
            mouse_region_text = self._extract_text_near_mouse(screenshot_path, mouse_x, mouse_y)
            
            # Get trigger type (what caused the screenshot)
            trigger = metadata.get('trigger', 'unknown') if metadata else 'unknown'
            key_combo = metadata.get('key_combination', None) if metadata else None
            
            # Detect UI elements
            ui_elements = self._detect_ui_elements(full_text)
            mouse_ui_elements = self._detect_ui_elements(mouse_region_text)
            
            # Build the activity description
            activity = ""
            
            # Add window context
            if window_title and app_name:
                # Avoid redundancy if app name is in window title
                if app_name.lower() not in window_title.lower():
                    activity += f"In {app_name}: {window_title}. "
                else:
                    activity += f"In {window_title}. "
            
            # Add action description
            interaction = self._analyze_window_interaction(
                window_title, app_name, full_text, mouse_region_text
            )
            if interaction:
                activity += f"{interaction}. "
            
            # Add mouse activity if relevant
            if mouse_region_text and 'Periodic' not in trigger:
                filtered_text = mouse_region_text[:50]  # Limit length
                filtered_text = re.sub(r'\s+', ' ', filtered_text).strip()
                if filtered_text:
                    if 'LeftClick' in trigger:
                        activity += f"Clicked on \"{filtered_text}\". "
                    elif 'RightClick' in trigger:
                        activity += f"Right-clicked on \"{filtered_text}\". "
                    elif 'Scroll' in trigger:
                        activity += f"Scrolled near \"{filtered_text}\". "
                    elif 'KeyCombo' in trigger and key_combo:
                        activity += f"Pressed {key_combo} near \"{filtered_text}\". "
            
            # Add keyboard input if relevant
            if keyboard_buffer:
                short_text = keyboard_buffer[:30]
                if len(keyboard_buffer) > 30:
                    short_text += "..."
                activity += f"Typed: \"{short_text}\". "
            
            # Add UI element context if we don't have better information
            if not interaction and mouse_ui_elements:
                elements_str = ", ".join(mouse_ui_elements[:3])  # Limit to 3 elements
                activity += f"Near elements: {elements_str}. "
            
            # If we still don't have much information
            if len(activity.strip()) < 5:
                activity = f"Using {app_name} window titled '{window_title}'"
            
            return activity.strip()
            
        except Exception as e:
            logger.error(f"Error generating activity description: {e}")
            return f"Using computer"
    
    def _save_analysis_result(self, screenshot_path, metadata, activity_description):
        """Save analysis results to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(screenshot_path)
            output_filename = f"{timestamp}_{filename}_analysis.json"
            output_path = os.path.join(self.output_dir, output_filename)
            
            result = {
                "timestamp": timestamp,
                "screenshot": screenshot_path,
                "activity_description": activity_description,
                "metadata": metadata
            }
            
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=4)
                
            logger.info(f"Saved analysis result to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving analysis result: {e}")
            return None
    
    def _analysis_loop(self):
        """Main analysis loop that runs in background thread"""
        logger.info("Analysis loop started")
        
        while self.running:
            try:
                # Find the newest screenshot to analyze
                screenshot_path = self._find_newest_screenshot()
                
                if not screenshot_path or screenshot_path == self.last_analyzed_file:
                    # No new screenshots to analyze
                    time.sleep(0.5)
                    continue
                
                # Mark this file as processed
                self.processed_files.add(screenshot_path)
                self.last_analyzed_file = screenshot_path
                
                # Get metadata for this screenshot
                metadata = self._get_screenshot_metadata(screenshot_path)
                
                # Get current keyboard buffer
                keyboard_buffer = self.keyboard_listener.buffer if self.keyboard_listener else ""
                
                # Generate description of user activity
                activity_description = self._generate_activity_description(
                    screenshot_path, metadata, keyboard_buffer
                )
                
                # Update current activity
                self.current_activity = activity_description
                self.activity_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "activity": activity_description,
                    "screenshot": os.path.basename(screenshot_path)
                })
                
                # Save analysis results
                self._save_analysis_result(screenshot_path, metadata, activity_description)
                
                # Log the activity
                logger.info(f"Activity: {activity_description}")
                
                # Don't process too quickly
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                time.sleep(1)
        
        logger.info("Analysis loop stopped")


# Example Qt sidebar UI implementation to display the activity
class ActivitySidebar:
    """Example Qt-based sidebar that displays activity descriptions"""
    def __init__(self, text_analyzer):
        from PyQt5 import QtWidgets, QtCore, QtGui
        self.app = QtWidgets.QApplication([])
        self.text_analyzer = text_analyzer
        self.update_timer = None
        
        # Create the main window
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("Activity Monitor")
        self.window.setWindowFlags(
            QtCore.Qt.Window | 
            QtCore.Qt.WindowStaysOnTopHint | 
            QtCore.Qt.FramelessWindowHint
        )
        self.window.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Set up UI
        self._setup_ui()
        
        # Position window
        screen = self.app.primaryScreen().geometry()
        self.window.move(screen.width() - self.window.width() - 20, 100)
        
        # Make draggable
        self.window.mousePressEvent = self._mouse_press_event
        self.window.mouseMoveEvent = self._mouse_move_event
        
    def _setup_ui(self):
        from PyQt5 import QtWidgets, QtCore, QtGui
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(self.window)
        
        # Create frame
        self.frame = QtWidgets.QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 200);
                border-radius: 10px;
                border: 1px solid rgba(100, 100, 100, 120);
            }
        """)
        frame_layout = QtWidgets.QVBoxLayout(self.frame)
        
        # Title bar with controls
        title_bar = QtWidgets.QHBoxLayout()
        
        # Title
        title_label = QtWidgets.QLabel("Activity Monitor")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_bar.addWidget(title_label)
        
        # Close button
        close_btn = QtWidgets.QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 80, 80, 200);
                border-radius: 10px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 50, 50, 255);
            }
        """)
        close_btn.clicked.connect(self.app.quit)
        title_bar.addWidget(close_btn)
        
        frame_layout.addLayout(title_bar)
        
        # Divider
        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setStyleSheet("background-color: rgba(100, 100, 100, 120);")
        frame_layout.addWidget(divider)
        
        # Activity label
        self.activity_label = QtWidgets.QLabel("Monitoring user activity...")
        self.activity_label.setStyleSheet("color: white;")
        self.activity_label.setWordWrap(True)
        frame_layout.addWidget(self.activity_label)
        
        # History list
        self.history_list = QtWidgets.QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(30, 30, 30, 180);
                color: white;
                border-radius: 5px;
                border: none;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid rgba(60, 60, 60, 120);
            }
            QListWidget::item:selected {
                background-color: rgba(60, 120, 210, 150);
            }
        """)
        self.history_list.setFixedHeight(200)
        frame_layout.addWidget(self.history_list)
        
        # Add the frame to main layout
        layout.addWidget(self.frame)
        
        # Set window size
        self.window.setFixedWidth(300)
        self.window.setMinimumHeight(300)
        
    def _mouse_press_event(self, event):
        from PyQt5 import QtCore
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.window.frameGeometry().topLeft()
            event.accept()
            
    def _mouse_move_event(self, event):
        from PyQt5 import QtCore
        if event.buttons() & QtCore.Qt.LeftButton:
            self.window.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def _update_ui(self):
        """Update UI with latest activity information"""
        # Update current activity label
        current = self.text_analyzer.get_current_activity()
        if current:
            self.activity_label.setText(current)
        
        # Update history list
        history = self.text_analyzer.get_activity_history()
        if history:
            # Only update if changed
            current_count = self.history_list.count()
            if current_count != len(history):
                self.history_list.clear()
                for item in reversed(history):
                    time_str = datetime.fromisoformat(item["timestamp"]).strftime("%H:%M:%S")
                    self.history_list.addItem(f"[{time_str}] {item['activity']}")
                
                # Select most recent
                if self.history_list.count() > 0:
                    self.history_list.setCurrentRow(0)
    
    def start(self):
        """Show the sidebar and start the update timer"""
        from PyQt5 import QtCore
        self.window.show()
        
        # Create timer to update UI
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(500)  # Update every 500ms
        
        # Run the application
        return self.app.exec_()


# Example of how to use the TextAnalyzer with existing loggers
if __name__ == "__main__":
    from screen_mouse_logger import EnhancedScreenLogger
    from keyboard_logger import KeyboardListener
    
    # Create keyboard listener
    keyboard_listener = KeyboardListener()
    keyboard_listener.start()
    
    # Create screen logger
    screen_logger = EnhancedScreenLogger()
    
    # Create text analyzer
    text_analyzer = TextAnalyzer(screen_logger, keyboard_listener)
    text_analyzer.start()
    
    # Create and show sidebar
    try:
        # Only import Qt if needed
        sidebar = ActivitySidebar(text_analyzer)
        
        # Start screen logger in a separate thread
        threading.Thread(target=screen_logger.start, daemon=True).start()
        
        # Run sidebar (this will block until sidebar is closed)
        sidebar.start()
    except Exception as e:
        logger.error(f"Error starting UI: {e}")
        # Run without UI
        screen_logger.start()
    
    # Clean up
    text_analyzer.stop()
    keyboard_listener.stop()
>>>>>>> 6fe9b61b92db2138ce1f5c366e25b24ae028ead1
