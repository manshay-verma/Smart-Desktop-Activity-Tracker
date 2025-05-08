import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ChevronRight, ChevronLeft, Activity, Zap, Settings, X } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

interface FloatingSidebarProps {
  isTracking: boolean;
  onToggleTracking: () => void;
  activityLogs: any[];
  automationSuggestions: any[];
}

export function FloatingSidebar({
  isTracking,
  onToggleTracking,
  activityLogs,
  automationSuggestions,
}: FloatingSidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [position, setPosition] = useState<'left' | 'right'>('right');
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('activity');

  // Check local storage for position preference
  useEffect(() => {
    const savedPosition = localStorage.getItem('sidebar-position');
    if (savedPosition === 'left' || savedPosition === 'right') {
      setPosition(savedPosition);
    }
  }, []);

  // Save position preference
  const togglePosition = () => {
    const newPosition = position === 'right' ? 'left' : 'right';
    setPosition(newPosition);
    localStorage.setItem('sidebar-position', newPosition);
  };

  // Handle automation suggestion click
  const handleAutomationClick = (suggestion: any) => {
    toast({
      title: 'Automation Executed',
      description: `Performed: ${suggestion.description}`,
    });
  };

  return (
    <div className={`floating-sidebar ${position} ${isCollapsed ? 'collapsed' : ''} bg-sidebar`}>
      {/* Toggle button */}
      <div 
        className="sidebar-toggle bg-sidebar-primary text-sidebar-primary-foreground"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {position === 'right' ? (
          isCollapsed ? <ChevronLeft size={16} /> : <ChevronRight size={16} />
        ) : (
          isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />
        )}
      </div>
      
      {/* Header */}
      <div className="p-4 bg-sidebar-primary text-sidebar-primary-foreground flex justify-between items-center">
        <h2 className="text-lg font-semibold">Activity Tracker</h2>
        <div className="flex items-center space-x-2">
          <Switch 
            id="tracking-switch" 
            checked={isTracking} 
            onCheckedChange={onToggleTracking} 
          />
          <Label htmlFor="tracking-switch" className="text-xs">
            {isTracking ? 'On' : 'Off'}
          </Label>
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-hidden">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
          <TabsList className="w-full justify-around bg-sidebar border-b border-sidebar-border">
            <TabsTrigger value="activity" className="flex-1 text-xs py-2">
              <Activity size={14} className="mr-1" /> Activity
            </TabsTrigger>
            <TabsTrigger value="automation" className="flex-1 text-xs py-2">
              <Zap size={14} className="mr-1" /> Automation
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex-1 text-xs py-2">
              <Settings size={14} className="mr-1" /> Settings
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="activity" className="flex-1 overflow-y-auto p-0 m-0">
            <div className="p-2">
              <h3 className="text-sm font-medium mb-2">Recent Activity</h3>
              
              {activityLogs.length === 0 ? (
                <div className="text-sm text-muted-foreground text-center p-4">
                  No activity recorded yet.
                </div>
              ) : (
                <div className="space-y-2">
                  {activityLogs.map((log, index) => (
                    <div 
                      key={index} 
                      className="activity-item bg-sidebar-accent/10 p-2 rounded-md text-xs"
                    >
                      <div className="font-medium">{log.description}</div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="automation" className="flex-1 overflow-y-auto p-0 m-0">
            <div className="p-2">
              <h3 className="text-sm font-medium mb-2">Suggestions</h3>
              
              {automationSuggestions.length === 0 ? (
                <div className="text-sm text-muted-foreground text-center p-4">
                  No automation suggestions available.
                </div>
              ) : (
                <div className="space-y-2">
                  {automationSuggestions.map((suggestion, index) => (
                    <div 
                      key={index} 
                      className="bg-sidebar-accent/10 p-2 rounded-md text-xs"
                    >
                      <div className="font-medium">{suggestion.title}</div>
                      <div className="my-1">{suggestion.description}</div>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="w-full mt-1 h-7 text-xs"
                        onClick={() => handleAutomationClick(suggestion)}
                      >
                        <Zap size={12} className="mr-1" /> Run Now
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="settings" className="flex-1 overflow-y-auto p-0 m-0">
            <div className="p-3 space-y-3">
              <div className="space-y-1">
                <Label htmlFor="position-toggle">Sidebar Position</Label>
                <div className="flex items-center">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={togglePosition}
                    className="w-full"
                  >
                    {position === 'right' ? 'Right Side' : 'Left Side'}
                  </Button>
                </div>
              </div>
              
              <div className="space-y-1">
                <Label>Recording Options</Label>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="keyboard-logging" className="text-xs cursor-pointer">
                      Keyboard Logging
                    </Label>
                    <Switch id="keyboard-logging" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="screen-capture" className="text-xs cursor-pointer">
                      Screen Capture
                    </Label>
                    <Switch id="screen-capture" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="auto-suggestions" className="text-xs cursor-pointer">
                      Automation Suggestions
                    </Label>
                    <Switch id="auto-suggestions" defaultChecked />
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
