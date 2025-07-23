"""Neural Collaborative Filtering models using TensorFlow."""
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class NeuralCollaborativeFiltering:
    """Neural Collaborative Filtering model."""
    
    def __init__(self, n_users: int, n_items: int, embedding_dim: int = 50, 
                 hidden_layers: list = [64, 32, 16], dropout_rate: float = 0.2):
        self.n_users = n_users
        self.n_items = n_items
        self.embedding_dim = embedding_dim
        self.hidden_layers = hidden_layers
        self.dropout_rate = dropout_rate
        self.model = None
        self.user_id_map = {}
        self.item_id_map = {}
        self.reverse_user_map = {}
        self.reverse_item_map = {}
    
    def build_model(self):
        """Build the NCF model architecture."""
        # Input layers
        user_input = layers.Input(shape=(1,), name='user_input')
        item_input = layers.Input(shape=(1,), name='item_input')
        
        # Embedding layers
        user_embedding = layers.Embedding(
            input_dim=self.n_users, 
            output_dim=self.embedding_dim,
            name='user_embedding'
        )(user_input)
        
        item_embedding = layers.Embedding(
            input_dim=self.n_items,
            output_dim=self.embedding_dim,
            name='item_embedding'
        )(item_input)
        
        # Flatten embeddings
        user_vec = layers.Flatten()(user_embedding)
        item_vec = layers.Flatten()(item_embedding)
        
        # Concatenate embeddings
        concat = layers.Concatenate()([user_vec, item_vec])
        
        # Dense layers
        x = concat
        for units in self.hidden_layers:
            x = layers.Dense(units, activation='relu')(x)
            x = layers.Dropout(self.dropout_rate)(x)
        
        # Output layer
        output = layers.Dense(1, activation='sigmoid', name='prediction')(x)
        
        # Build model
        self.model = models.Model(inputs=[user_input, item_input], outputs=output)
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        logger.info("NCF model built successfully")
        return self.model
    
    def prepare_training_data(self, interaction_matrix: pd.DataFrame):
        """Prepare data for training."""
        # Create mappings
        self.user_id_map = {user_id: idx for idx, user_id in enumerate(interaction_matrix.index)}
        self.item_id_map = {item_id: idx for idx, item_id in enumerate(interaction_matrix.columns)}
        self.reverse_user_map = {idx: user_id for user_id, idx in self.user_id_map.items()}
        self.reverse_item_map = {idx: item_id for item_id, idx in self.item_id_map.items()}
        
        # Prepare positive samples
        positive_samples = []
        for user_id in interaction_matrix.index:
            for item_id in interaction_matrix.columns:
                if interaction_matrix.loc[user_id, item_id] > 0:
                    positive_samples.append([
                        self.user_id_map[user_id],
                        self.item_id_map[item_id],
                        1
                    ])
        
        # Prepare negative samples (equal number)
        all_items = list(interaction_matrix.columns)
        negative_samples = []
        
        for user_id in interaction_matrix.index:
            user_items = interaction_matrix.loc[user_id]
            positive_items = user_items[user_items > 0].index.tolist()
            negative_items = [item for item in all_items if item not in positive_items]
            
            # Sample negative items
            n_positive = len(positive_items)
            sampled_negative = np.random.choice(
                negative_items, 
                size=min(n_positive, len(negative_items)), 
                replace=False
            )
            
            for item_id in sampled_negative:
                negative_samples.append([
                    self.user_id_map[user_id],
                    self.item_id_map[item_id],
                    0
                ])
        
        # Combine samples
        all_samples = positive_samples + negative_samples
        np.random.shuffle(all_samples)
        
        samples_array = np.array(all_samples)
        
        return {
            'user_input': samples_array[:, 0],
            'item_input': samples_array[:, 1],
            'labels': samples_array[:, 2]
        }
    
    def train(self, interaction_matrix: pd.DataFrame, epochs: int = 10, 
              batch_size: int = 256, validation_split: float = 0.2):
        """Train the NCF model."""
        if self.model is None:
            self.build_model()
        
        # Prepare training data
        data = self.prepare_training_data(interaction_matrix)
        
        # Train model
        history = self.model.fit(
            [data['user_input'], data['item_input']],
            data['labels'],
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
        
        logger.info(f"NCF model trained for {epochs} epochs")
        return history
    
    def predict(self, user_id: int, item_id: int) -> float:
        """Predict probability for user-item pair."""
        if user_id not in self.user_id_map or item_id not in self.item_id_map:
            return 0.0
        
        user_idx = self.user_id_map[user_id]
        item_idx = self.item_id_map[item_id]
        
        prediction = self.model.predict([
            np.array([user_idx]),
            np.array([item_idx])
        ], verbose=0)[0][0]
        
        return float(prediction)
    
    def recommend(self, user_id: int, n_recommendations: int = 10) -> list:
        """Get top N recommendations for a user."""
        if user_id not in self.user_id_map:
            return []
        
        user_idx = self.user_id_map[user_id]
        
        # Get all items
        all_items = list(self.item_id_map.keys())
        
        # Predict for all items
        user_indices = [user_idx] * len(all_items)
        item_indices = [self.item_id_map[item_id] for item_id in all_items]
        
        predictions = self.model.predict([
            np.array(user_indices),
            np.array(item_indices)
        ], verbose=0).flatten()
        
        # Get top recommendations
        top_indices = np.argsort(predictions)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_indices:
            item_id = all_items[idx]
            score = float(predictions[idx])
            recommendations.append({
                'item_id': item_id,
                'score': score
            })
        
        return recommendations

class DeepAutoencoder:
    """Deep Autoencoder for collaborative filtering."""
    
    def __init__(self, n_items: int, encoding_dim: int = 50):
        self.n_items = n_items
        self.encoding_dim = encoding_dim
        self.model = None
        self.encoder = None
        
    def build_model(self):
        """Build the autoencoder model."""
        # Input layer
        input_layer = layers.Input(shape=(self.n_items,), name='input')
        
        # Encoder
        encoded = layers.Dense(128, activation='relu')(input_layer)
        encoded = layers.Dense(64, activation='relu')(encoded)
        encoded = layers.Dense(self.encoding_dim, activation='relu', name='encoding')(encoded)
        
        # Decoder
        decoded = layers.Dense(64, activation='relu')(encoded)
        decoded = layers.Dense(128, activation='relu')(decoded)
        decoded = layers.Dense(self.n_items, activation='sigmoid', name='decoding')(decoded)
        
        # Build models
        self.model = models.Model(inputs=input_layer, outputs=decoded)
        self.encoder = models.Model(inputs=input_layer, outputs=encoded)
        
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        logger.info("Deep Autoencoder model built successfully")
        return self.model
    
    def train(self, interaction_matrix: pd.DataFrame, epochs: int = 50, 
              batch_size: int = 256, validation_split: float = 0.2):
        """Train the autoencoder."""
        if self.model is None:
            self.build_model()
        
        # Prepare data
        X = interaction_matrix.values
        
        # Train model
        history = self.model.fit(
            X, X,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
        
        logger.info(f"Autoencoder trained for {epochs} epochs")
        return history
    
    def get_recommendations(self, user_vector: np.ndarray, 
                           n_recommendations: int = 10) -> list:
        """Get recommendations for a user."""
        if self.model is None:
            return []
        
        # Get encoded representation
        encoded = self.encoder.predict(user_vector.reshape(1, -1), verbose=0)
        
        # Get reconstructed vector
        reconstructed = self.model.predict(user_vector.reshape(1, -1), verbose=0)[0]
        
        # Get top recommendations
        top_indices = np.argsort(reconstructed)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_indices:
            if user_vector[idx] == 0:  # Only recommend un-interacted items
                recommendations.append({
                    'item_id': idx,
                    'score': float(reconstructed[idx])
                })
        
        return recommendations
