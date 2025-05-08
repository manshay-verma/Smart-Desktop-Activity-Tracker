"""
Machine Learning Integration Module
Analyzes collected data to detect patterns and provide intelligent suggestions
"""

import os
import time
import logging
import threading
import json
import pickle
from datetime import datetime
import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from utils import setup_logging
from config import CONFIG

# Setup logging
logger = setup_logging()

class MLIntegration:
    """
    Provides ML-based pattern recognition and predictions
    """
    def __init__(self, data_dir, shared_data):
        """
        Initialize the ML integration module
        
        Args:
            data_dir (str): Directory for ML data
            shared_data (dict): Shared data dictionary for inter-module communication
        """
        self.data_dir = data_dir
        self.shared_data = shared_data
        self.running = False
        
        # Create ML directory
        self.ml_dir = os.path.join(data_dir, "ml_models")
        if not os.path.exists(self.ml_dir):
            os.makedirs(self.ml_dir)
        
        # ML parameters
        self.train_interval = CONFIG.get('ml_train_interval', 3600)  # Train every hour
        self.min_samples_for_training = CONFIG.get('min_samples_for_training', 50)
        self.last_training_time = 0
        
        # ML models
        self.activity_classifier = None
        self.time_predictor = None
        self.task_cluster_model = None
        
        # Load existing models
        self._load_models()
        
        logger.info("ML Integration Module initialized")
    
    def start(self):
        """Start ML processing"""
        logger.info("Starting ML integration")
        self.running = True
        
        # Main ML loop
        while self.running:
            try:
                # Check if it's time to train/retrain models
                current_time = time.time()
                if current_time - self.last_training_time > self.train_interval:
                    self._train_models()
                    self.last_training_time = current_time
                
                # Generate predictions and suggestions
                self._generate_predictions()
                
                # Sleep before next processing
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in ML processing: {e}")
                time.sleep(300)  # Sleep longer on error (5 minutes)
    
    def stop(self):
        """Stop ML processing"""
        logger.info("Stopping ML integration")
        self.running = False
        
        # Save models before stopping
        self._save_models()
    
    def _load_models(self):
        """Load existing ML models if available"""
        try:
            # Activity classifier
            activity_model_path = os.path.join(self.ml_dir, "activity_classifier.pkl")
            if os.path.exists(activity_model_path):
                with open(activity_model_path, 'rb') as f:
                    self.activity_classifier = pickle.load(f)
                logger.info("Loaded activity classifier model")
            
            # Time predictor
            time_model_path = os.path.join(self.ml_dir, "time_predictor.pkl")
            if os.path.exists(time_model_path):
                with open(time_model_path, 'rb') as f:
                    self.time_predictor = pickle.load(f)
                logger.info("Loaded time predictor model")
            
            # Task cluster model
            cluster_model_path = os.path.join(self.ml_dir, "task_cluster_model.pkl")
            if os.path.exists(cluster_model_path):
                with open(cluster_model_path, 'rb') as f:
                    self.task_cluster_model = pickle.load(f)
                logger.info("Loaded task cluster model")
            
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")
    
    def _save_models(self):
        """Save trained ML models"""
        try:
            # Activity classifier
            if self.activity_classifier:
                activity_model_path = os.path.join(self.ml_dir, "activity_classifier.pkl")
                with open(activity_model_path, 'wb') as f:
                    pickle.dump(self.activity_classifier, f)
                logger.info("Saved activity classifier model")
            
            # Time predictor
            if self.time_predictor:
                time_model_path = os.path.join(self.ml_dir, "time_predictor.pkl")
                with open(time_model_path, 'wb') as f:
                    pickle.dump(self.time_predictor, f)
                logger.info("Saved time predictor model")
            
            # Task cluster model
            if self.task_cluster_model:
                cluster_model_path = os.path.join(self.ml_dir, "task_cluster_model.pkl")
                with open(cluster_model_path, 'wb') as f:
                    pickle.dump(self.task_cluster_model, f)
                logger.info("Saved task cluster model")
            
        except Exception as e:
            logger.error(f"Error saving ML models: {e}")
    
    def _train_models(self):
        """Train or retrain ML models with collected data"""
        try:
            logger.info("Training ML models")
            
            # Collect training data from logs
            training_data = self._collect_training_data()
            
            # Skip if not enough data
            if len(training_data) < self.min_samples_for_training:
                logger.info(f"Not enough training data: {len(training_data)} samples (need {self.min_samples_for_training})")
                return
            
            # Train activity classifier
            self._train_activity_classifier(training_data)
            
            # Train time predictor
            self._train_time_predictor(training_data)
            
            # Train task clustering
            self._train_task_clustering(training_data)
            
            # Save trained models
            self._save_models()
            
            logger.info("ML model training completed")
            
        except Exception as e:
            logger.error(f"Error training ML models: {e}")
    
    def _collect_training_data(self):
        """
        Collect and prepare training data from logs
        
        Returns:
            list: List of training samples
        """
        training_data = []
        
        try:
            # Collect text analysis results
            analysis_dir = os.path.join(self.data_dir, "text_analysis")
            if os.path.exists(analysis_dir):
                for filename in os.listdir(analysis_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(analysis_dir, filename)
                        try:
                            with open(file_path, 'r') as f:
                                analysis = json.load(f)
                                
                                # Extract features
                                sample = {
                                    'timestamp': analysis.get('timestamp', ''),
                                    'ocr_text': analysis.get('ocr_text', ''),
                                    'detected_apps': analysis.get('detected_apps', []),
                                    'active_window': analysis.get('active_window', ''),
                                    'description': analysis.get('description', '')
                                }
                                
                                # Parse timestamp
                                try:
                                    dt = datetime.strptime(sample['timestamp'], "%Y%m%d_%H%M%S")
                                    sample['hour'] = dt.hour
                                    sample['day_of_week'] = dt.weekday()
                                except:
                                    sample['hour'] = 0
                                    sample['day_of_week'] = 0
                                
                                training_data.append(sample)
                        except:
                            continue
            
            logger.info(f"Collected {len(training_data)} training samples")
            
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
        
        return training_data
    
    def _train_activity_classifier(self, training_data):
        """
        Train activity classifier model
        
        Args:
            training_data (list): Training samples
        """
        if not training_data:
            return
        
        try:
            # Extract features and labels
            descriptions = [sample.get('description', '') for sample in training_data]
            apps = [' '.join(sample.get('detected_apps', [])) for sample in training_data]
            
            # Create combined features
            texts = [f"{desc} {app}" for desc, app in zip(descriptions, apps)]
            
            # Create labels (simplified for demo - using detected app as label)
            # In a real implementation, you might want to use more sophisticated labeling
            labels = []
            for sample in training_data:
                apps = sample.get('detected_apps', [])
                if apps:
                    labels.append(apps[0])
                else:
                    labels.append("Unknown")
            
            # Make sure we have enough unique labels
            unique_labels = set(labels)
            if len(unique_labels) < 2:
                logger.warning("Not enough unique activity labels for classification")
                return
            
            # Vectorize text
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            X = vectorizer.fit_transform(texts)
            
            # Train classifier
            X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)
            
            classifier = RandomForestClassifier(n_estimators=10)
            classifier.fit(X_train, y_train)
            
            # Evaluate
            accuracy = classifier.score(X_test, y_test)
            logger.info(f"Activity classifier trained with accuracy: {accuracy:.2f}")
            
            # Save model components
            self.activity_classifier = {
                'vectorizer': vectorizer,
                'classifier': classifier
            }
            
        except Exception as e:
            logger.error(f"Error training activity classifier: {e}")
    
    def _train_time_predictor(self, training_data):
        """
        Train time-based prediction model
        
        Args:
            training_data (list): Training samples
        """
        if not training_data:
            return
        
        try:
            # Extract features
            features = []
            labels = []
            
            for sample in training_data:
                apps = sample.get('detected_apps', [])
                if not apps:
                    continue
                
                # Feature: hour of day and day of week
                feature = [
                    sample.get('hour', 0),
                    sample.get('day_of_week', 0)
                ]
                
                # Label: primary app
                label = apps[0]
                
                features.append(feature)
                labels.append(label)
            
            # Make sure we have enough data
            if len(features) < self.min_samples_for_training:
                logger.warning("Not enough samples for time predictor")
                return
            
            # Convert to numpy arrays
            X = np.array(features)
            y = np.array(labels)
            
            # Train classifier
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            classifier = RandomForestClassifier(n_estimators=10)
            classifier.fit(X_train, y_train)
            
            # Evaluate
            accuracy = classifier.score(X_test, y_test)
            logger.info(f"Time predictor trained with accuracy: {accuracy:.2f}")
            
            # Save model
            self.time_predictor = classifier
            
        except Exception as e:
            logger.error(f"Error training time predictor: {e}")
    
    def _train_task_clustering(self, training_data):
        """
        Train task clustering model to identify types of tasks
        
        Args:
            training_data (list): Training samples
        """
        if not training_data:
            return
        
        try:
            # Extract text descriptions
            descriptions = [sample.get('description', '') for sample in training_data]
            
            # Vectorize
            vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
            X = vectorizer.fit_transform(descriptions)
            
            # Make sure we have enough data
            if X.shape[0] < self.min_samples_for_training:
                logger.warning("Not enough samples for task clustering")
                return
            
            # Determine number of clusters (simplified)
            n_clusters = min(5, X.shape[0] // 10)
            if n_clusters < 2:
                n_clusters = 2
            
            # Train KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            kmeans.fit(X)
            
            # Save model components
            self.task_cluster_model = {
                'vectorizer': vectorizer,
                'kmeans': kmeans
            }
            
            logger.info(f"Task clustering model trained with {n_clusters} clusters")
            
        except Exception as e:
            logger.error(f"Error training task clustering: {e}")
    
    def _generate_predictions(self):
        """Generate predictions and suggestions using trained models"""
        try:
            # Skip if no models are trained
            if not self.activity_classifier and not self.time_predictor:
                return
            
            suggestions = []
            
            # Current context
            current_description = self.shared_data.get('current_activity', '')
            current_apps = self.shared_data.get('detected_apps', [])
            current_window = self.shared_data.get('active_window', '')
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()
            
            # 1. Time-based app prediction
            if self.time_predictor:
                try:
                    # Predict app based on time
                    features = np.array([[current_hour, current_day]])
                    predicted_app = self.time_predictor.predict(features)[0]
                    
                    # If predicted app is not already open, suggest it
                    if predicted_app not in current_apps:
                        confidence = 0.7  # Simplified
                        suggestion = {
                            'type': 'ml_time_prediction',
                            'description': f"Based on your patterns, you often use '{predicted_app}' at this time",
                            'app': predicted_app,
                            'confidence': confidence,
                            'suggestion': f"Would you like to open '{predicted_app}' now?"
                        }
                        suggestions.append(suggestion)
                except Exception as e:
                    logger.error(f"Error in time-based prediction: {e}")
            
            # 2. Activity classification
            if self.activity_classifier and current_description:
                try:
                    # Vectorize current description and apps
                    vectorizer = self.activity_classifier['vectorizer']
                    classifier = self.activity_classifier['classifier']
                    
                    apps_text = ' '.join(current_apps)
                    text = f"{current_description} {apps_text}"
                    
                    X = vectorizer.transform([text])
                    
                    # Get prediction and confidence
                    predicted_activity = classifier.predict(X)[0]
                    confidence = max(classifier.predict_proba(X)[0])
                    
                    # Suggest based on activity
                    if confidence > 0.6:  # Threshold
                        suggestion = {
                            'type': 'ml_activity_analysis',
                            'description': f"I detected you're doing: {predicted_activity}",
                            'activity': predicted_activity,
                            'confidence': confidence,
                            'suggestion': f"Would you like help with {predicted_activity}?"
                        }
                        suggestions.append(suggestion)
                except Exception as e:
                    logger.error(f"Error in activity classification: {e}")
            
            # 3. Task clustering
            if self.task_cluster_model and current_description:
                try:
                    # Vectorize current description
                    vectorizer = self.task_cluster_model['vectorizer']
                    kmeans = self.task_cluster_model['kmeans']
                    
                    X = vectorizer.transform([current_description])
                    
                    # Get cluster
                    cluster = kmeans.predict(X)[0]
                    
                    # Add to shared data for tracking
                    self.shared_data['current_task_cluster'] = int(cluster)
                    
                except Exception as e:
                    logger.error(f"Error in task clustering: {e}")
            
            # Add ML-generated suggestions to shared data
            if suggestions:
                current_suggestions = self.shared_data.get('automation_suggestions', [])
                # Add only new suggestions
                for suggestion in suggestions:
                    if suggestion not in current_suggestions:
                        current_suggestions.append(suggestion)
                self.shared_data['automation_suggestions'] = current_suggestions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
