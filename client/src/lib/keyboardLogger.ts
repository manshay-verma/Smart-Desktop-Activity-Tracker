/**
 * Keyboard Logger - Tracks and analyzes keyboard input
 */

interface KeyboardEvent {
  key: string;
  isSpecialKey: boolean;
  timestamp: Date;
  text?: string;
}

class KeyboardLogger {
  private isLogging: boolean = false;
  private keyBuffer: string[] = [];
  private specialKeys: Set<string> = new Set([
    'Shift', 'Control', 'Alt', 'Meta', 
    'Enter', 'Tab', 'Escape', 'Backspace', 'Delete',
    'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
    'Home', 'End', 'PageUp', 'PageDown'
  ]);
  private listeners: { [key: string]: Function[] } = {
    'keypress': []
  };
  private keyPressHandler: (e: any) => void;

  constructor() {
    // Initialize bound event handler
    this.keyPressHandler = this.handleKeyPress.bind(this);
  }

  /**
   * Initialize keyboard logger
   */
  public async initialize(): Promise<void> {
    console.log('Keyboard Logger initialized');
  }

  /**
   * Start logging keyboard input
   */
  public start(): void {
    if (this.isLogging) return;

    this.isLogging = true;
    console.log('Keyboard logging started');

    // Attach event listeners
    document.addEventListener('keydown', this.keyPressHandler);

    // Clear buffer
    this.keyBuffer = [];
  }

  /**
   * Stop logging keyboard input
   */
  public stop(): void {
    if (!this.isLogging) return;

    this.isLogging = false;
    console.log('Keyboard logging stopped');

    // Remove event listeners
    document.removeEventListener('keydown', this.keyPressHandler);

    // Flush buffer if there's anything left
    this.flushKeyBuffer();
  }

  /**
   * Handle key press events
   */
  private handleKeyPress(event: KeyboardEvent): void {
    if (!this.isLogging) return;

    const key = event.key;
    const isSpecialKey = this.specialKeys.has(key) || key.startsWith('F') && /F\d+/.test(key);

    // For special keys, emit immediately
    if (isSpecialKey) {
      const keyEvent: KeyboardEvent = {
        key,
        isSpecialKey: true,
        timestamp: new Date()
      };
      this.notifyListeners('keypress', keyEvent);
      return;
    }

    // For regular keys, add to buffer
    this.keyBuffer.push(key);

    // Check if we should flush the buffer (e.g., on space, punctuation, or buffer size)
    if (
      key === ' ' || 
      ['.', ',', '!', '?', ';', ':', '\n'].includes(key) ||
      this.keyBuffer.length >= 20
    ) {
      this.flushKeyBuffer();
    }
  }

  /**
   * Flush key buffer and notify listeners
   */
  private flushKeyBuffer(): void {
    if (this.keyBuffer.length === 0) return;

    const text = this.keyBuffer.join('');
    this.keyBuffer = [];

    const keyEvent: KeyboardEvent = {
      key: 'text-input',
      isSpecialKey: false,
      text,
      timestamp: new Date()
    };

    this.notifyListeners('keypress', keyEvent);
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
export const keyboardLogger = new KeyboardLogger();
