"""Model management utilities for saving and loading ML models."""
import os
import joblib
import json
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    """Handles saving, loading, and versioning of ML models."""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
    
    def save_model(self, model: Any, model_name: str, metadata: Optional[Dict] = None) -> str:
        """Save a trained model with metadata."""
        model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
        metadata_path = os.path.join(self.models_dir, f"{model_name}_metadata.json")
        
        # Save model
        joblib.dump(model, model_path)
        
        # Save metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'model_name': model_name,
            'model_type': type(model).__name__
        })
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved: {model_path}")
        return model_path
    
    def load_model(self, model_name: str) -> Any:
        """Load a saved model."""
        model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        model = joblib.load(model_path)
        logger.info(f"Model loaded: {model_path}")
        return model
    
    def get_model_metadata(self, model_name: str) -> Dict:
        """Get model metadata."""
        metadata_path = os.path.join(self.models_dir, f"{model_name}_metadata.json")
        
        if not os.path.exists(metadata_path):
            return {}
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return metadata
    
    def list_models(self) -> list:
        """List all saved models."""
        models = []
        for file in os.listdir(self.models_dir):
            if file.endswith('.pkl'):
                model_name = file[:-4]  # Remove .pkl extension
                models.append(model_name)
        return models
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a saved model."""
        model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
        metadata_path = os.path.join(self.models_dir, f"{model_name}_metadata.json")
        
        success = False
        if os.path.exists(model_path):
            os.remove(model_path)
            success = True
        
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        return success
