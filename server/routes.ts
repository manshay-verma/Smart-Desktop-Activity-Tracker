import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import fs from 'fs';
import path from 'path';
import { insertActivityLogSchema, insertAutomationTaskSchema, insertScreenshotSchema, insertSettingsSchema } from "@shared/schema";
import { z } from "zod";

// Create directories for screenshots if they don't exist
const screenshotsDir = path.join(process.cwd(), 'data', 'screenshots');
const fullScreenDir = path.join(screenshotsDir, 'full');
const mouseAreaDir = path.join(screenshotsDir, 'mouse');

if (!fs.existsSync(fullScreenDir)) {
  fs.mkdirSync(fullScreenDir, { recursive: true });
}

if (!fs.existsSync(mouseAreaDir)) {
  fs.mkdirSync(mouseAreaDir, { recursive: true });
}

export async function registerRoutes(app: Express): Promise<Server> {
  // GET /api/activity-logs - Get all activity logs
  app.get('/api/activity-logs', async (req, res) => {
    try {
      const activityLogs = await storage.getActivityLogs();
      res.json(activityLogs);
    } catch (error) {
      console.error('Error fetching activity logs:', error);
      res.status(500).json({ message: 'Failed to fetch activity logs' });
    }
  });

  // POST /api/activity-logs - Create a new activity log
  app.post('/api/activity-logs', async (req, res) => {
    try {
      const validatedData = insertActivityLogSchema.parse(req.body);
      const newActivityLog = await storage.createActivityLog(validatedData);
      res.status(201).json(newActivityLog);
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ message: 'Invalid activity log data', errors: error.errors });
      } else {
        console.error('Error creating activity log:', error);
        res.status(500).json({ message: 'Failed to create activity log' });
      }
    }
  });

  // GET /api/automation-tasks - Get all automation tasks
  app.get('/api/automation-tasks', async (req, res) => {
    try {
      const automationTasks = await storage.getAutomationTasks();
      res.json(automationTasks);
    } catch (error) {
      console.error('Error fetching automation tasks:', error);
      res.status(500).json({ message: 'Failed to fetch automation tasks' });
    }
  });

  // POST /api/automation-tasks - Create a new automation task
  app.post('/api/automation-tasks', async (req, res) => {
    try {
      const validatedData = insertAutomationTaskSchema.parse(req.body);
      const newAutomationTask = await storage.createAutomationTask(validatedData);
      res.status(201).json(newAutomationTask);
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ message: 'Invalid automation task data', errors: error.errors });
      } else {
        console.error('Error creating automation task:', error);
        res.status(500).json({ message: 'Failed to create automation task' });
      }
    }
  });

  // POST /api/automation-tasks/:id/execute - Execute an automation task
  app.post('/api/automation-tasks/:id/execute', async (req, res) => {
    try {
      const taskId = parseInt(req.params.id);
      // In a real implementation, this would execute the automation task
      // For now, we'll just update the execution count
      const automationTask = await storage.getAutomationTask(taskId);
      
      if (!automationTask) {
        return res.status(404).json({ message: 'Automation task not found' });
      }
      
      // Update execution count
      await storage.updateAutomationTaskExecutionCount(taskId);
      
      res.json({ message: 'Task executed successfully' });
    } catch (error) {
      console.error('Error executing automation task:', error);
      res.status(500).json({ message: 'Failed to execute automation task' });
    }
  });

  // GET /api/screenshots/:id - Get a specific screenshot
  app.get('/api/screenshots/:id', async (req, res) => {
    try {
      const screenshotId = parseInt(req.params.id);
      const screenshot = await storage.getScreenshot(screenshotId);
      
      if (!screenshot) {
        return res.status(404).json({ message: 'Screenshot not found' });
      }
      
      // Check if the file exists
      const fullScreenPath = path.join(fullScreenDir, `${screenshotId}.png`);
      if (!fs.existsSync(fullScreenPath)) {
        return res.status(404).json({ message: 'Screenshot file not found' });
      }
      
      // Send the file
      res.sendFile(fullScreenPath);
    } catch (error) {
      console.error('Error fetching screenshot:', error);
      res.status(500).json({ message: 'Failed to fetch screenshot' });
    }
  });

  // GET /api/screenshots/:id/mouse-area - Get the mouse area screenshot
  app.get('/api/screenshots/:id/mouse-area', async (req, res) => {
    try {
      const screenshotId = parseInt(req.params.id);
      const screenshot = await storage.getScreenshot(screenshotId);
      
      if (!screenshot) {
        return res.status(404).json({ message: 'Screenshot not found' });
      }
      
      // Check if the file exists
      const mouseAreaPath = path.join(mouseAreaDir, `${screenshotId}.png`);
      if (!fs.existsSync(mouseAreaPath)) {
        return res.status(404).json({ message: 'Mouse area screenshot file not found' });
      }
      
      // Send the file
      res.sendFile(mouseAreaPath);
    } catch (error) {
      console.error('Error fetching mouse area screenshot:', error);
      res.status(500).json({ message: 'Failed to fetch mouse area screenshot' });
    }
  });

  // GET /api/screenshots/:id/metadata - Get screenshot metadata
  app.get('/api/screenshots/:id/metadata', async (req, res) => {
    try {
      const screenshotId = parseInt(req.params.id);
      const screenshot = await storage.getScreenshot(screenshotId);
      
      if (!screenshot) {
        return res.status(404).json({ message: 'Screenshot not found' });
      }
      
      res.json({
        id: screenshot.id,
        timestamp: screenshot.timestamp,
        mouseX: screenshot.mouseX,
        mouseY: screenshot.mouseY,
        activeWindow: screenshot.activeWindow,
        activeApplication: screenshot.activeApplication,
        extractedText: screenshot.extractedText,
        confidence: screenshot.confidence
      });
    } catch (error) {
      console.error('Error fetching screenshot metadata:', error);
      res.status(500).json({ message: 'Failed to fetch screenshot metadata' });
    }
  });

  // POST /api/capture - Capture a new screenshot
  app.post('/api/capture', async (req, res) => {
    try {
      const { mouseX, mouseY, cropSize } = req.body;
      
      // In a real implementation, this would take an actual screenshot
      // For now, we'll create empty image files
      
      // Create a new screenshot record
      const newScreenshot = await storage.createScreenshot({
        userId: 1, // Default user ID
        fullScreenPath: 'placeholder',
        mouseAreaPath: 'placeholder',
        mouseX,
        mouseY,
        activeWindow: 'Sample Window',
        activeApplication: 'Sample Application',
        extractedText: 'Sample text from the window',
        confidence: 80
      });
      
      // Create placeholders for the screenshot files
      const fullScreenPath = path.join(fullScreenDir, `${newScreenshot.id}.png`);
      const mouseAreaPath = path.join(mouseAreaDir, `${newScreenshot.id}.png`);
      
      // Create empty files
      fs.writeFileSync(fullScreenPath, '');
      fs.writeFileSync(mouseAreaPath, '');
      
      // Update the screenshot record with the real paths
      await storage.updateScreenshotPaths(
        newScreenshot.id, 
        `/api/screenshots/${newScreenshot.id}`,
        `/api/screenshots/${newScreenshot.id}/mouse-area`
      );
      
      res.status(201).json({
        id: newScreenshot.id,
        fullScreenPath: `/api/screenshots/${newScreenshot.id}`,
        mouseAreaPath: `/api/screenshots/${newScreenshot.id}/mouse-area`,
        mouseX,
        mouseY,
        timestamp: newScreenshot.timestamp
      });
    } catch (error) {
      console.error('Error capturing screenshot:', error);
      res.status(500).json({ message: 'Failed to capture screenshot' });
    }
  });

  // POST /api/ocr - Analyze image with OCR
  app.post('/api/ocr', async (req, res) => {
    try {
      const { imagePath } = req.body;
      
      // In a real implementation, this would use an OCR service
      // For now, we'll return mock data
      res.json({
        extractedText: 'Sample extracted text from the image',
        confidence: 85,
        areas: [
          {
            text: 'Window Title',
            bounds: { x: 10, y: 10, width: 200, height: 30 },
            confidence: 90
          },
          {
            text: 'Button',
            bounds: { x: 50, y: 100, width: 80, height: 40 },
            confidence: 80
          }
        ]
      });
    } catch (error) {
      console.error('Error analyzing image with OCR:', error);
      res.status(500).json({ message: 'Failed to analyze image' });
    }
  });

  // GET /api/mouse-position - Get current mouse position
  app.get('/api/mouse-position', async (req, res) => {
    // In a real implementation, this would get the actual mouse position
    // For now, we'll return random coordinates
    res.json({
      x: Math.floor(Math.random() * 1920),
      y: Math.floor(Math.random() * 1080)
    });
  });

  // GET /api/settings - Get user settings
  app.get('/api/settings', async (req, res) => {
    try {
      const userId = 1; // Default user ID
      const settings = await storage.getSettingsByUserId(userId);
      
      if (!settings) {
        // Return default settings if none found
        return res.json({
          captureInterval: 1000,
          keepHistoryDays: 7,
          enableKeyLogging: true,
          enableScreenCapture: true,
          enableAutomationSuggestions: true,
          sidebarPosition: 'right',
          theme: 'light',
        });
      }
      
      res.json(settings);
    } catch (error) {
      console.error('Error fetching settings:', error);
      res.status(500).json({ message: 'Failed to fetch settings' });
    }
  });

  // POST /api/settings - Update user settings
  app.post('/api/settings', async (req, res) => {
    try {
      const userId = 1; // Default user ID
      const validatedData = insertSettingsSchema.parse({
        ...req.body,
        userId
      });
      
      // Check if settings already exist for this user
      const existingSettings = await storage.getSettingsByUserId(userId);
      
      let settings;
      if (existingSettings) {
        // Update existing settings
        settings = await storage.updateSettings(existingSettings.id, validatedData);
      } else {
        // Create new settings
        settings = await storage.createSettings(validatedData);
      }
      
      res.json(settings);
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ message: 'Invalid settings data', errors: error.errors });
      } else {
        console.error('Error updating settings:', error);
        res.status(500).json({ message: 'Failed to update settings' });
      }
    }
  });

  // GET /api/tracking/status - Get tracking status
  app.get('/api/tracking/status', async (req, res) => {
    // In a real implementation, this would get the actual tracking status
    // For now, we'll return a default status
    res.json({
      isActive: true,
      lastUpdated: new Date()
    });
  });

  // POST /api/tracking/toggle - Toggle tracking status
  app.post('/api/tracking/toggle', async (req, res) => {
    try {
      const { isActive } = req.body;
      
      // In a real implementation, this would actually toggle tracking
      // For now, we'll just return success
      res.json({
        isActive,
        lastUpdated: new Date()
      });
    } catch (error) {
      console.error('Error toggling tracking status:', error);
      res.status(500).json({ message: 'Failed to toggle tracking status' });
    }
  });

  // POST /api/data/clear - Clear all user data
  app.post('/api/data/clear', async (req, res) => {
    try {
      const userId = 1; // Default user ID
      
      // Delete all user data
      await storage.clearUserData(userId);
      
      // Delete all screenshot files
      fs.readdirSync(fullScreenDir).forEach(file => {
        fs.unlinkSync(path.join(fullScreenDir, file));
      });
      
      fs.readdirSync(mouseAreaDir).forEach(file => {
        fs.unlinkSync(path.join(mouseAreaDir, file));
      });
      
      res.json({ message: 'All user data cleared successfully' });
    } catch (error) {
      console.error('Error clearing user data:', error);
      res.status(500).json({ message: 'Failed to clear user data' });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
