from flask import Blueprint, jsonify, request
import json
import os

ml_bp = Blueprint('ml_api', __name__)

@ml_bp.route('/predict', methods=['POST'])
def predict():
    """Mock prediction endpoint for TensorFlow models"""
    try:
        data = request.get_json()
        
        # Mock prediction response
        prediction = {
            'success': True,
            'prediction': {
                'demand_forecast': 0.75,
                'recommendation_score': 0.85,
                'fine_probability': 0.15
            },
            'message': 'Mock prediction completed (TensorFlow not installed)'
        }
        
        return jsonify(prediction)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ml_bp.route('/status', methods=['GET'])
def ml_status():
    """Check ML service status"""
    return jsonify({
        'status': 'mock_mode',
        'message': 'TensorFlow not installed - using mock responses',
        'available_models': ['demand_forecast', 'book_recommendation', 'fine_prediction']
    })
