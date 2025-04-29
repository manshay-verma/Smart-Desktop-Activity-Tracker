# Smart Desktop Activity Tracker

A powerful Windows desktop application for tracking user activity, analyzing work patterns, and suggesting automation opportunities.

## Features

- **Activity Monitoring**: Track keyboard and mouse activity to understand work patterns
- **Screenshot Capture**: Automatically capture and analyze screenshots based on activity triggers
- **Text Analysis**: Extract and analyze text from screenshots to identify application usage
- **Automation Suggestion**: Identify repetitive tasks and suggest automation opportunities
- **User-Friendly Interface**: Real-time activity display and customization options

## System Requirements

- Windows 10/11
- Python 3.8 or newer
- 4GB RAM minimum (8GB recommended)
- 100MB free disk space plus storage for screenshots

## Installation

See [Installation Guide](installation_guide.md) for detailed setup instructions.

Quick start:
1. Run `setup.bat` as administrator
2. After setup completes, run `start.bat`

## Usage

### Main Interface

The application runs with a floating sidebar that can be:
- Expanded or collapsed
- Moved around the screen
- Set to auto-hide when not in use

### Activity Tracking

- Activity is tracked automatically in the background
- Screenshots are taken based on configured triggers
- Text is extracted and analyzed from screenshots
- Repetitive patterns are identified for automation

### Automation

- Identify repetitive tasks through pattern recognition
- Record and execute automation sequences
- Customize automation triggers
- Manage suggested automations

## Configuration

- **Settings**: Customize appearance, tracking intervals, and notifications
- **Privacy**: Control what data is captured and stored
- **Storage**: Manage screenshot retention and database cleanup
- **Automation**: Configure trigger sensitivities and execution preferences

## Troubleshooting

See the [Installation Guide](installation_guide.md) for common troubleshooting steps.

For database issues, run:
```
fix_db.bat
```

## Privacy Considerations

- All data is stored locally on your machine
- No data is transmitted to external servers
- Option to exclude sensitive applications from tracking
- Automatic cleanup of old data based on configured retention period

## License

[MIT License](LICENSE)

## Acknowledgements

- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI Framework
- [OpenCV](https://opencv.org/) - Image Processing
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Text Extraction
- [scikit-learn](https://scikit-learn.org/) - Machine Learning