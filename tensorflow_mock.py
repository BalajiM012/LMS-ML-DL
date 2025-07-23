"""
TensorFlow Mock Module
This module provides mock implementations of TensorFlow functionality
when TensorFlow is not available or cannot be installed.
"""

import warnings
import numpy as np

class MockTensorFlow:
    """Mock TensorFlow class for compatibility"""
    
    def __init__(self):
        self.__version__ = "2.15.0-mock"
        self.keras = MockKeras()
        self.compat = MockCompat()
        
    def __getattr__(self, name):
        return MockTensor(name)

class MockKeras:
    """Mock Keras class"""
    
    def __init__(self):
        self.models = MockModels()
        self.layers = MockLayers()
        self.optimizers = MockOptimizers()
        self.losses = MockLosses()
        
    def Sequential(self):
        return MockSequential()

class MockModels:
    def load_model(self, filepath):
        return MockModel()

class MockLayers:
    def Dense(self, units, activation=None):
        return MockLayer()
    
    def LSTM(self, units, return_sequences=False):
        return MockLayer()
    
    def Embedding(self, input_dim, output_dim):
        return MockLayer()

class MockOptimizers:
    def Adam(self, learning_rate=0.001):
        return MockOptimizer()

class MockLosses:
    def MeanSquaredError(self):
        return MockLoss()
    
    def SparseCategoricalCrossentropy(self):
        return MockLoss()

class MockSequential:
    def add(self, layer):
        pass
    
    def compile(self, optimizer, loss, metrics=None):
        pass
    
    def fit(self, x, y, epochs=1, batch_size=32, validation_data=None):
        return MockHistory()
    
    def predict(self, x):
        return np.random.random((len(x), 1))

class MockModel:
    def predict(self, x):
        if hasattr(x, '__len__'):
            return np.random.random((len(x), 1))
        return np.random.random((1, 1))

class MockLayer:
    pass

class MockOptimizer:
    pass

class MockLoss:
    pass

class MockHistory:
    def __init__(self):
        self.history = {'loss': [0.5, 0.4, 0.3]}

class MockTensor:
    def __init__(self, name):
        self.name = name
    
    def __call__(self, *args, **kwargs):
        return np.array([1.0])

class MockCompat:
    class v1:
        @staticmethod
        def disable_v2_behavior():
            pass

# Create mock tensorflow instance
try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    warnings.warn("TensorFlow not found. Using mock implementation.")
    tf = MockTensorFlow()

# Export mock tensorflow
__all__ = ['tf', 'HAS_TENSORFLOW']
