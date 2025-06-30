import asyncio
from transformers import pipeline
from .config import settings


class ModelManager:
    """Manages the sentiment analysis model with lazy loading and thread safety."""
    
    def __init__(self):
        self.model = None
        self.model_name = settings.model_name
        self.cache_dir = settings.model_cache_dir
        self.lock = asyncio.Lock()
    
    def _load_model(self):
        """Private method to load the sentiment analysis model."""
        self.model = pipeline(
            "sentiment-analysis",
            model=self.model_name,
            cache_dir=self.cache_dir
        )
    
    async def get_model(self):
        """Public method to get the model with lazy loading and thread safety."""
        if self.model is not None:
            return self.model
        
        async with self.lock:
            # Double-check pattern to prevent race condition
            if self.model is None:
                self._load_model()
            return self.model