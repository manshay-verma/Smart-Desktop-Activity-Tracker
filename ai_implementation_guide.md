# AI Implementation Guide

This document explains how to implement, modify, or extend the AI components of the Smart Desktop Activity Tracker.

## AI Component Overview

The Smart Desktop Activity Tracker uses several AI components:

1. **Text Extraction and Analysis** (OCR + NLP)
2. **Pattern Recognition** (Unsupervised Learning)
3. **Automation Suggestion** (Rule-based + ML)
4. **User Behavior Modeling** (Statistical Analysis)

## 1. Text Analysis Module

### Location: `text_analyzer.py`

#### How It Works

The Text Analyzer extracts and processes text from screenshots using:
- Tesseract OCR for text extraction
- NLTK for natural language processing
- Custom rules for entity recognition

#### Key Components

```python
# Text extraction function
def extract_text_from_image(self, image_path):
    """
    Extract text from an image using OCR
    
    Args:
        image_path (str): Path to the image file
    
    Returns:
        str: Extracted text
    """
    try:
        # Use Tesseract OCR to extract text
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        self.shared_data["last_error"] = str(e)
        return ""

# Text analysis function
def analyze_text(self, text, context=None):
    """
    Analyze extracted text for patterns and meaning
    
    Args:
        text (str): The text to analyze
        context (dict, optional): Additional context information
    
    Returns:
        dict: Analysis results
    """
    # Perform basic NLP operations
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [w for w in tokens if w not in stop_words]
    
    # Extract structured information
    emails = self._extract_emails(text)
    urls = self._extract_urls(text)
    applications = self._identify_applications(text, context)
    
    return {
        "tokens": filtered_tokens,
        "word_count": len(tokens),
        "emails": emails,
        "urls": urls,
        "applications": applications
    }
```

#### How to Modify

To improve text extraction:
1. Add preprocessing for images (e.g., contrast enhancement)
2. Configure Tesseract parameters for your use case
3. Implement post-processing to clean up OCR results

Example improvement:
```python
def extract_text_from_image(self, image_path):
    try:
        # Load image
        image = cv2.imread(image_path)
        
        # Preprocess: Convert to grayscale and enhance contrast
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Use Tesseract with custom configuration
        custom_config = r'--oem 3 --psm 6 -l eng'
        text = pytesseract.image_to_string(gray, config=custom_config)
        
        # Post-process: Clean up common OCR errors
        text = self._clean_ocr_text(text)
        
        return text
    except Exception as e:
        self.shared_data["last_error"] = str(e)
        return ""
```

## 2. Pattern Recognition

### Location: `ml_integration.py`

#### How It Works

The ML integration module uses unsupervised learning to identify patterns in user behavior:

```python
class PatternRecognizer:
    def __init__(self):
        # Initialize ML models
        self.clustering_model = DBSCAN(eps=0.3, min_samples=5)
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.is_trained = False
        
    def train_models(self, activity_data):
        """
        Train ML models on activity data
        
        Args:
            activity_data (list): List of activity records
        """
        if not activity_data or len(activity_data) < 10:
            return False
            
        # Extract features
        features = self._extract_features(activity_data)
        
        # Train clustering model
        self.clustering_model.fit(features)
        
        # Set trained flag
        self.is_trained = True
        return True
        
    def detect_patterns(self, new_activities):
        """
        Detect patterns in new activities
        
        Args:
            new_activities (list): List of new activity records
        
        Returns:
            list: Detected patterns with metadata
        """
        if not self.is_trained:
            return []
            
        # Extract features from new activities
        features = self._extract_features(new_activities)
        
        # Predict clusters
        clusters = self.clustering_model.fit_predict(features)
        
        # Identify sequences within clusters
        patterns = self._find_sequences(new_activities, clusters)
        
        # Calculate confidence scores
        scored_patterns = self._score_patterns(patterns, new_activities)
        
        return scored_patterns
```

#### How to Modify

To improve pattern recognition:
1. Add more features to capture additional aspects of user behavior
2. Try different clustering algorithms (K-means, Hierarchical Clustering)
3. Implement more sophisticated sequence detection algorithms

Example improvement:
```python
def _extract_features(self, activities):
    """
    Extract features from activity data
    
    Args:
        activities (list): List of activity records
    
    Returns:
        numpy.ndarray: Feature matrix
    """
    features = []
    
    for activity in activities:
        # Basic features
        time_of_day = activity['timestamp'].hour / 24.0
        day_of_week = activity['timestamp'].weekday() / 7.0
        activity_type = self._encode_activity_type(activity['activity_type'])
        
        # Application context features
        app_vector = self._one_hot_encode_application(activity['application_name'])
        
        # Content-based features
        content_vector = self._extract_content_features(activity['description'])
        
        # Combine all features
        activity_features = np.concatenate([
            [time_of_day, day_of_week], 
            activity_type, 
            app_vector, 
            content_vector
        ])
        
        features.append(activity_features)
    
    return np.array(features)
```

## 3. Automation Suggestion Engine

### Location: `repetitive_task_suggestion.py`

#### How It Works

The suggestion engine analyzes detected patterns to suggest automation opportunities:

```python
def analyze_activity_history(self, days=7):
    """
    Analyze activity history to find repetitive patterns
    
    Args:
        days (int): Number of days of history to analyze
    
    Returns:
        list: Detected patterns
    """
    # Get activity logs from database
    cutoff_date = datetime.now() - timedelta(days=days)
    activity_logs = self.db_manager.get_activity_logs(after_date=cutoff_date)
    
    if not activity_logs:
        return []
    
    # Initialize ML models if needed
    if not hasattr(self, 'pattern_recognizer') or self.pattern_recognizer is None:
        self.pattern_recognizer = PatternRecognizer()
        
    # Train models
    self.pattern_recognizer.train_models(activity_logs)
    
    # Detect patterns
    patterns = self.pattern_recognizer.detect_patterns(activity_logs)
    
    return patterns

def generate_suggestions(self, min_confidence=0.7):
    """
    Generate automation suggestions based on detected patterns
    
    Args:
        min_confidence (float): Minimum confidence threshold
    
    Returns:
        list: Automation suggestions
    """
    # Analyze recent activity
    patterns = self.analyze_activity_history()
    
    # Filter patterns by confidence score
    qualified_patterns = [p for p in patterns if p['confidence'] >= min_confidence]
    
    suggestions = []
    for pattern in qualified_patterns:
        # Create a suggestion
        suggestion = {
            'title': self._generate_title(pattern),
            'description': self._generate_description(pattern),
            'confidence': pattern['confidence'],
            'pattern_data': pattern
        }
        
        # Save suggestion to database
        suggestion_id = self.db_manager.save_automation_suggestion(
            suggestion['title'],
            suggestion['description'],
            suggestion['confidence'],
            suggestion['pattern_data']
        )
        
        if suggestion_id:
            suggestion['id'] = suggestion_id
            suggestions.append(suggestion)
    
    return suggestions
```

#### How to Modify

To improve automation suggestions:
1. Add more sophisticated benefit analysis
2. Implement feedback-based learning
3. Add contextual awareness to suggestions

Example improvement:
```python
def _calculate_benefit_score(self, pattern):
    """
    Calculate a benefit score for automating a pattern
    
    Args:
        pattern (dict): Pattern data
    
    Returns:
        float: Benefit score (0-1)
    """
    # Frequency factor: How often does this pattern occur?
    frequency = min(pattern['occurrences'] / 20.0, 1.0)
    
    # Time savings factor: How much time would automation save?
    # Estimate based on pattern complexity (number of steps)
    complexity = len(pattern['sequence'])
    time_savings = min(complexity / 10.0, 1.0)
    
    # Manual effort factor: How manual is this task?
    # More keyboard/mouse actions = more manual
    action_count = sum(1 for step in pattern['sequence'] 
                      if step['activity_type'] in ['keyboard', 'mouse_click'])
    manual_effort = min(action_count / 15.0, 1.0)
    
    # Consistency factor: How consistent is this pattern?
    consistency = pattern['consistency_score']
    
    # Calculate weighted score
    benefit_score = (
        frequency * 0.3 +
        time_savings * 0.25 +
        manual_effort * 0.25 +
        consistency * 0.2
    )
    
    return benefit_score
```

## 4. User Behavior Modeling

### Location: Currently distributed across multiple modules

#### How It Works

User behavior modeling is handled by:
- Activity logging in `db_manager.py`
- Basic analysis in `ml_integration.py`
- Application-specific logic in various modules

#### How to Implement a Dedicated User Model

To create a more sophisticated user behavior model:

1. Create a new file `user_model.py`:

```python
class UserBehaviorModel:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.time_patterns = {}
        self.application_sequences = {}
        self.content_preferences = {}
        
    def build_model(self, days=30):
        """
        Build a comprehensive user behavior model
        
        Args:
            days (int): Number of days of history to analyze
        """
        # Get historical data
        cutoff_date = datetime.now() - timedelta(days=days)
        activity_logs = self.db_manager.get_activity_logs(after_date=cutoff_date)
        
        # Analyze time patterns
        self.time_patterns = self._analyze_time_patterns(activity_logs)
        
        # Analyze application usage sequences
        self.application_sequences = self._analyze_app_sequences(activity_logs)
        
        # Analyze content preferences
        self.content_preferences = self._analyze_content_preferences(activity_logs)
    
    def predict_next_activity(self, current_context):
        """
        Predict the next likely activity based on current context
        
        Args:
            current_context (dict): Current user context
        
        Returns:
            dict: Predicted next activity
        """
        # Calculate time-based predictions
        time_predictions = self._get_time_based_predictions(current_context)
        
        # Calculate sequence-based predictions
        sequence_predictions = self._get_sequence_predictions(current_context)
        
        # Calculate content-based predictions
        content_predictions = self._get_content_predictions(current_context)
        
        # Combine predictions with appropriate weights
        combined_predictions = self._combine_predictions(
            time_predictions,
            sequence_predictions,
            content_predictions
        )
        
        return combined_predictions
```

2. Integrate the model with existing modules:

```python
# In main.py, add:
from user_model import UserBehaviorModel

# Initialize user model
user_model = UserBehaviorModel(db_manager)

# Build initial model
user_model.build_model()

# Add to shared data
shared_data['user_model'] = user_model

# Schedule periodic model updates
def update_user_model():
    user_model.build_model()
    
# Schedule to run daily
schedule.every().day.at("03:00").do(update_user_model)
```

## Best Practices for AI Module Development

1. **Data Privacy**: 
   - Always respect user privacy
   - Process data locally
   - Minimize storage of sensitive information
   - Provide clear options for data deletion

2. **Performance Optimization**:
   - Run intensive ML operations in background threads
   - Use incremental learning where possible
   - Cache results for frequently accessed predictions
   - Monitor resource usage

3. **Error Handling**:
   - Implement graceful fallbacks for ML failures
   - Log errors for debugging
   - Never crash the application due to ML errors
   - Validate all AI-generated suggestions before presenting to user

4. **Testing AI Components**:
   - Create unit tests with known patterns
   - Test with edge cases (very large or small datasets)
   - Validate suggestions manually before deployment
   - Use A/B testing for new algorithms

## Integration Guidelines

When integrating new AI features:

1. Make new features optional and configurable
2. Allow users to enable/disable AI components
3. Start with conservative thresholds and gradually adjust
4. Collect feedback on AI-generated suggestions
5. Provide clear explanations for AI-driven recommendations