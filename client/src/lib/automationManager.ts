/**
 * Automation Manager - Detects patterns and manages automation tasks
 */

interface AutomationTask {
  id: number;
  name: string;
  description: string;
  steps: string[];
  triggers: Array<{
    type: string;
    value: string;
  }>;
  executionCount: number;
  isActive: boolean;
}

interface AutomationSuggestion {
  id: number;
  title: string;
  description: string;
  confidence: number;
  activities: any[];
  createdAt: Date;
}

class AutomationManager {
  private isInitialized: boolean = false;
  private activityHistory: any[] = [];
  private historyMaxLength: number = 1000;
  private tasks: AutomationTask[] = [];
  private suggestions: AutomationSuggestion[] = [];
  private listeners: { [key: string]: Function[] } = {
    'suggestion': [],
    'task': []
  };

  /**
   * Initialize automation manager
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Load existing automation tasks
      await this.loadTasks();
      
      this.isInitialized = true;
      console.log('Automation Manager initialized');
    } catch (error) {
      console.error('Failed to initialize Automation Manager:', error);
      throw error;
    }
  }

  /**
   * Check for patterns in activities and generate automation suggestions
   */
  public checkForPatterns(activity: any): void {
    // Add to history
    this.activityHistory.push(activity);
    
    // Trim history if too long
    if (this.activityHistory.length > this.historyMaxLength) {
      this.activityHistory = this.activityHistory.slice(-this.historyMaxLength);
    }
    
    // Check for patterns
    this.detectPatterns();
    
    // Check if any automation task should be triggered
    this.checkTriggers(activity);
  }

  /**
   * Load existing automation tasks from server
   */
  private async loadTasks(): Promise<void> {
    try {
      const response = await fetch('/api/automation-tasks');
      if (response.ok) {
        this.tasks = await response.json();
      }
    } catch (error) {
      console.error('Failed to load automation tasks:', error);
    }
  }

  /**
   * Detect patterns in activity history
   */
  private detectPatterns(): void {
    // Skip if there's not enough history
    if (this.activityHistory.length < 10) return;
    
    // In a real implementation, this would use sophisticated 
    // pattern recognition algorithms. For this demo, we'll use
    // some basic heuristics.
    
    this.detectRepeatedSequence();
    this.detectTimeBasedPatterns();
    this.detectApplicationPatterns();
  }

  /**
   * Detect repeated sequences of activities
   */
  private detectRepeatedSequence(): void {
    // Look at the last 20 activities
    const recentActivities = this.activityHistory.slice(-20);
    
    // Count activity types
    const typeCounts: {[key: string]: number} = {};
    
    for (const activity of recentActivities) {
      if (!activity.type) continue;
      
      if (!typeCounts[activity.type]) {
        typeCounts[activity.type] = 1;
      } else {
        typeCounts[activity.type]++;
      }
    }
    
    // Check if any type appears frequently
    for (const [type, count] of Object.entries(typeCounts)) {
      if (count >= 3) {
        // Check if we already have a suggestion for this pattern
        if (this.hasExistingSuggestion('repeated_sequence', type)) {
          continue;
        }
        
        // Create suggestion
        const activities = recentActivities.filter(a => a.type === type);
        
        if (type === 'keyboard' && activities.some(a => a.text)) {
          this.createSuggestion({
            title: 'Repeated Text Input',
            description: `You've typed similar text multiple times. Would you like to create a template?`,
            confidence: 0.7,
            activities,
            type: 'repeated_sequence',
            subtype: type
          });
        } else if (type === 'mouse_click') {
          this.createSuggestion({
            title: 'Repeated Clicks Detected',
            description: `You've clicked in the same area multiple times. Want to automate this?`,
            confidence: 0.6,
            activities,
            type: 'repeated_sequence',
            subtype: type
          });
        }
      }
    }
  }

  /**
   * Detect time-based patterns in activities
   */
  private detectTimeBasedPatterns(): void {
    // Check if certain activities happen at similar times
    // This would require more sophisticated analysis in a real implementation
  }

  /**
   * Detect application usage patterns
   */
  private detectApplicationPatterns(): void {
    // Look for sequences of application launches
    const appActivities = this.activityHistory
      .filter(a => a.type === 'application' || 
                  (a.type === 'screen_capture' && a.textData?.applicationName));
    
    if (appActivities.length < 3) return;
    
    // Get the last 3 unique applications
    const recentApps: string[] = [];
    for (let i = appActivities.length - 1; i >= 0 && recentApps.length < 3; i--) {
      const activity = appActivities[i];
      const appName = activity.type === 'application' 
        ? activity.name 
        : activity.textData.applicationName;
        
      if (appName && !recentApps.includes(appName)) {
        recentApps.push(appName);
      }
    }
    
    if (recentApps.length === 3) {
      // Check if we've already suggested this app sequence
      const sequenceKey = recentApps.join(',');
      if (this.hasExistingSuggestion('app_sequence', sequenceKey)) {
        return;
      }
      
      this.createSuggestion({
        title: 'Application Sequence',
        description: `You often open ${recentApps.join(', ')} together. Create a workflow?`,
        confidence: 0.65,
        activities: appActivities.slice(-5),
        type: 'app_sequence',
        subtype: sequenceKey
      });
    }
  }

  /**
   * Check if automation triggers match current activity
   */
  private checkTriggers(activity: any): void {
    for (const task of this.tasks) {
      if (!task.isActive) continue;
      
      let shouldTrigger = false;
      
      for (const trigger of task.triggers) {
        switch (trigger.type) {
          case 'time':
            // Check if current time matches trigger
            const now = new Date();
            const triggerTime = trigger.value; // Format: "HH:MM"
            const [hours, minutes] = triggerTime.split(':').map(Number);
            
            if (now.getHours() === hours && now.getMinutes() === minutes) {
              shouldTrigger = true;
            }
            break;
            
          case 'mouse':
            // Check if mouse position matches
            if (activity.type === 'screen_capture' && activity.mousePosition) {
              const [targetX, targetY] = trigger.value.split(',').map(Number);
              const tolerance = 20; // pixels
              
              if (Math.abs(activity.mousePosition.x - targetX) <= tolerance &&
                  Math.abs(activity.mousePosition.y - targetY) <= tolerance) {
                shouldTrigger = true;
              }
            }
            break;
            
          case 'keyboard':
            // Check for keyboard shortcut
            if (activity.type === 'keyboard' && 
                activity.isSpecialKey && 
                activity.key === trigger.value) {
              shouldTrigger = true;
            }
            break;
            
          case 'click':
            // Check for clicks in specific area
            if (activity.type === 'mouse_click') {
              const [x, y, width, height] = trigger.value.split(',').map(Number);
              
              if (activity.x >= x && activity.x <= x + width &&
                  activity.y >= y && activity.y <= y + height) {
                shouldTrigger = true;
              }
            }
            break;
        }
        
        if (shouldTrigger) {
          this.executeTask(task.id);
          break;
        }
      }
    }
  }

  /**
   * Create a new automation suggestion
   */
  private createSuggestion(data: {
    title: string;
    description: string;
    confidence: number;
    activities: any[];
    type: string;
    subtype: string;
  }): void {
    const suggestion: AutomationSuggestion = {
      id: Date.now(),
      title: data.title,
      description: data.description,
      confidence: data.confidence,
      activities: data.activities,
      createdAt: new Date()
    };
    
    // Add metadata
    (suggestion as any).metadata = {
      type: data.type,
      subtype: data.subtype
    };
    
    // Add to suggestions
    this.suggestions.push(suggestion);
    
    // Limit to 10 most recent suggestions
    if (this.suggestions.length > 10) {
      this.suggestions.shift();
    }
    
    // Notify listeners
    this.notifyListeners('suggestion', suggestion);
  }

  /**
   * Check if we already have a suggestion of this type
   */
  private hasExistingSuggestion(type: string, subtype: string): boolean {
    return this.suggestions.some(suggestion => 
      (suggestion as any).metadata?.type === type && 
      (suggestion as any).metadata?.subtype === subtype
    );
  }

  /**
   * Execute an automation task
   */
  public async executeTask(taskId: number): Promise<boolean> {
    const task = this.tasks.find(t => t.id === taskId);
    if (!task) {
      console.error(`Task with ID ${taskId} not found`);
      return false;
    }
    
    console.log(`Executing task: ${task.name}`);
    
    try {
      // In a real implementation, we would execute the steps
      // For this demo, we'll simulate by calling our API
      const response = await fetch(`/api/automation-tasks/${taskId}/execute`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Failed to execute task');
      }
      
      // Update execution count
      task.executionCount++;
      
      // Notify listeners
      this.notifyListeners('task', {
        type: 'execution',
        taskId,
        success: true,
        message: `Task "${task.name}" executed successfully`
      });
      
      return true;
    } catch (error) {
      console.error(`Error executing task ${taskId}:`, error);
      
      // Notify listeners
      this.notifyListeners('task', {
        type: 'execution',
        taskId,
        success: false,
        message: `Failed to execute task "${task.name}"`
      });
      
      return false;
    }
  }

  /**
   * Create a new automation task
   */
  public async createTask(task: Omit<AutomationTask, 'id' | 'executionCount' | 'isActive'>): Promise<AutomationTask | null> {
    try {
      const response = await fetch('/api/automation-tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...task,
          isActive: true
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to create automation task');
      }
      
      const newTask = await response.json();
      
      // Add to local tasks
      this.tasks.push(newTask);
      
      // Notify listeners
      this.notifyListeners('task', {
        type: 'create',
        task: newTask
      });
      
      return newTask;
    } catch (error) {
      console.error('Error creating automation task:', error);
      return null;
    }
  }

  /**
   * Get all automation suggestions
   */
  public getSuggestions(): AutomationSuggestion[] {
    return [...this.suggestions];
  }

  /**
   * Get all automation tasks
   */
  public getTasks(): AutomationTask[] {
    return [...this.tasks];
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
}

// Create singleton instance
export const automationManager = new AutomationManager();
