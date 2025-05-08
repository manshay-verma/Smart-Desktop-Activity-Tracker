import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";
import Dashboard from "@/pages/dashboard";
import { useEffect, useState } from "react";
import { FloatingSidebar } from "./components/FloatingSidebar";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  const [isTracking, setIsTracking] = useState<boolean>(false);
  const [activityLogs, setActivityLogs] = useState<any[]>([]);
  const [automationSuggestions, setAutomationSuggestions] = useState<any[]>([]);
  
  // Start tracking when app loads
  useEffect(() => {
    const initializeTracking = async () => {
      try {
        // Fetch user settings from server
        const response = await fetch('/api/settings');
        if (response.ok) {
          const settings = await response.json();
          // Initialize tracking with user settings
          setIsTracking(true);
        } else {
          // Use default settings if not found
          setIsTracking(true);
        }
      } catch (error) {
        console.error('Failed to initialize tracking:', error);
        // Start with default settings
        setIsTracking(true);
      }
    };

    initializeTracking();
    
    // Clean up on unmount
    return () => {
      setIsTracking(false);
    };
  }, []);

  // Mock function to add activity log (this would be replaced with actual tracked activities)
  const addActivityLog = (activity: any) => {
    setActivityLogs(prev => [activity, ...prev].slice(0, 50)); // Keep last 50 activities
  };

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
        <FloatingSidebar 
          isTracking={isTracking}
          onToggleTracking={() => setIsTracking(!isTracking)}
          activityLogs={activityLogs}
          automationSuggestions={automationSuggestions}
        />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
