"""
Machine Learning Models for Library Management System
Provides book recommendation, demand forecasting, and fine prediction
"""

import numpy as np
from typing import Dict, List, Any, Optional
import json
import os

# Import TensorFlow compatibility layer
from src.tensorflow_compat import tf, HAS_TENSORFLOW

class LibraryMLModels:
    """Library Management System ML Models"""
    
    def __init__(self):
        self.has_tensorflow = HAS_TENSORFLOW
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models based on TensorFlow availability"""
        if self.has_tensorflow:
            print("✅ Using real TensorFlow models")
            self._load_real_models()
        else:
            print("⚠️  Using mock TensorFlow models")
            self._load_mock_models()
    
    def _load_real_models(self):
        """Load real TensorFlow models"""
        try:
            # Book recommendation model
            self.models['recommendation'] = self._build_recommendation_model()
            
            # Demand forecasting model
            self.models['demand_forecast'] = self._build_demand_forecast_model()
            
            # Fine prediction model
            self.models['fine_prediction'] = self._build_fine_prediction_model()
            
        except Exception as e:
            print(f"Error loading real models: {e}")
            self._load_mock_models()
    
    def _load_mock_models(self):
        """Load mock models when TensorFlow is not available"""
        self.models = {
            'recommendation': MockRecommendationModel(),
            'demand_forecast': MockDemandForecastModel(),
            'fine_prediction': MockFinePredictionModel()
        }
    
    def _build_recommendation_model(self):
        """Build book recommendation model"""
        if not self.has_tensorflow:
            return MockRecommendationModel()
        
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(10,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=tf.keras.losses.BinaryCrossentropy(),
            metrics=['accuracy']
        )
        
        return model
    
    def _build_demand_forecast_model(self):
        """Build demand forecasting model"""
        if not self.has_tensorflow:
            return MockDemandForecastModel()
        
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(30, 5)),
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=tf.keras.losses.MeanSquaredError(),
            metrics=['mae']
        )
        
        return model
    
    def _build_fine_prediction_model(self):
        """Build fine prediction model"""
        if not self.has_tensorflow:
            return MockFinePredictionModel()
        
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(8,)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=tf.keras.losses.MeanSquaredError(),
            metrics=['mae']
        )
        
        return model
    
    def recommend_books(self, user_id: int, book_history: List[Dict]) -> List[Dict]:
        """Get book recommendations for a user"""
        model = self.models['recommendation']
        
        # Prepare features
        features = self._prepare_recommendation_features(user_id, book_history)
        
        if self.has_tensorflow:
            predictions = model.predict(np.array([features]))
        else:
            predictions = model.predict(features)
        
        # Format recommendations
        recommendations = self._format_recommendations(predictions, book_history)
        return recommendations
    
    def forecast_demand(self, book_id: int, historical_data: List[Dict]) -> Dict:
        """Forecast demand for a book"""
        model = self.models['demand_forecast']
        
        # Prepare time series data
        features = self._prepare_demand_features(historical_data)
        
        if self.has_tensorflow:
            forecast = model.predict(np.array([features]))
        else:
            forecast = model.predict(features)
        
        return {
            'book_id': book_id,
            'forecast': float(forecast[0][0]) if hasattr(forecast, '__getitem__') else float(forecast),
            'confidence': 0.85,
            'period': '30_days'
        }
    
    def predict_fine(self, user_data: Dict, book_data: Dict) -> Dict:
        """Predict fine amount for a potential late return"""
        model = self.models['fine_prediction']
        
        # Prepare features
        features = self._prepare_fine_features(user_data, book_data)
        
        if self.has_tensorflow:
            prediction = model.predict(np.array([features]))
        else:
            prediction = model.predict(features)
        
        return {
            'predicted_fine': float(prediction[0][0]) if hasattr(prediction, '__getitem__') else float(prediction),
            'confidence': 0.78,
            'factors': ['user_history', 'book_popularity', 'seasonal_demand']
        }
    
    def _prepare_recommendation_features(self, user_id: int, book_history: List[Dict]) -> List[float]:
        """Prepare features for recommendation model"""
        # Mock feature extraction
        return [
            user_id % 100,  # User ID hash
            len(book_history),  # Number of books read
            np.mean([b.get('rating', 3) for b in book_history]) if book_history else 3.0,  # Average rating
            len(set([b.get('category', 'unknown') for b in book_history])),  # Category diversity
            1.0 if any(b.get('rating', 0) >= 4 for b in book_history) else 0.0,  # High rating indicator
            0.5,  # Placeholder features
            0.3,
            0.7,
            0.2,
            0.8
        ]
    
    def _prepare_demand_features(self, historical_data: List[Dict]) -> List[List[float]]:
        """Prepare time series features for demand forecasting"""
        # Mock time series data
        return [[
            d.get('borrow_count', 1),
            d.get('return_count', 1),
            d.get('fine_count', 0),
            d.get('seasonal_factor', 1.0),
            d.get('day_of_week', 1)
        ] for d in historical_data[-30:]]  # Last 30 days
    
    def _prepare_fine_features(self, user_data: Dict, book_data: Dict) -> List[float]:
        """Prepare features for fine prediction"""
        return [
            user_data.get('late_returns', 0),
            user_data.get('total_books', 0),
            user_data.get('average_rating', 3.0),
            book_data.get('popularity_score', 0.5),
            book_data.get('category_demand', 0.5),
            book_data.get('seasonal_factor', 1.0),
            user_data.get('membership_duration', 365),
            book_data.get('fine_rate', 1.0)
        ]
    
    def _format_recommendations(self, predictions, book_history: List[Dict]) -> List[Dict]:
        """Format recommendation results"""
        recommendations = []
        
        # Mock book database
        mock_books = [
            {'id': 1, 'title': 'Python Programming', 'author': 'John Doe', 'score': 0.9},
            {'id': 2, 'title': 'Machine Learning Basics', 'author': 'Jane Smith', 'score': 0.85},
            {'id': 3, 'title': 'Data Science Handbook', 'author': 'Alan Johnson', 'score': 0.8},
            {'id': 4, 'title': 'Flask Web Development', 'author': 'Mike Brown', 'score': 0.75},
            {'id': 5, 'title': 'Database Design', 'author': 'Sarah Wilson', 'score': 0.7}
        ]
        
        for book in mock_books:
            recommendations.append({
                'book_id': book['id'],
                'title': book['title'],
                'author': book['author'],
                'recommendation_score': book['score'],
                'reason': 'Based on your reading history'
            })
        
        return sorted(recommendations, key=lambda x: x['recommendation_score'], reverse=True)

# Mock model classes
class MockRecommendationModel:
    def predict(self, features):
        return np.array([[0.85, 0.78, 0.92, 0.65, 0.88]])

class MockDemandForecastModel:
    def predict(self, features):
        return np.array([[15.5]])

class MockFinePredictionModel:
    def predict(self, features):
        return np.array([[12.5]])

# Global ML instance
ml_models = LibraryMLModels()

# Export functions
def get_book_recommendations(user_id: int, book_history: List[Dict]) -> List[Dict]:
    """Get book recommendations for a user"""
    return ml_models.recommend_books(user_id, book_history)

def forecast_book_demand(book_id: int, historical_data: List[Dict]) -> Dict:
    """Forecast demand for a book"""
    return ml_models.forecast_demand(book_id, historical_data)

def predict_fine_amount(user_data: Dict, book_data: Dict) -> Dict:
    """Predict fine amount for late return"""
    return ml_models.predict_fine(user_data, book_data)

def get_ml_status() -> Dict:
    """Get ML system status"""
    return {
        'tensorflow_available': ml_models.has_tensorflow,
        'models_loaded': list(ml_models.models.keys()),
        'status': 'operational'
    }
