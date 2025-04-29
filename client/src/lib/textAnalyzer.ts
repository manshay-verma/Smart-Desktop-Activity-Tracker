/**
 * Text Analyzer Module - Handles OCR and text processing
 */

interface TextAnalysisResult {
  windowTitle?: string;
  applicationName?: string;
  extractedText: string;
  confidence: number;
  areas: Array<{
    text: string;
    bounds: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
    confidence: number;
  }>;
}

class TextAnalyzer {
  /**
   * Initialize text analyzer
   */
  public async initialize(): Promise<void> {
    console.log('Text Analyzer initialized');
    // In a real implementation, we might preload OCR libraries here
  }
  
  /**
   * Analyze an image to extract text using OCR
   */
  public async analyzeImage(imagePath: string): Promise<TextAnalysisResult> {
    try {
      // In a real implementation, we would:
      // 1. Send the image to a server-side OCR service
      // 2. Process the results
      
      // For this demo, we'll simulate by calling our API
      const response = await fetch('/api/ocr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          imagePath
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze image');
      }
      
      const data = await response.json();
      
      // Extract window title and application name from OCR results
      const windowTitle = this.extractWindowTitle(data.extractedText);
      const applicationName = this.extractApplicationName(data.extractedText);
      
      return {
        windowTitle,
        applicationName,
        extractedText: data.extractedText,
        confidence: data.confidence,
        areas: data.areas || []
      };
    } catch (error) {
      console.error('Error analyzing image:', error);
      
      // Return empty result in case of error
      return {
        extractedText: '',
        confidence: 0,
        areas: []
      };
    }
  }
  
  /**
   * Analyze text from a specific area of the screen
   */
  public async analyzeArea(
    imagePath: string, 
    x: number, 
    y: number, 
    width: number, 
    height: number
  ): Promise<TextAnalysisResult> {
    try {
      // In a real implementation, we would:
      // 1. Crop the image to the specified area
      // 2. Send the cropped image to OCR service
      
      // For this demo, we'll simulate by calling our API
      const response = await fetch('/api/ocr/area', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          imagePath,
          x,
          y,
          width,
          height
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze image area');
      }
      
      const data = await response.json();
      
      return {
        extractedText: data.extractedText,
        confidence: data.confidence,
        areas: data.areas || []
      };
    } catch (error) {
      console.error('Error analyzing image area:', error);
      
      // Return empty result in case of error
      return {
        extractedText: '',
        confidence: 0,
        areas: []
      };
    }
  }
  
  /**
   * Extract window title from OCR text
   * This uses heuristics to identify the likely window title
   */
  private extractWindowTitle(text: string): string | undefined {
    if (!text) return undefined;
    
    // Common patterns for window titles
    // 1. Look for text followed by " - Program Name"
    const dashMatch = text.match(/(.+) - ([\w\s]+)$/);
    if (dashMatch) {
      return dashMatch[0];
    }
    
    // 2. For browsers, look for "Page Name - Browser Name"
    const browserMatch = text.match(/(.+) - (Chrome|Firefox|Edge|Safari|Opera)/);
    if (browserMatch) {
      return browserMatch[0];
    }
    
    // 3. Look for the first line that might be a title
    const lines = text.split('\n').filter(line => line.trim().length > 0);
    if (lines.length > 0) {
      // Check if first line is reasonable length for a title
      if (lines[0].length > 3 && lines[0].length < 100) {
        return lines[0];
      }
    }
    
    return undefined;
  }
  
  /**
   * Extract application name from OCR text
   */
  private extractApplicationName(text: string): string | undefined {
    if (!text) return undefined;
    
    // Common application patterns
    const appPatterns = [
      // Browser pattern: "Page Name - Chrome"
      { regex: / - (Chrome|Firefox|Edge|Safari|Opera)$/, group: 1 },
      
      // Office apps: "Document - Word"
      { regex: / - (Word|Excel|PowerPoint|Outlook)$/, group: 1 },
      
      // Code editors
      { regex: / - (Visual Studio Code|Sublime Text|Atom|PyCharm|IntelliJ IDEA)$/, group: 1 },
      
      // Generic pattern for windows apps
      { regex: / - ([\w\s]+)$/, group: 1 }
    ];
    
    for (const pattern of appPatterns) {
      const match = text.match(pattern.regex);
      if (match && match[pattern.group]) {
        return match[pattern.group];
      }
    }
    
    return undefined;
  }
}

// Create singleton instance
export const textAnalyzer = new TextAnalyzer();
