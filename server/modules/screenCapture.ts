/**
 * Server-side Screen Capture Module
 * Handles screenshot capture, processing, and storage
 */

import fs from 'fs';
import path from 'path';
import { storage } from '../storage';

// Directory paths
const screenshotsDir = path.join(process.cwd(), 'data', 'screenshots');
const fullScreenDir = path.join(screenshotsDir, 'full');
const mouseAreaDir = path.join(screenshotsDir, 'mouse');

// Ensure directories exist
if (!fs.existsSync(fullScreenDir)) {
  fs.mkdirSync(fullScreenDir, { recursive: true });
}

if (!fs.existsSync(mouseAreaDir)) {
  fs.mkdirSync(mouseAreaDir, { recursive: true });
}

class ScreenCapture {
  /**
   * Initialize the screen capture module
   */
  async initialize(): Promise<void> {
    console.log('Screen capture module initialized');
  }
  
  /**
   * Capture a screenshot with the given parameters
   */
  async captureScreen(
    userId: number,
    mouseX: number,
    mouseY: number,
    cropSize: number = 200
  ): Promise<any> {
    try {
      // Create a new screenshot record in the database
      const screenshot = await storage.createScreenshot({
        userId,
        fullScreenPath: 'placeholder',
        mouseAreaPath: 'placeholder',
        mouseX,
        mouseY,
        activeWindow: 'Unknown',
        activeApplication: 'Unknown',
        extractedText: '',
        confidence: 0
      });
      
      // Define file paths
      const fullScreenPath = path.join(fullScreenDir, `${screenshot.id}.png`);
      const mouseAreaPath = path.join(mouseAreaDir, `${screenshot.id}.png`);
      
      // In a real implementation, this would capture actual screenshots
      // For now, create empty placeholder files
      fs.writeFileSync(fullScreenPath, '');
      fs.writeFileSync(mouseAreaPath, '');
      
      // Update the screenshot record with the real paths
      const updatedScreenshot = await storage.updateScreenshotPaths(
        screenshot.id,
        `/api/screenshots/${screenshot.id}`,
        `/api/screenshots/${screenshot.id}/mouse-area`
      );
      
      return {
        id: updatedScreenshot.id,
        fullScreenPath: updatedScreenshot.fullScreenPath,
        mouseAreaPath: updatedScreenshot.mouseAreaPath,
        mouseX: updatedScreenshot.mouseX,
        mouseY: updatedScreenshot.mouseY,
        timestamp: updatedScreenshot.timestamp
      };
    } catch (error) {
      console.error('Error capturing screen:', error);
      throw new Error('Failed to capture screen');
    }
  }
  
  /**
   * Delete a screenshot and its associated files
   */
  async deleteScreenshot(screenshotId: number): Promise<void> {
    try {
      // Get the screenshot
      const screenshot = await storage.getScreenshot(screenshotId);
      if (!screenshot) {
        throw new Error(`Screenshot with ID ${screenshotId} not found`);
      }
      
      // Delete the files
      const fullScreenPath = path.join(fullScreenDir, `${screenshotId}.png`);
      const mouseAreaPath = path.join(mouseAreaDir, `${screenshotId}.png`);
      
      if (fs.existsSync(fullScreenPath)) {
        fs.unlinkSync(fullScreenPath);
      }
      
      if (fs.existsSync(mouseAreaPath)) {
        fs.unlinkSync(mouseAreaPath);
      }
      
      // In a real implementation, we would also delete the database record
      // but our storage interface doesn't have a delete method yet
    } catch (error) {
      console.error(`Error deleting screenshot ${screenshotId}:`, error);
      throw new Error('Failed to delete screenshot');
    }
  }
  
  /**
   * Clean up old screenshots based on retention policy
   */
  async cleanupOldScreenshots(userId: number, retentionDays: number): Promise<void> {
    try {
      // Get all screenshots for the user
      const screenshots = await storage.getScreenshotsByUserId(userId);
      
      // Calculate the cutoff date
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - retentionDays);
      
      // Find screenshots older than the cutoff
      const oldScreenshots = screenshots.filter(
        screenshot => new Date(screenshot.timestamp) < cutoffDate
      );
      
      // Delete each old screenshot
      for (const screenshot of oldScreenshots) {
        await this.deleteScreenshot(screenshot.id);
      }
    } catch (error) {
      console.error('Error cleaning up old screenshots:', error);
      throw new Error('Failed to clean up old screenshots');
    }
  }
}

// Create a singleton instance
export const screenCapture = new ScreenCapture();
