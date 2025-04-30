# Smart Desktop Activity Tracker: User Guide

## Getting Started

### Installation

1. Run `setup.bat` as administrator to install all required dependencies
2. Once setup is complete, run `start.bat` to launch the application
3. The application will start with a floating sidebar on your desktop

### Basic Usage

#### Main Interface

The floating sidebar provides quick access to:
- Current activity status
- Recent activity history
- Automation suggestions
- Recording controls for new automations
- Settings

You can:
- **Move the sidebar** by clicking and dragging the title bar
- **Collapse/Expand** by clicking the minimize button
- **Access settings** by clicking the gear icon

#### Activity Tracking

The application automatically tracks:
- Keyboard input (frequency, not actual keystrokes)
- Mouse movements and clicks
- Active applications and windows
- Screen content (via screenshots)

To control tracking:
1. Click the Settings icon in the sidebar
2. Enable/disable different tracking modules
3. Adjust capture frequency and sensitivity

#### Managing Automations

To create a new automation:
1. Click "Record" in the sidebar
2. Perform the sequence of actions you want to automate
3. Click "Stop" when finished
4. Give your automation a name
5. (Optional) Set triggers for automatic execution

To run an existing automation:
1. Click "Automations" in the sidebar
2. Select an automation from the list
3. Click "Run" to execute it

#### Reviewing Activity History

To review your activity history:
1. Click "History" in the sidebar
2. Browse through captured screenshots and activity logs
3. Filter by time period, application, or activity type
4. Select an item to view details

## Privacy Controls

### Sensitive Applications

To exclude sensitive applications:
1. Go to Settings > Privacy
2. Add applications to the exclusion list
3. The tracker will not capture screenshots or analyze text from these applications

### Data Retention

To control how long data is kept:
1. Go to Settings > Storage
2. Set your preferred retention period (1-30 days)
3. Data older than this period will be automatically deleted

### Manual Cleanup

To manually delete tracking data:
1. Go to Settings > Storage
2. Click "Clean Up Now"
3. Select what type of data to remove and confirm

## Advanced Features

### Automation Suggestions

The system automatically identifies repetitive tasks by:
1. Analyzing patterns in your activities
2. Identifying sequences that are performed frequently
3. Suggesting these as potential automations

When a suggestion appears:
- Review the detected pattern
- Choose "Implement" to create an automation
- Choose "Dismiss" to ignore the suggestion

### Customizing Triggers

To set up custom automation triggers:
1. Go to Automations
2. Select an automation
3. Click "Edit Triggers"
4. Choose from:
   - Time-based triggers (daily, weekdays, etc.)
   - Event-based triggers (application launch, file change, etc.)
   - Keyboard shortcut triggers

### Exporting Data

To export your activity data:
1. Go to Settings > Data
2. Click "Export"
3. Choose what data to include
4. Select a file format (CSV, JSON)
5. Choose a location to save the export

## Troubleshooting

### Application Not Responding

If the sidebar becomes unresponsive:
1. Right-click the system tray icon
2. Select "Restart Interface"

If the entire application freezes:
1. Close the application using Task Manager
2. Run `start.bat` to restart

### Database Issues

If you encounter database errors:
1. Run `fix_db.bat` to reset to SQLite
2. Run `test_db.py` to verify the connection

### Missing Screenshots

If screenshots are not being captured:
1. Check Settings > Privacy to ensure the application isn't excluded
2. Check storage space on your hard drive
3. Verify that screenshot module is enabled in settings

### High CPU/Memory Usage

If the application is using too many resources:
1. Reduce screenshot quality in Settings > Performance
2. Increase the interval between captures
3. Limit the number of screenshots stored