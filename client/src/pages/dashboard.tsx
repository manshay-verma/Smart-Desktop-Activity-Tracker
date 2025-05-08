import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ActivityLog } from '@/components/ActivityLog';
import { AutomationSuggestions } from '@/components/AutomationSuggestions';
import { SettingsPanel } from '@/components/SettingsPanel';
import { ScreenshotViewer } from '@/components/ScreenshotViewer';
import { useToast } from '@/hooks/use-toast';
import { Clock, Activity, Cpu, Settings, BarChart2, Play, Pause } from 'lucide-react';

export default function Dashboard() {
  const [isTracking, setIsTracking] = useState(false);
  const [activeTab, setActiveTab] = useState('activity');
  const [activityData, setActivityData] = useState<any[]>([]);
  const [automationTasks, setAutomationTasks] = useState<any[]>([]);
  const [selectedScreenshot, setSelectedScreenshot] = useState<string | null>(null);
  const { toast } = useToast();

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch activity logs
        const activityResponse = await fetch('/api/activity-logs');
        if (activityResponse.ok) {
          const data = await activityResponse.json();
          setActivityData(data);
        }

        // Fetch automation tasks
        const automationResponse = await fetch('/api/automation-tasks');
        if (automationResponse.ok) {
          const data = await automationResponse.json();
          setAutomationTasks(data);
        }

        // Get tracking status
        const trackingResponse = await fetch('/api/tracking/status');
        if (trackingResponse.ok) {
          const { isActive } = await trackingResponse.json();
          setIsTracking(isActive);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load dashboard data. Please try again.',
          variant: 'destructive',
        });
      }
    };

    fetchData();
  }, [toast]);

  // Toggle tracking state
  const handleToggleTracking = async () => {
    try {
      const response = await fetch('/api/tracking/toggle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ isActive: !isTracking }),
      });

      if (response.ok) {
        setIsTracking(!isTracking);
        toast({
          title: isTracking ? 'Tracking Paused' : 'Tracking Started',
          description: isTracking ? 'Activity tracking has been paused.' : 'Now monitoring your desktop activity.',
        });
      } else {
        throw new Error('Failed to toggle tracking');
      }
    } catch (error) {
      console.error('Error toggling tracking:', error);
      toast({
        title: 'Error',
        description: 'Failed to toggle tracking. Please try again.',
        variant: 'destructive',
      });
    }
  };

  // View screenshot
  const handleViewScreenshot = (screenshotPath: string) => {
    setSelectedScreenshot(screenshotPath);
  };

  // Calculate statistics
  const totalActivities = activityData.length;
  const lastActivity = activityData[0]?.timestamp ? new Date(activityData[0].timestamp).toLocaleTimeString() : 'N/A';
  const automationCount = automationTasks.length;

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Smart Desktop Activity Tracker</h1>
          <p className="text-muted-foreground">Track, analyze, and automate your desktop activities</p>
        </div>
        <Button 
          onClick={handleToggleTracking}
          variant={isTracking ? "destructive" : "default"}
          className="flex items-center gap-2"
        >
          {isTracking ? (
            <>
              <Pause className="h-4 w-4" /> Pause Tracking
            </>
          ) : (
            <>
              <Play className="h-4 w-4" /> Start Tracking
            </>
          )}
        </Button>
      </div>

      {/* Dashboard overview cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Activity Count
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{totalActivities}</div>
            <CardDescription>Total tracked activities</CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              Last Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{lastActivity}</div>
            <CardDescription>Most recent tracked event</CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5 text-primary" />
              Automations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{automationCount}</div>
            <CardDescription>Available automation tasks</CardDescription>
          </CardContent>
        </Card>
      </div>

      {/* Main content tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="activity" className="flex items-center gap-2">
            <BarChart2 className="h-4 w-4" /> Activity Logs
          </TabsTrigger>
          <TabsTrigger value="automation" className="flex items-center gap-2">
            <Cpu className="h-4 w-4" /> Automation
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" /> Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="activity">
          <ActivityLog 
            activities={activityData} 
            onViewScreenshot={handleViewScreenshot}
          />
        </TabsContent>

        <TabsContent value="automation">
          <AutomationSuggestions 
            automationTasks={automationTasks}
            onAddTask={(task) => {
              setAutomationTasks([...automationTasks, task]);
              toast({
                title: 'Automation Added',
                description: `The task "${task.name}" has been added successfully.`,
              });
            }}
            onRemoveTask={(taskId) => {
              setAutomationTasks(automationTasks.filter(task => task.id !== taskId));
              toast({
                title: 'Automation Removed',
                description: 'The task has been removed successfully.',
              });
            }}
          />
        </TabsContent>

        <TabsContent value="settings">
          <SettingsPanel />
        </TabsContent>
      </Tabs>

      {/* Screenshot viewer modal */}
      {selectedScreenshot && (
        <ScreenshotViewer 
          screenshotUrl={selectedScreenshot} 
          onClose={() => setSelectedScreenshot(null)} 
        />
      )}
    </div>
  );
}
