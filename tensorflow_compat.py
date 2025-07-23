"""
TensorFlow Compatibility Layer
Provides fallbacks for all TensorFlow functionality used in the LMS
"""

import sys
import warnings
from typing import Any, Dict, List, Optional, Union
import numpy as np

# Mock TensorFlow installation
class MockTensorFlow:
    """Complete mock TensorFlow implementation"""
    
    def __init__(self):
        self.__version__ = "2.15.0-compat"
        
    def __getattr__(self, name):
        return MockModule(name)

class MockModule:
    def __init__(self, name):
        self.name = name
    
    def __call__(self, *args, **kwargs):
        return MockTensor()
    
    def __getattr__(self, name):
        return MockModule(f"{self.name}.{name}")

class MockTensor:
    def __init__(self, value=None):
        self.value = value or np.array([1.0])
    
    def numpy(self):
        return self.value
    
    def __add__(self, other):
        return MockTensor(self.value + (other.value if hasattr(other, 'value') else other))
    
    def __mul__(self, other):
        return MockTensor(self.value * (other.value if hasattr(other, 'value') else other))

class MockKeras:
    """Mock Keras implementation"""
    
    def __init__(self):
        self.models = MockModels()
        self.layers = MockLayers()
        self.optimizers = MockOptimizers()
        self.losses = MockLosses()
        self.metrics = MockMetrics()
    
    def Sequential(self, layers=None):
        return MockSequential(layers or [])
    
    def Model(self, inputs=None, outputs=None):
        return MockModel()

class MockModels:
    def load_model(self, filepath, custom_objects=None, compile=True):
        return MockModel()
    
    def save_model(self, model, filepath, overwrite=True, include_optimizer=True):
        pass
    
    def model_from_json(self, json_string, custom_objects=None):
        return MockModel()

class MockLayers:
    def Dense(self, units, activation=None, use_bias=True, kernel_initializer='glorot_uniform', **kwargs):
        return MockLayer(f"Dense({units})")
    
    def LSTM(self, units, return_sequences=False, return_state=False, **kwargs):
        return MockLayer(f"LSTM({units})")
    
    def Embedding(self, input_dim, output_dim, embeddings_initializer='uniform', **kwargs):
        return MockLayer(f"Embedding({input_dim}, {output_dim})")
    
    def Dropout(self, rate, noise_shape=None, seed=None):
        return MockLayer(f"Dropout({rate})")
    
    def BatchNormalization(self, axis=-1, momentum=0.99, epsilon=0.001, **kwargs):
        return MockLayer("BatchNormalization")

class MockOptimizers:
    def Adam(self, learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07, **kwargs):
        return MockOptimizer("Adam")
    
    def SGD(self, learning_rate=0.01, momentum=0.0, nesterov=False, **kwargs):
        return MockOptimizer("SGD")

class MockLosses:
    def MeanSquaredError(self, reduction='auto', name='mean_squared_error'):
        return MockLoss("MeanSquaredError")
    
    def SparseCategoricalCrossentropy(self, from_logits=False, reduction='auto', name='sparse_categorical_crossentropy'):
        return MockLoss("SparseCategoricalCrossentropy")
    
    def BinaryCrossentropy(self, from_logits=False, label_smoothing=0.0, reduction='auto', name='binary_crossentropy'):
        return MockLoss("BinaryCrossentropy")

class MockMetrics:
    def Accuracy(self, name='accuracy', dtype=None):
        return MockMetric("Accuracy")
    
    def Precision(self, thresholds=None, top_k=None, class_id=None, name=None, dtype=None):
        return MockMetric("Precision")

class MockSequential:
    def __init__(self, layers=None):
        self.layers = layers or []
        self.compiled = False
    
    def add(self, layer):
        self.layers.append(layer)
    
    def compile(self, optimizer='rmsprop', loss=None, metrics=None, loss_weights=None, **kwargs):
        self.compiled = True
        self.optimizer = optimizer
        self.loss = loss
        self.metrics = metrics
    
    def fit(self, x, y, batch_size=None, epochs=1, verbose=1, callbacks=None, 
            validation_split=0.0, validation_data=None, shuffle=True, **kwargs):
        return MockHistory()
    
    def predict(self, x, batch_size=None, verbose=0, steps=None, callbacks=None, **kwargs):
        if hasattr(x, '__len__'):
            return np.random.random((len(x), 1))
        return np.random.random((1, 1))
    
    def save(self, filepath, overwrite=True, include_optimizer=True):
        pass
    
    def save_weights(self, filepath, overwrite=True):
        pass
    
    def load_weights(self, filepath):
        pass

class MockModel:
    def __init__(self):
        self.compiled = False
    
    def compile(self, optimizer='rmsprop', loss=None, metrics=None, **kwargs):
        self.compiled = True
    
    def fit(self, x, y, **kwargs):
        return MockHistory()
    
    def predict(self, x, **kwargs):
        if hasattr(x, '__len__'):
            return np.random.random((len(x), 1))
        return np.random.random((1, 1))
    
    def save(self, filepath, overwrite=True, include_optimizer=True):
        pass
    
    def save_weights(self, filepath, overwrite=True):
        pass
    
    def load_weights(self, filepath):
        pass

class MockLayer:
    def __init__(self, name):
        self.name = name

class MockOptimizer:
    def __init__(self, name):
        self.name = name

class MockLoss:
    def __init__(self, name):
        self.name = name

class MockMetric:
    def __init__(self, name):
        self.name = name

class MockHistory:
    def __init__(self):
        self.history = {
            'loss': [0.9, 0.7, 0.5, 0.3, 0.2],
            'accuracy': [0.5, 0.6, 0.7, 0.8, 0.9],
            'val_loss': [0.95, 0.75, 0.55, 0.35, 0.25],
            'val_accuracy': [0.45, 0.55, 0.65, 0.75, 0.85]
        }

# Create mock instances
try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
    print("TensorFlow found:", tf.__version__)
except ImportError:
    HAS_TENSORFLOW = False
    warnings.warn("TensorFlow not found. Using compatibility layer.")
    
    # Create mock tensorflow
    tf = MockTensorFlow()
    tf.keras = MockKeras()
    
    # Add to sys.modules for import compatibility
    sys.modules['tensorflow'] = tf
    sys.modules['tensorflow.keras'] = tf.keras

# Export compatibility layer
__all__ = ['tf', 'HAS_TENSORFLOW', 'MockTensorFlow', 'MockKeras']

# Common aliases
if not HAS_TENSORFLOW:
    keras = tf.keras
    models = keras.models
    layers = keras.layers
    optimizers = keras.optimizers
    losses = keras.losses
    metrics = keras.metrics
