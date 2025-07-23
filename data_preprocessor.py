"""Data preprocessing utilities for ML models."""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from src.models import User, Book, BorrowRecord
import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Handles data preprocessing for ML models."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_interaction_matrix(self) -> pd.DataFrame:
        """Create user-book interaction matrix."""
        borrow_records = self.db.query(BorrowRecord).all()
        
        interactions = []
        for record in borrow_records:
            interactions.append({
                'user_id': record.user_id,
                'book_id': record.book_id,
                'rating': 1,  # Implicit feedback - borrowed = 1
                'timestamp': record.borrow_date
            })
        
        df = pd.DataFrame(interactions)
        
        if df.empty:
            return pd.DataFrame()
        
        # Create pivot table
        interaction_matrix = df.pivot_table(
            index='user_id',
            columns='book_id',
            values='rating',
            fill_value=0
        )
        
        return interaction_matrix
    
    def get_book_features(self) -> pd.DataFrame:
        """Extract book features for content-based filtering."""
        books = self.db.query(Book).all()
        
        features = []
        for book in books:
            features.append({
                'book_id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'copies': book.copies
            })
        
        return pd.DataFrame(features)
    
    def get_user_features(self) -> pd.DataFrame:
        """Extract user features."""
        users = self.db.query(User).all()
        
        features = []
        for user in users:
            features.append({
                'user_id': user.id,
                'role': user.role
            })
        
        return pd.DataFrame(features)
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Prepare all data for training."""
        interaction_matrix = self.get_interaction_matrix()
        book_features = self.get_book_features()
        user_features = self.get_user_features()
        
        return interaction_matrix, book_features, user_features
    
    def split_data(self, interaction_matrix: pd.DataFrame, 
                   test_ratio: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split interaction matrix into train/test sets."""
        if interaction_matrix.empty:
            return interaction_matrix, interaction_matrix
        
        # Randomly mask some interactions for testing
        test_matrix = interaction_matrix.copy()
        train_matrix = interaction_matrix.copy()
        
        # Mask 20% of non-zero entries for testing
        mask = np.random.random(interaction_matrix.shape) < test_ratio
        mask = mask & (interaction_matrix > 0)
        
        train_matrix = train_matrix.mask(mask, 0)
        test_matrix = test_matrix.where(mask, 0)
        
        return train_matrix, test_matrix
