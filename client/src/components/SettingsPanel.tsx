import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { Save, Trash2, RotateCcw } from 'lucide-react';

export function SettingsPanel() {
  const [settings, setSettings] = useState({
    captureInterval: 1000,
    keepHistoryDays: 7,
    enableKeyLogging: true,
    enableScreenCapture: true,
    enableAutomationSuggestions: true,
    sidebarPosition: 'right',
    theme: 'light',
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  // Fetch settings
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('/api/settings');
        if (response.ok) {
          const data = await response.json();
          setSettings(data);
        }
      } catch (error) {
        console.error('Failed to fetch settings:', error);
        toast({
          title: 'Error',
          description: 'Failed to load your settings. Using defaults.',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchSettings();
  }, [toast]);

  // Update setting value
  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  // Save settings
  const saveSettings = async () => {
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        toast({
          title: 'Settings Saved',
          description: 'Your settings have been updated successfully.',
        });
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to save your settings. Please try again.',
        variant: 'destructive',
      });
    }
  };

  // Reset to default settings
  const resetSettings = () => {
    setSettings({
      captureInterval: 1000,
      keepHistoryDays: 7,
      enableKeyLogging: true,
      enableScreenCapture: true,
      enableAutomationSuggestions: true,
      sidebarPosition: 'right',
      theme: 'light',
    });
    
    toast({
      title: 'Settings Reset',
      description: 'Your settings have been reset to defaults. Click Save to apply.',
    });
  };

  // Clear all data
  const clearAllData = async () => {
    try {
      const response = await fetch('/api/data/clear', {
        method: 'POST',
      });

      if (response.ok) {
        toast({
          title: 'Data Cleared',
          description: 'All your tracked data has been cleared successfully.',
        });
      } else {
        throw new Error('Failed to clear data');
      }
    } catch (error) {
      console.error('Error clearing data:', error);
      toast({
        title: 'Error',
        description: 'Failed to clear your data. Please try again.',
        variant: 'destructive',
      });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex justify-center items-center h-40">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Settings</CardTitle>
        <CardDescription>
          Configure your activity tracking and application preferences
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Tracking Settings</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="captureInterval">Screenshot Capture Interval (ms)</Label>
              <Input
                id="captureInterval"
                type="number"
                min="500"
                max="10000"
                step="100"
                value={settings.captureInterval}
                onChange={(e) => handleSettingChange('captureInterval', parseInt(e.target.value))}
              />
              <p className="text-xs text-muted-foreground">
                How often to capture screenshots (minimum 500ms)
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="keepHistoryDays">Keep History (days)</Label>
              <Input
                id="keepHistoryDays"
                type="number"
                min="1"
                max="90"
                value={settings.keepHistoryDays}
                onChange={(e) => handleSettingChange('keepHistoryDays', parseInt(e.target.value))}
              />
              <p className="text-xs text-muted-foreground">
                How many days to retain activity history
              </p>
            </div>
          </div>
          
          <div className="space-y-4 pt-2">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="enableKeyLogging" className="mr-2">Enable Keyboard Logging</Label>
                <p className="text-xs text-muted-foreground">
                  Track keyboard input for activity analysis
                </p>
              </div>
              <Switch
                id="enableKeyLogging"
                checked={settings.enableKeyLogging}
                onCheckedChange={(checked) => handleSettingChange('enableKeyLogging', checked)}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="enableScreenCapture" className="mr-2">Enable Screen Capture</Label>
                <p className="text-xs text-muted-foreground">
                  Take screenshots for visual activity tracking
                </p>
              </div>
              <Switch
                id="enableScreenCapture"
                checked={settings.enableScreenCapture}
                onCheckedChange={(checked) => handleSettingChange('enableScreenCapture', checked)}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="enableAutomationSuggestions" className="mr-2">Enable Automation Suggestions</Label>
                <p className="text-xs text-muted-foreground">
                  Suggest automation based on repetitive tasks
                </p>
              </div>
              <Switch
                id="enableAutomationSuggestions"
                checked={settings.enableAutomationSuggestions}
                onCheckedChange={(checked) => handleSettingChange('enableAutomationSuggestions', checked)}
              />
            </div>
          </div>
        </div>
        
        <Separator />
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Interface Settings</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="sidebarPosition">Sidebar Position</Label>
              <Select
                value={settings.sidebarPosition}
                onValueChange={(value) => handleSettingChange('sidebarPosition', value)}
              >
                <SelectTrigger id="sidebarPosition">
                  <SelectValue placeholder="Select sidebar position" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="right">Right</SelectItem>
                  <SelectItem value="left">Left</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="theme">Theme</Label>
              <Select
                value={settings.theme}
                onValueChange={(value) => handleSettingChange('theme', value)}
              >
                <SelectTrigger id="theme">
                  <SelectValue placeholder="Select theme" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
        
        <Separator />
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Data Management</h3>
          
          <div className="flex flex-col sm:flex-row gap-2">
            <Button 
              variant="destructive" 
              className="flex items-center gap-2"
              onClick={clearAllData}
            >
              <Trash2 className="h-4 w-4" /> Clear All Data
            </Button>
            <Button 
              variant="outline" 
              className="flex items-center gap-2"
              onClick={resetSettings}
            >
              <RotateCcw className="h-4 w-4" /> Reset Settings
            </Button>
            <Button 
              className="flex items-center gap-2 sm:ml-auto"
              onClick={saveSettings}
            >
              <Save className="h-4 w-4" /> Save Settings
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            Clearing data will permanently remove all your tracked activities, screenshots, and logs.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
