/**
 * Screen Capture Module - Handles taking screenshots and processing them
 */

interface Screenshot {
  id?: number;
  fullScreenPath: string;
  mouseAreaPath: string;
  mouseX: number;
  mouseY: number;
  timestamp: Date;
}

class ScreenCapture {
  private mouseCropSize: number = 200; // Size of the area around mouse to crop (pixels)
  
  /**
   * Initialize screen capture module
   */
  public async initialize(): Promise<void> {
    console.log('Screen Capture module initialized');
    // In a web context, we'll be using the browser's capture API
    // but would need permissions
  }
  
  /**
   * Capture the current screen
   */
  public async captureScreen(): Promise<Screenshot> {
    try {
      // Get current mouse position
      const mousePosition = await this.getMousePosition();
      
      // In a real implementation we would:
      // 1. Use navigator.mediaDevices.getDisplayMedia() to capture the screen
      // 2. Draw the capture to a canvas
      // 3. Export the canvas to an image
      // 4. Crop a portion around the mouse
      
      // For this demo, we'll simulate by sending a request to our API
      const response = await fetch('/api/capture', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mouseX: mousePosition.x,
          mouseY: mousePosition.y,
          cropSize: this.mouseCropSize
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to capture screen');
      }
      
      const data = await response.json();
      
      // Return screenshot info
      return {
        id: data.id,
        fullScreenPath: data.fullScreenPath,
        mouseAreaPath: data.mouseAreaPath,
        mouseX: mousePosition.x,
        mouseY: mousePosition.y,
        timestamp: new Date(),
      };
    } catch (error) {
      console.error('Error capturing screen:', error);
      
      // Return a placeholder in case of error
      return {
        fullScreenPath: '/placeholder-screenshot.svg',
        mouseAreaPath: '/placeholder-mouse-area.svg',
        mouseX: 0,
        mouseY: 0,
        timestamp: new Date(),
      };
    }
  }
  
  /**
   * Get current mouse position
   */
  private async getMousePosition(): Promise<{ x: number, y: number }> {
    // In a browser context, we'd need to track mouse position with an event listener
    // For this demo, we'll simulate by getting the last position from the API
    try {
      const response = await fetch('/api/mouse-position');
      if (!response.ok) {
        throw new Error('Failed to get mouse position');
      }
      
      const { x, y } = await response.json();
      return { x, y };
    } catch (error) {
      console.error('Error getting mouse position:', error);
      // Return center of screen as fallback
      return {
        x: window.innerWidth / 2,
        y: window.innerHeight / 2
      };
    }
  }
  
  /**
   * Crop image around mouse cursor
   * Note: In a web context, this would use canvas to crop the image
   */
  private cropAroundMouse(imageSrc: string, mouseX: number, mouseY: number): Promise<string> {
    return new Promise((resolve, reject) => {
      // Create temp image to load the source
      const img = new Image();
      img.onload = () => {
        // Create a canvas element to do the cropping
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('Could not get canvas context'));
          return;
        }
        
        // Set dimensions to crop size
        canvas.width = this.mouseCropSize;
        canvas.height = this.mouseCropSize;
        
        // Calculate crop area with mouse at center
        const cropX = Math.max(0, mouseX - this.mouseCropSize / 2);
        const cropY = Math.max(0, mouseY - this.mouseCropSize / 2);
        
        // Draw the cropped part to the canvas
        ctx.drawImage(
          img,
          cropX, cropY, this.mouseCropSize, this.mouseCropSize, // Source rectangle
          0, 0, this.mouseCropSize, this.mouseCropSize          // Destination rectangle
        );
        
        // Convert canvas to data URL
        const croppedImageDataUrl = canvas.toDataURL('image/png');
        resolve(croppedImageDataUrl);
      };
      
      img.onerror = () => {
        reject(new Error('Failed to load image for cropping'));
      };
      
      img.src = imageSrc;
    });
  }
}

// Create singleton instance
export const screenCapture = new ScreenCapture();
