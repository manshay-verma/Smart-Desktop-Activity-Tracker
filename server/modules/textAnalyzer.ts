/**
 * Server-side Text Analyzer Module
 * Handles OCR and text processing from screenshots
 */

import { storage } from '../storage';

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
   * Initialize the text analyzer
   */
  async initialize(): Promise<void> {
    console.log('Text analyzer module initialized');
    // In a real implementation, this would initialize OCR libraries
  }
  
  /**
   * Analyze a screenshot to extract text using OCR
   */
  async analyzeScreenshot(screenshotId: number): Promise<TextAnalysisResult> {
    try {
      // Get the screenshot
      const screenshot = await storage.getScreenshot(screenshotId);
      if (!screenshot) {
        throw new Error(`Screenshot with ID ${screenshotId} not found`);
      }
      
      // In a real implementation, this would use OCR on the screenshot
      // For now, we'll return mock data
      const result: TextAnalysisResult = {
        windowTitle: 'Sample Window',
        applicationName: 'Sample Application',
        extractedText: 'Sample text extracted from screenshot',
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
      };
      
      // Update the screenshot with extracted text
      await this.updateScreenshotWithAnalysis(screenshotId, result);
      
      return result;
    } catch (error) {
      console.error(`Error analyzing screenshot ${screenshotId}:`, error);
      throw new Error('Failed to analyze screenshot');
    }
  }
  
  /**
   * Analyze a specific area of a screenshot
   */
  async analyzeScreenshotArea(
    screenshotId: number,
    x: number,
    y: number,
    width: number,
    height: number
  ): Promise<TextAnalysisResult> {
    try {
      // Get the screenshot
      const screenshot = await storage.getScreenshot(screenshotId);
      if (!screenshot) {
        throw new Error(`Screenshot with ID ${screenshotId} not found`);
      }
      
      // In a real implementation, this would crop and analyze the area
      // For now, we'll return mock data
      return {
        extractedText: `Text from area at (${x}, ${y})`,
        confidence: 75,
        areas: [
          {
            text: 'Area Text',
            bounds: { x: 0, y: 0, width, height },
            confidence: 75
          }
        ]
      };
    } catch (error) {
      console.error(`Error analyzing screenshot area ${screenshotId}:`, error);
      throw new Error('Failed to analyze screenshot area');
    }
  }
  
  /**
   * Update a screenshot record with OCR analysis results
   */
  private async updateScreenshotWithAnalysis(screenshotId: number, analysis: TextAnalysisResult): Promise<void> {
    try {
      // In a real implementation, this would update the screenshot record
      // with the extracted text and other OCR data
      // Our storage interface doesn't have this method yet
    } catch (error) {
      console.error(`Error updating screenshot ${screenshotId} with analysis:`, error);
      throw new Error('Failed to update screenshot with analysis');
    }
  }
  
  /**
   * Extract window title from OCR text
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

// Create a singleton instance
export const textAnalyzer = new TextAnalyzer();
