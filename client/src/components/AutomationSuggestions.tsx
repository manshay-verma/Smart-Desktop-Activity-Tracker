import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Zap, Plus, Play, Trash2, Edit, LayoutList, Clock, MousePointer, Keyboard, MousePointerClick } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface AutomationSuggestionsProps {
  automationTasks: any[];
  onAddTask: (task: any) => void;
  onRemoveTask: (taskId: number) => void;
}

export function AutomationSuggestions({ 
  automationTasks = [], 
  onAddTask, 
  onRemoveTask 
}: AutomationSuggestionsProps) {
  const [activeTab, setActiveTab] = useState('available');
  const [newTaskName, setNewTaskName] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskSteps, setNewTaskSteps] = useState<string[]>(['']);
  const [newTaskTriggers, setNewTaskTriggers] = useState<any[]>([{ type: 'time', value: '' }]);
  const [showNewTaskDialog, setShowNewTaskDialog] = useState(false);
  const { toast } = useToast();

  // Handle task execution
  const executeTask = async (taskId: number) => {
    try {
      const response = await fetch(`/api/automation-tasks/${taskId}/execute`, {
        method: 'POST',
      });
      
      if (response.ok) {
        toast({
          title: 'Task Executed',
          description: 'The automation task was executed successfully.',
        });
      } else {
        throw new Error('Failed to execute task');
      }
    } catch (error) {
      console.error('Error executing task:', error);
      toast({
        title: 'Execution Failed',
        description: 'Failed to execute the automation task. Please try again.',
        variant: 'destructive',
      });
    }
  };

  // Add a step to new task
  const addStep = () => {
    setNewTaskSteps([...newTaskSteps, '']);
  };

  // Update a step
  const updateStep = (index: number, value: string) => {
    const updatedSteps = [...newTaskSteps];
    updatedSteps[index] = value;
    setNewTaskSteps(updatedSteps);
  };

  // Remove a step
  const removeStep = (index: number) => {
    const updatedSteps = newTaskSteps.filter((_, i) => i !== index);
    setNewTaskSteps(updatedSteps);
  };

  // Add a trigger
  const addTrigger = () => {
    setNewTaskTriggers([...newTaskTriggers, { type: 'time', value: '' }]);
  };

  // Update a trigger
  const updateTrigger = (index: number, field: string, value: string) => {
    const updatedTriggers = [...newTaskTriggers];
    updatedTriggers[index] = { ...updatedTriggers[index], [field]: value };
    setNewTaskTriggers(updatedTriggers);
  };

  // Remove a trigger
  const removeTrigger = (index: number) => {
    const updatedTriggers = newTaskTriggers.filter((_, i) => i !== index);
    setNewTaskTriggers(updatedTriggers);
  };

  // Create new task
  const handleCreateTask = () => {
    if (!newTaskName.trim()) {
      toast({
        title: 'Error',
        description: 'Task name is required.',
        variant: 'destructive',
      });
      return;
    }

    // Filter out empty steps
    const filteredSteps = newTaskSteps.filter(step => step.trim() !== '');
    if (filteredSteps.length === 0) {
      toast({
        title: 'Error',
        description: 'At least one step is required.',
        variant: 'destructive',
      });
      return;
    }

    const newTask = {
      id: Date.now(), // Temporary ID
      name: newTaskName,
      description: newTaskDescription,
      steps: filteredSteps,
      triggers: newTaskTriggers,
      executionCount: 0,
      isActive: true,
    };

    onAddTask(newTask);
    
    // Reset form
    setNewTaskName('');
    setNewTaskDescription('');
    setNewTaskSteps(['']);
    setNewTaskTriggers([{ type: 'time', value: '' }]);
    setShowNewTaskDialog(false);
  };

  // Get trigger type icon
  const getTriggerIcon = (type: string) => {
    switch (type) {
      case 'time':
        return <Clock className="h-4 w-4" />;
      case 'mouse':
        return <MousePointer className="h-4 w-4" />;
      case 'keyboard':
        return <Keyboard className="h-4 w-4" />;
      case 'click':
        return <MousePointerClick className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Automation Tasks</h2>
        <Dialog open={showNewTaskDialog} onOpenChange={setShowNewTaskDialog}>
          <DialogTrigger asChild>
            <Button size="sm" className="flex items-center gap-2">
              <Plus className="h-4 w-4" /> Add New Task
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create New Automation Task</DialogTitle>
              <DialogDescription>
                Define steps and triggers for your automated task.
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Task Name</label>
                <Input 
                  value={newTaskName}
                  onChange={(e) => setNewTaskName(e.target.value)}
                  placeholder="E.g., Open Chrome and load Gmail"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Textarea 
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  placeholder="What does this automation do?"
                  rows={2}
                />
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium">Steps</label>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={addStep}
                    className="h-6 px-2"
                  >
                    <Plus className="h-3 w-3 mr-1" /> Add Step
                  </Button>
                </div>
                
                <div className="space-y-2 max-h-[200px] overflow-y-auto p-1">
                  {newTaskSteps.map((step, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-medium">
                        {index + 1}
                      </div>
                      <Input 
                        value={step}
                        onChange={(e) => updateStep(index, e.target.value)}
                        placeholder={`Step ${index + 1}`}
                        className="flex-1"
                      />
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => removeStep(index)}
                        disabled={newTaskSteps.length <= 1}
                        className="h-8 w-8 p-0"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium">Triggers</label>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={addTrigger}
                    className="h-6 px-2"
                  >
                    <Plus className="h-3 w-3 mr-1" /> Add Trigger
                  </Button>
                </div>
                
                <div className="space-y-2 max-h-[150px] overflow-y-auto p-1">
                  {newTaskTriggers.map((trigger, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <select
                        value={trigger.type}
                        onChange={(e) => updateTrigger(index, 'type', e.target.value)}
                        className="h-9 rounded-md border px-2 text-sm"
                      >
                        <option value="time">Time</option>
                        <option value="mouse">Mouse Position</option>
                        <option value="keyboard">Keyboard Shortcut</option>
                        <option value="click">Mouse Click</option>
                      </select>
                      
                      <Input 
                        value={trigger.value}
                        onChange={(e) => updateTrigger(index, 'value', e.target.value)}
                        placeholder={trigger.type === 'time' ? 'HH:MM' : 'Value'}
                        className="flex-1"
                      />
                      
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => removeTrigger(index)}
                        disabled={newTaskTriggers.length <= 1}
                        className="h-8 w-8 p-0"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowNewTaskDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateTask}>
                Create Task
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="available" className="flex items-center gap-2">
            <LayoutList className="h-4 w-4" /> Available Tasks
          </TabsTrigger>
          <TabsTrigger value="suggested" className="flex items-center gap-2">
            <Zap className="h-4 w-4" /> Suggested Tasks
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="available">
          {automationTasks.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-muted-foreground mb-4">
                  No automation tasks available. Create a new task to get started.
                </p>
                <Button 
                  onClick={() => setShowNewTaskDialog(true)}
                  className="flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" /> Create Task
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {automationTasks.map((task) => (
                <Card key={task.id}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex justify-between items-center">
                      <span className="flex items-center gap-2">
                        <Zap className="h-5 w-5 text-primary" />
                        {task.name}
                      </span>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Delete Automation Task</AlertDialogTitle>
                            <AlertDialogDescription>
                              Are you sure you want to delete this task? This action cannot be undone.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction onClick={() => onRemoveTask(task.id)}>
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </CardTitle>
                    <CardDescription>{task.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <h4 className="text-sm font-medium mb-1">Steps:</h4>
                        <ul className="text-sm space-y-1 ml-1">
                          {task.steps.map((step: string, index: number) => (
                            <li key={index} className="flex items-start gap-2">
                              <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center text-xs font-medium mt-0.5">
                                {index + 1}
                              </div>
                              <span>{step}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium mb-1">Triggers:</h4>
                        <div className="flex flex-wrap gap-2">
                          {task.triggers.map((trigger: any, index: number) => (
                            <div 
                              key={index}
                              className="flex items-center gap-1 text-xs bg-secondary px-2 py-1 rounded"
                            >
                              {getTriggerIcon(trigger.type)}
                              <span className="capitalize">{trigger.type}:</span>
                              <span className="font-medium">{trigger.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div className="pt-2 flex justify-between items-center">
                        <div className="text-xs text-muted-foreground">
                          Run {task.executionCount} times
                        </div>
                        <Button 
                          size="sm" 
                          onClick={() => executeTask(task.id)}
                          className="flex items-center gap-1"
                        >
                          <Play className="h-3 w-3" /> Run Now
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="suggested">
          <Card>
            <CardHeader>
              <CardTitle>Task Suggestions</CardTitle>
              <CardDescription>
                Suggested automations based on your activity patterns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center p-6">
                <p className="text-muted-foreground mb-4">
                  No suggestions available yet. The system will analyze your activity patterns
                  and suggest potential automation tasks as you use the application.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
