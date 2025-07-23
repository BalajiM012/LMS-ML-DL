"""Matrix factorization models for collaborative filtering."""
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class SVDRecommender:
    """Singular Value Decomposition based recommendation system."""
    
    def __init__(self, n_components: int = 50, random_state: int = 42):
        self.n_components = n_components
        self.random_state = random_state
        self.svd = TruncatedSVD(n_components=n_components, random_state=random_state)
        self.user_factors = None
        self.item_factors = None
        self.user_id_map = {}
        self.item_id_map = {}
        self.reverse_user_map = {}
        self.reverse_item_map = {}
    
    def fit(self, interaction_matrix: pd.DataFrame):
        """Train the SVD model."""
        logger.info("Training SVD model...")
        
        # Create mappings
        self.user_id_map = {user_id: idx for idx, user_id in enumerate(interaction_matrix.index)}
        self.item_id_map = {item_id: idx for idx, item_id in enumerate(interaction_matrix.columns)}
        self.reverse_user_map = {idx: user_id for user_id, idx in self.user_id_map.items()}
        self.reverse_item_map = {idx: item_id for item_id, idx in self.item_id_map.items()}
        
        # Convert to numpy array
        interaction_array = interaction_matrix.values
        
        # Fit SVD
        self.user_factors = self.svd.fit_transform(interaction_array)
        self.item_factors = self.svd.components_.T
        
        logger.info(f"SVD model trained with {self.n_components} components")
    
    def predict(self, user_id: int, item_id: int) -> float:
        """Predict rating for a user-item pair."""
        if user_id not in self.user_id_map or item_id not in self.item_id_map:
            return 0.0
        
        user_idx = self.user_id_map[user_id]
        item_idx = self.item_id_map[item_id]
        
        prediction = np.dot(self.user_factors[user_idx], self.item_factors[item_idx])
        return max(0, prediction)  # Ensure non-negative
    
    def recommend(self, user_id: int, n_recommendations: int = 10) -> list:
        """Get top N recommendations for a user."""
        if user_id not in self.user_id_map:
            return []
        
        user_idx = self.user_id_map[user_id]
        user_vector = self.user_factors[user_idx]
        
        # Calculate scores for all items
        scores = np.dot(user_vector, self.item_factors.T)
        
        # Get top items
        top_items = np.argsort(scores)[::-1][:n_recommendations]
        
        recommendations = []
        for item_idx in top_items:
            item_id = self.reverse_item_map[item_idx]
            score = float(scores[item_idx])
            recommendations.append({
                'item_id': item_id,
                'score': score
            })
        
        return recommendations
    
    def get_similar_items(self, item_id: int, n_similar: int = 10) -> list:
        """Find similar items based on item factors."""
        if item_id not in self.item_id_map:
            return []
        
        item_idx = self.item_id_map[item_id]
        item_vector = self.item_factors[item_idx].reshape(1, -1)
        
        # Calculate similarities
        similarities = cosine_similarity(item_vector, self.item_factors)[0]
        
        # Get top similar items
        similar_items = np.argsort(similarities)[::-1][1:n_similar+1]  # Exclude self
        
        recommendations = []
        for similar_idx in similar_items:
            similar_item_id = self.reverse_item_map[similar_idx]
            similarity = float(similarities[similar_idx])
            recommendations.append({
                'item_id': similar_item_id,
                'similarity': similarity
            })
        
        return recommendations

class NMFRecommender:
    """Non-negative Matrix Factorization for collaborative filtering."""
    
    def __init__(self, n_components: int = 50, max_iter: int = 100, random_state: int = 42):
        self.n_components = n_components
        self.max_iter = max_iter
        self.random_state = random_state
        self.user_factors = None
        self.item_factors = None
        self.user_id_map = {}
        self.item_id_map = {}
        self.reverse_user_map = {}
        self.reverse_item_map = {}
    
    def fit(self, interaction_matrix: pd.DataFrame):
        """Train the NMF model."""
        logger.info("Training NMF model...")
        
        # Create mappings
        self.user_id_map = {user_id: idx for idx, user_id in enumerate(interaction_matrix.index)}
        self.item_id_map = {item_id: idx for idx, item_id in enumerate(interaction_matrix.columns)}
        self.reverse_user_map = {idx: user_id for user_id, idx in self.user_id_map.items()}
        self.reverse_item_map = {idx: item_id for item_id, idx in self.item_id_map.items()}
        
        # Convert to numpy array
        interaction_array = interaction_matrix.values
        
        # Initialize factors
        n_users, n_items = interaction_array.shape
        self.user_factors = np.random.rand(n_users, self.n_components)
        self.item_factors = np.random.rand(n_items, self.n_components)
        
        # NMF training (simple multiplicative update)
        for iteration in range(self.max_iter):
            # Update item factors
            numerator = self.user_factors.T @ interaction_array
            denominator = self.user_factors.T @ self.user_factors @ self.item_factors.T
            self.item_factors = self.item_factors * (numerator / (denominator + 1e-10)).T
            
            # Update user factors
            numerator = interaction_array @ self.item_factors
            denominator = self.user_factors @ self.item_factors.T @ self.item_factors
            self.user_factors = self.user_factors * (numerator / (denominator + 1e-10))
        
        logger.info(f"NMF model trained with {self.n_components} components")
    
    def predict(self, user_id: int, item_id: int) -> float:
        """Predict rating for a user-item pair."""
        if user_id not in self.user_id_map or item_id not in self.item_id_map:
            return 0.0
        
        user_idx = self.user_id_map[user_id]
        item_idx = self.item_id_map[item_id]
        
        prediction = np.dot(self.user_factors[user_idx], self.item_factors[item_idx])
        return max(0, prediction)
    
    def recommend(self, user_id: int, n_recommendations: int = 10) -> list:
        """Get top N recommendations for a user."""
        if user_id not in self.user_id_map:
            return []
        
        user_idx = self.user_id_map[user_id]
        user_vector = self.user_factors[user_idx]
        
        # Calculate scores for all items
        scores = np.dot(user_vector, self.item_factors.T)
        
        # Get top items
        top_items = np.argsort(scores)[::-1][:n_recommendations]
        
        recommendations = []
        for item_idx in top_items:
            item_id = self.reverse_item_map[item_idx]
            score = float(scores[item_idx])
            recommendations.append({
                'item_id': item_id,
                'score': score
            })
        
        return recommendations
