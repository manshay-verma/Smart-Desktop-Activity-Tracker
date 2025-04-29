import { 
  users, screenshots, activityLogs, automationTasks, settings,
  type User, type InsertUser, 
  type Screenshot, type InsertScreenshot,
  type ActivityLog, type InsertActivityLog,
  type AutomationTask, type InsertAutomationTask,
  type Settings, type InsertSettings
} from "@shared/schema";

// modify the interface with any CRUD methods
// you might need
export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

  // Screenshot methods
  getScreenshot(id: number): Promise<Screenshot | undefined>;
  createScreenshot(screenshot: InsertScreenshot): Promise<Screenshot>;
  updateScreenshotPaths(id: number, fullScreenPath: string, mouseAreaPath: string): Promise<Screenshot>;
  getScreenshotsByUserId(userId: number): Promise<Screenshot[]>;

  // Activity Log methods
  getActivityLogs(): Promise<ActivityLog[]>;
  getActivityLogsByUserId(userId: number): Promise<ActivityLog[]>;
  createActivityLog(activityLog: InsertActivityLog): Promise<ActivityLog>;

  // Automation Task methods
  getAutomationTasks(): Promise<AutomationTask[]>;
  getAutomationTask(id: number): Promise<AutomationTask | undefined>;
  getAutomationTasksByUserId(userId: number): Promise<AutomationTask[]>;
  createAutomationTask(task: InsertAutomationTask): Promise<AutomationTask>;
  updateAutomationTaskExecutionCount(id: number): Promise<AutomationTask>;

  // Settings methods
  getSettingsByUserId(userId: number): Promise<Settings | undefined>;
  createSettings(settings: InsertSettings): Promise<Settings>;
  updateSettings(id: number, settings: InsertSettings): Promise<Settings>;

  // Data management
  clearUserData(userId: number): Promise<void>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private screenshots: Map<number, Screenshot>;
  private activityLogs: Map<number, ActivityLog>;
  private automationTasks: Map<number, AutomationTask>;
  private userSettings: Map<number, Settings>;
  
  private currentUserId: number;
  private currentScreenshotId: number;
  private currentActivityLogId: number;
  private currentAutomationTaskId: number;
  private currentSettingsId: number;

  constructor() {
    this.users = new Map();
    this.screenshots = new Map();
    this.activityLogs = new Map();
    this.automationTasks = new Map();
    this.userSettings = new Map();
    
    this.currentUserId = 1;
    this.currentScreenshotId = 1;
    this.currentActivityLogId = 1;
    this.currentAutomationTaskId = 1;
    this.currentSettingsId = 1;
    
    // Add a default user
    this.users.set(1, {
      id: 1,
      username: 'default',
      password: 'password'
    });
  }

  // User methods
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  // Screenshot methods
  async getScreenshot(id: number): Promise<Screenshot | undefined> {
    return this.screenshots.get(id);
  }

  async createScreenshot(insertScreenshot: InsertScreenshot): Promise<Screenshot> {
    const id = this.currentScreenshotId++;
    const screenshot: Screenshot = { 
      ...insertScreenshot, 
      id,
      timestamp: new Date() 
    };
    this.screenshots.set(id, screenshot);
    return screenshot;
  }

  async updateScreenshotPaths(id: number, fullScreenPath: string, mouseAreaPath: string): Promise<Screenshot> {
    const screenshot = this.screenshots.get(id);
    if (!screenshot) {
      throw new Error(`Screenshot with ID ${id} not found`);
    }
    
    const updatedScreenshot = {
      ...screenshot,
      fullScreenPath,
      mouseAreaPath
    };
    
    this.screenshots.set(id, updatedScreenshot);
    return updatedScreenshot;
  }

  async getScreenshotsByUserId(userId: number): Promise<Screenshot[]> {
    return Array.from(this.screenshots.values()).filter(
      (screenshot) => screenshot.userId === userId
    );
  }

  // Activity Log methods
  async getActivityLogs(): Promise<ActivityLog[]> {
    return Array.from(this.activityLogs.values())
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }

  async getActivityLogsByUserId(userId: number): Promise<ActivityLog[]> {
    return Array.from(this.activityLogs.values())
      .filter((log) => log.userId === userId)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }

  async createActivityLog(insertActivityLog: InsertActivityLog): Promise<ActivityLog> {
    const id = this.currentActivityLogId++;
    const activityLog: ActivityLog = {
      ...insertActivityLog,
      id,
      timestamp: new Date()
    };
    this.activityLogs.set(id, activityLog);
    return activityLog;
  }

  // Automation Task methods
  async getAutomationTasks(): Promise<AutomationTask[]> {
    return Array.from(this.automationTasks.values());
  }

  async getAutomationTask(id: number): Promise<AutomationTask | undefined> {
    return this.automationTasks.get(id);
  }

  async getAutomationTasksByUserId(userId: number): Promise<AutomationTask[]> {
    return Array.from(this.automationTasks.values()).filter(
      (task) => task.userId === userId
    );
  }

  async createAutomationTask(insertTask: InsertAutomationTask): Promise<AutomationTask> {
    const id = this.currentAutomationTaskId++;
    const task: AutomationTask = {
      ...insertTask,
      id,
      executionCount: 0,
      lastExecuted: undefined
    };
    this.automationTasks.set(id, task);
    return task;
  }

  async updateAutomationTaskExecutionCount(id: number): Promise<AutomationTask> {
    const task = this.automationTasks.get(id);
    if (!task) {
      throw new Error(`Automation task with ID ${id} not found`);
    }
    
    const updatedTask = {
      ...task,
      executionCount: task.executionCount + 1,
      lastExecuted: new Date()
    };
    
    this.automationTasks.set(id, updatedTask);
    return updatedTask;
  }

  // Settings methods
  async getSettingsByUserId(userId: number): Promise<Settings | undefined> {
    return Array.from(this.userSettings.values()).find(
      (settings) => settings.userId === userId
    );
  }

  async createSettings(insertSettings: InsertSettings): Promise<Settings> {
    const id = this.currentSettingsId++;
    const settingsObj: Settings = { ...insertSettings, id };
    this.userSettings.set(id, settingsObj);
    return settingsObj;
  }

  async updateSettings(id: number, updatedSettings: InsertSettings): Promise<Settings> {
    const settings = this.userSettings.get(id);
    if (!settings) {
      throw new Error(`Settings with ID ${id} not found`);
    }
    
    const newSettings = { ...settings, ...updatedSettings };
    this.userSettings.set(id, newSettings);
    return newSettings;
  }

  // Data management
  async clearUserData(userId: number): Promise<void> {
    // Delete all screenshots for this user
    const userScreenshots = await this.getScreenshotsByUserId(userId);
    userScreenshots.forEach(screenshot => {
      this.screenshots.delete(screenshot.id);
    });
    
    // Delete all activity logs for this user
    const userLogs = await this.getActivityLogsByUserId(userId);
    userLogs.forEach(log => {
      this.activityLogs.delete(log.id);
    });
    
    // Delete all automation tasks for this user
    const userTasks = await this.getAutomationTasksByUserId(userId);
    userTasks.forEach(task => {
      this.automationTasks.delete(task.id);
    });
    
    // Delete user settings
    const userSettings = await this.getSettingsByUserId(userId);
    if (userSettings) {
      this.userSettings.delete(userSettings.id);
    }
  }
}

export const storage = new MemStorage();
