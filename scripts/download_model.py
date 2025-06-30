#!/usr/bin/env python3
"""
Script to pre-download the sentiment analysis model and tokenizer.
This avoids downloading during application startup.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from transformers import pipeline
from app.config import settings


def download_model():
    """Download and cache the sentiment analysis model."""
    print(f"Downloading model: {settings.model_name}")
    print(f"Cache directory: {settings.model_cache_dir}")
    
    # Create cache directory if it doesn't exist
    os.makedirs(settings.model_cache_dir, exist_ok=True)
    
    try:
        # Load the pipeline, which will download and cache the model
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=settings.model_name,
            tokenizer=settings.model_name,
            cache_dir=settings.model_cache_dir
        )
        
        print("Model downloaded successfully!")
        
        # Test the model with a simple example
        test_result = sentiment_pipeline("This is a test.")
        print(f"Test result: {test_result}")
        
    except Exception as e:
        print(f"Error downloading model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    download_model()