/**
 * Main Activity Tracker that coordinates all tracking modules
 */

import { screenCapture } from './screenCapture';
import { keyboardLogger } from './keyboardLogger';
import { textAnalyzer } from './textAnalyzer';
import { automationManager } from './automationManager';

interface Settings {
  captureInterval: number;
  enableKeyLogging: boolean;
  enableScreenCapture: boolean;
  enableAutomationSuggestions: boolean;
}

class ActivityTracker {
  private isTracking: boolean = false;
  private settings: Settings = {
    captureInterval: 1000, // 1 second by default
    enableKeyLogging: true,
    enableScreenCapture: true,
    enableAutomationSuggestions: true,
  };
  private captureInterval?: number;
  private listeners: { [key: string]: Function[] } = {
    'activity': [],
    'screenshot': [],
    'automation': [],
  };

  constructor() {
    // Empty constructor
  }

  /**
   * Initialize the activity tracker with settings
   */
  public async initialize(settings?: Partial<Settings>): Promise<void> {
    if (settings) {
      this.settings = { ...this.settings, ...settings };
    }

    try {
      // Initialize sub-modules
      await screenCapture.initialize();
      await keyboardLogger.initialize();
      await textAnalyzer.initialize();
      await automationManager.initialize();

      // Set up event listeners between modules
      this.setupEventListeners();

      console.log('Activity Tracker initialized with settings:', this.settings);
    } catch (error) {
      console.error('Failed to initialize Activity Tracker:', error);
      throw error;
    }
  }

  /**
   * Start tracking activities
   */
  public start(): void {
    if (this.isTracking) return;

    this.isTracking = true;
    console.log('Starting activity tracking...');

    if (this.settings.enableKeyLogging) {
      keyboardLogger.start();
    }

    if (this.settings.enableScreenCapture) {
      // Start regular screen captures
      this.captureInterval = window.setInterval(() => {
        this.captureActivity();
      }, this.settings.captureInterval);
    }

    // Notify listeners
    this.notifyListeners('activity', { type: 'system', message: 'Activity tracking started' });
  }

  /**
   * Stop tracking activities
   */
  public stop(): void {
    if (!this.isTracking) return;

    this.isTracking = false;
    console.log('Stopping activity tracking...');

    // Clear interval
    if (this.captureInterval) {
      clearInterval(this.captureInterval);
      this.captureInterval = undefined;
    }

    // Stop sub-modules
    keyboardLogger.stop();

    // Notify listeners
    this.notifyListeners('activity', { type: 'system', message: 'Activity tracking stopped' });
  }

  /**
   * Capture current screen and analyze
   */
  private async captureActivity(): Promise<void> {
    if (!this.isTracking) return;

    try {
      // Take screenshot
      const screenshot = await screenCapture.captureScreen();
      
      // Notify listeners about new screenshot
      this.notifyListeners('screenshot', screenshot);
      
      // Analyze screenshot with OCR
      const textData = await textAnalyzer.analyzeImage(screenshot.fullScreenPath);
      
      // Log the activity
      const activity = {
        type: 'screen_capture',
        timestamp: new Date(),
        screenshot: screenshot,
        textData: textData,
        mousePosition: {
          x: screenshot.mouseX,
          y: screenshot.mouseY
        }
      };
      
      // Save the activity to server
      this.saveActivity(activity);
      
      // Notify listeners
      this.notifyListeners('activity', activity);
      
      // Check for automation opportunities if enabled
      if (this.settings.enableAutomationSuggestions) {
        automationManager.checkForPatterns(activity);
      }
    } catch (error) {
      console.error('Error during activity capture:', error);
    }
  }

  /**
   * Save activity to the server
   */
  private async saveActivity(activity: any): Promise<void> {
    try {
      await fetch('/api/activity-logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          activityType: activity.type,
          description: this.generateDescription(activity),
          data: activity,
          screenshotId: activity.screenshot?.id
        }),
      });
    } catch (error) {
      console.error('Failed to save activity:', error);
    }
  }

  /**
   * Generate human-readable description from activity data
   */
  private generateDescription(activity: any): string {
    switch (activity.type) {
      case 'screen_capture':
        // Check if we have window info from text analysis
        if (activity.textData?.windowTitle) {
          return `Viewed ${activity.textData.windowTitle}`;
        }
        return 'Captured screen activity';
        
      case 'mouse_click':
        if (activity.target) {
          return `Clicked on ${activity.target}`;
        }
        return `Clicked at position (${activity.x}, ${activity.y})`;
        
      case 'keyboard':
        if (activity.isSpecialKey) {
          return `Pressed ${activity.key}`;
        }
        if (activity.text && activity.text.length < 20) {
          return `Typed "${activity.text}"`;
        }
        return 'Typed text';
        
      case 'application':
        return `Opened ${activity.name}`;
        
      case 'system':
        return activity.message;
        
      default:
        return 'Performed an activity';
    }
  }

  /**
   * Register event listeners
   */
  private setupEventListeners(): void {
    // Listen for keyboard events
    keyboardLogger.on('keypress', (keyboardEvent) => {
      if (!this.isTracking) return;
      
      const activity = {
        type: 'keyboard',
        timestamp: new Date(),
        ...keyboardEvent
      };
      
      this.saveActivity(activity);
      this.notifyListeners('activity', activity);
      
      // Check for automation opportunities
      if (this.settings.enableAutomationSuggestions) {
        automationManager.checkForPatterns(activity);
      }
    });

    // Listen for automation suggestions
    automationManager.on('suggestion', (suggestion) => {
      this.notifyListeners('automation', suggestion);
    });
  }

  /**
   * Subscribe to events
   */
  public on(event: string, callback: Function): void {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  /**
   * Notify all listeners of an event
   */
  private notifyListeners(event: string, data: any): void {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in listener for event "${event}":`, error);
        }
      });
    }
  }

  /**
   * Update tracker settings
   */
  public updateSettings(settings: Partial<Settings>): void {
    const wasTracking = this.isTracking;
    
    // Stop tracking to apply new settings
    if (wasTracking) {
      this.stop();
    }
    
    // Update settings
    this.settings = { ...this.settings, ...settings };
    
    // Restart if it was active
    if (wasTracking) {
      this.start();
    }
    
    console.log('Activity Tracker settings updated:', this.settings);
  }
}

// Create singleton instance
export const activityTracker = new ActivityTracker();
