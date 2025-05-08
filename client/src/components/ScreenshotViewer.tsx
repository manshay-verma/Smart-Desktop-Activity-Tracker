import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { X, ZoomIn, ZoomOut, PanelLeft, PanelRight } from 'lucide-react';

interface ScreenshotViewerProps {
  screenshotUrl: string;
  onClose: () => void;
}

export function ScreenshotViewer({ screenshotUrl, onClose }: ScreenshotViewerProps) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showFullScreen, setShowFullScreen] = useState(true);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [mouseAreaUrl, setMouseAreaUrl] = useState<string | null>(null);
  
  // Extract screenshot ID and fetch mouse area screenshot
  useEffect(() => {
    const fetchMouseAreaScreenshot = async () => {
      if (screenshotUrl) {
        const parts = screenshotUrl.split('/');
        const screenshotId = parts[parts.length - 1];
        
        try {
          // Assuming API endpoint for mouse area screenshot
          const mouseAreaUrl = `/api/screenshots/${screenshotId}/mouse-area`;
          // Check if mouse area exists
          const response = await fetch(mouseAreaUrl, { method: 'HEAD' });
          if (response.ok) {
            setMouseAreaUrl(mouseAreaUrl);
          }
        } catch (error) {
          console.error('Failed to fetch mouse area screenshot:', error);
        }
      }
    };
    
    fetchMouseAreaScreenshot();
  }, [screenshotUrl]);
  
  // Get mouse position from the screenshot metadata
  useEffect(() => {
    const fetchScreenshotMetadata = async () => {
      if (screenshotUrl) {
        const parts = screenshotUrl.split('/');
        const screenshotId = parts[parts.length - 1];
        
        try {
          const response = await fetch(`/api/screenshots/${screenshotId}/metadata`);
          if (response.ok) {
            const metadata = await response.json();
            if (metadata.mouseX && metadata.mouseY) {
              setMousePosition({
                x: metadata.mouseX,
                y: metadata.mouseY
              });
            }
          }
        } catch (error) {
          console.error('Failed to fetch screenshot metadata:', error);
        }
      }
    };
    
    fetchScreenshotMetadata();
  }, [screenshotUrl]);
  
  // Close on escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);
  
  // Handle zoom in
  const zoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.2, 3));
  };
  
  // Handle zoom out
  const zoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 0.2, 0.5));
  };
  
  return (
    <div className="screenshot-overlay" onClick={onClose}>
      <div 
        className="screenshot-container" 
        onClick={(e) => e.stopPropagation()}
        style={{ 
          transform: `scale(${zoomLevel})`,
          transition: 'transform 0.2s ease-out'
        }}
      >
        {/* Screenshot image */}
        <img 
          src={showFullScreen ? screenshotUrl : (mouseAreaUrl || screenshotUrl)} 
          alt="Screenshot" 
          className="rounded-md"
        />
        
        {/* Mouse position indicator (only shown on full screen) */}
        {showFullScreen && (
          <div 
            className="mouse-indicator" 
            style={{ 
              left: `${mousePosition.x}px`, 
              top: `${mousePosition.y}px` 
            }}
          />
        )}
        
        {/* Controls */}
        <div 
          className="absolute top-4 right-4 flex items-center gap-2 bg-black/50 p-2 rounded-md"
          onClick={(e) => e.stopPropagation()}
        >
          {mouseAreaUrl && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFullScreen(!showFullScreen)}
              className="text-white h-8 w-8 p-0"
              title={showFullScreen ? "Show Mouse Area" : "Show Full Screen"}
            >
              {showFullScreen ? <PanelRight size={16} /> : <PanelLeft size={16} />}
            </Button>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={zoomIn}
            className="text-white h-8 w-8 p-0"
            title="Zoom In"
          >
            <ZoomIn size={16} />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={zoomOut}
            className="text-white h-8 w-8 p-0"
            title="Zoom Out"
          >
            <ZoomOut size={16} />
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-white h-8 w-8 p-0"
            title="Close"
          >
            <X size={16} />
          </Button>
        </div>
      </div>
    </div>
  );
}
