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
