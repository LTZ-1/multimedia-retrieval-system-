"""
Database models for Multimedia Retrieval System
Supports both metadata-based and content-based retrieval
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Image(db.Model):
    """
    Image metadata table
    Stores image information and links to features
    """
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    file_path = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    keywords = db.Column(db.Text, default='')
    file_size = db.Column(db.Integer)  # bytes
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    features = db.relationship('ImageFeature', uselist=False, backref='image', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Image {self.image_name} in {self.category}>"
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'image_name': self.image_name,
            'file_path': self.file_path,
            'category': self.category,
            'keywords': self.keywords,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }


class ImageFeature(db.Model):
    """
    Image feature vectors table
    Stores visual features for content-based retrieval (CBIR)
    Features are normalized 512-dimensional color histograms
    """
    __tablename__ = 'image_features'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    # Store features as JSON (works with both SQLite and PostgreSQL)
    # For PostgreSQL with pgvector, this would use Vector(512) type
    features_json = db.Column(db.Text, nullable=False)  # JSON serialized features
    
    extraction_date = db.Column(db.DateTime, default=datetime.utcnow)
    extraction_method = db.Column(db.String(100), default='color_histogram_512')  # For tracking method
    
    def __repr__(self):
        return f"<ImageFeature for image_id={self.image_id}>"
    
    @property
    def features_array(self):
        """Convert JSON back to numpy array"""
        import json
        import numpy as np
        return np.array(json.loads(self.features_json), dtype=np.float32)
    
    @features_array.setter
    def features_array(self, array):
        """Store numpy array as JSON"""
        import json
        import numpy as np
        if isinstance(array, np.ndarray):
            self.features_json = json.dumps(array.tolist())
        else:
            self.features_json = json.dumps(array)


class SearchQuery(db.Model):
    """
    Log table to track search queries (for evaluation metrics)
    Useful for analyzing which method works better for different query types
    """
    __tablename__ = 'search_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.Text)  # Query keyword or image path
    search_type = db.Column(db.String(20), nullable=False, index=True)  # 'MBR' or 'CBIR'
    query_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    results_count = db.Column(db.Integer)
    execution_time = db.Column(db.Float)  # seconds
    
    def __repr__(self):
        return f"<SearchQuery {self.search_type} - {self.query_date}>"


class RelevanceJudgment(db.Model):
    """
    Table to store manual relevance judgments for evaluation
    Used to evaluate precision/recall of both methods
    """
    __tablename__ = 'relevance_judgments'
    
    id = db.Column(db.Integer, primary_key=True)
    query_image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False, index=True)
    retrieved_image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False, index=True)
    search_type = db.Column(db.String(20), nullable=False)  # 'MBR' or 'CBIR'
    is_relevant = db.Column(db.Boolean, nullable=False)  # True if relevant
    judge_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)  # Optional comments
    
    def __repr__(self):
        return f"<RelevanceJudgment query_id={self.query_image_id} retrieved_id={self.retrieved_image_id}>"
