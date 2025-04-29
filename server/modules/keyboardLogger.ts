/**
 * Server-side Keyboard Logger Module
 * Handles keyboard event processing and storage
 */

import { storage } from '../storage';

interface KeyboardEvent {
  key: string;
  isSpecialKey: boolean;
  timestamp: Date;
  text?: string;
}

class KeyboardLogger {
  private specialKeys: Set<string> = new Set([
    'Shift', 'Control', 'Alt', 'Meta', 
    'Enter', 'Tab', 'Escape', 'Backspace', 'Delete',
    'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
    'Home', 'End', 'PageUp', 'PageDown'
  ]);
  
  /**
   * Initialize the keyboard logger
   */
  async initialize(): Promise<void> {
    console.log('Keyboard logger module initialized');
  }
  
  /**
   * Process a keyboard event from the client
   */
  async processKeyboardEvent(userId: number, event: KeyboardEvent): Promise<void> {
    try {
      // Create an activity log for this keyboard event
      await storage.createActivityLog({
        userId,
        activityType: 'keyboard',
        description: this.generateDescription(event),
        data: event,
        screenshotId: undefined
      });
    } catch (error) {
      console.error('Error processing keyboard event:', error);
      throw new Error('Failed to process keyboard event');
    }
  }
  
  /**
   * Generate a description for a keyboard event
   */
  private generateDescription(event: KeyboardEvent): string {
    if (event.isSpecialKey) {
      return `Pressed ${event.key}`;
    }
    
    if (event.text) {
      if (event.text.length > 20) {
        return `Typed text (${event.text.length} characters)`;
      }
      return `Typed "${event.text}"`;
    }
    
    return 'Keyboard activity';
  }
  
  /**
   * Check if a key is a special key
   */
  isSpecialKey(key: string): boolean {
    return this.specialKeys.has(key) || 
           (key.startsWith('F') && /F\d+/.test(key));
  }
}

// Create a singleton instance
export const keyboardLogger = new KeyboardLogger();
