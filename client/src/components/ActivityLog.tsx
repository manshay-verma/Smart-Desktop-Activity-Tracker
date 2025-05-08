import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Eye, Search, FileText, Calendar, MousePointer, Monitor, Keyboard } from 'lucide-react';

interface ActivityLogProps {
  activities: any[];
  onViewScreenshot: (screenshotPath: string) => void;
}

export function ActivityLog({ activities = [], onViewScreenshot }: ActivityLogProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');

  // Filter activities based on search term, date and type
  const filteredActivities = activities.filter(activity => {
    const matchesSearch = searchTerm === '' || 
      activity.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDate = selectedDate === '' || 
      new Date(activity.timestamp).toDateString() === new Date(selectedDate).toDateString();
    
    const matchesType = selectedType === '' || 
      activity.activityType === selectedType;
    
    return matchesSearch && matchesDate && matchesType;
  });

  // Get unique dates from activities
  const uniqueDates = [...new Set(activities.map(activity => 
    new Date(activity.timestamp).toDateString()
  ))];

  // Get unique activity types
  const uniqueTypes = [...new Set(activities.map(activity => activity.activityType))];

  // Get icon for activity type
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'mouse_click':
        return <MousePointer className="h-4 w-4" />;
      case 'keyboard':
        return <Keyboard className="h-4 w-4" />;
      case 'application':
        return <Monitor className="h-4 w-4" />;
      case 'file':
        return <FileText className="h-4 w-4" />;
      default:
        return <Monitor className="h-4 w-4" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>Activity Logs</span>
          <div className="flex items-center gap-2">
            <Input
              placeholder="Search activities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-xs h-8"
              prefix={<Search className="h-4 w-4 text-muted-foreground" />}
            />
            
            <select 
              className="h-8 rounded-md border px-2 text-sm"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            >
              <option value="">All Dates</option>
              {uniqueDates.map((date, index) => (
                <option key={index} value={date}>
                  {date}
                </option>
              ))}
            </select>
            
            <select 
              className="h-8 rounded-md border px-2 text-sm"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
            >
              <option value="">All Types</option>
              {uniqueTypes.map((type, index) => (
                <option key={index} value={type}>
                  {type.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Type</TableHead>
                <TableHead className="w-[40%]">Description</TableHead>
                <TableHead>Application</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredActivities.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    No activities found.
                  </TableCell>
                </TableRow>
              ) : (
                filteredActivities.map((activity, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        {new Date(activity.timestamp).toLocaleTimeString()}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className="flex items-center gap-1 capitalize"
                      >
                        {getActivityIcon(activity.activityType)}
                        {activity.activityType.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-[300px] truncate">
                      {activity.description}
                    </TableCell>
                    <TableCell>
                      {activity.data?.application || '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      {activity.screenshotId && (
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => onViewScreenshot(`/api/screenshots/${activity.screenshotId}`)}
                          className="h-8 w-8 p-0"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
