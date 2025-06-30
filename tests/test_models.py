import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.models import ModelManager
from app.exceptions import ModelError


class TestModelManager:
    def test_init(self):
        """Test ModelManager initialization."""
        manager = ModelManager()
        assert manager.model is None
        assert manager.model_name == "distilbert-base-uncased-finetuned-sst-2-english"
        assert manager.cache_dir == "./model_cache"
        assert manager.lock is not None

    @patch('app.models.pipeline')
    def test_load_model(self, mock_pipeline):
        """Test private _load_model method."""
        mock_model = Mock()
        mock_pipeline.return_value = mock_model
        
        manager = ModelManager()
        manager._load_model()
        
        mock_pipeline.assert_called_once_with(
            "sentiment-analysis",
            model=manager.model_name
        )
        assert manager.model == mock_model

    @pytest.mark.asyncio
    @patch('app.models.pipeline')
    async def test_get_model_lazy_loading(self, mock_pipeline):
        """Test that get_model loads model only once."""
        mock_model = Mock()
        mock_pipeline.return_value = mock_model
        
        manager = ModelManager()
        
        # First call should load the model
        result1 = await manager.get_model()
        assert result1 == mock_model
        assert manager.model == mock_model
        mock_pipeline.assert_called_once()
        
        # Second call should return cached model without reloading
        result2 = await manager.get_model()
        assert result2 == mock_model
        assert result2 is result1  # Same object
        mock_pipeline.assert_called_once()  # Still only called once

    @pytest.mark.asyncio
    @patch('app.models.pipeline')
    async def test_get_model_concurrent_calls(self, mock_pipeline):
        """Test that concurrent calls to get_model only load once."""
        mock_model = Mock()
        mock_pipeline.return_value = mock_model
        
        manager = ModelManager()
        
        # Make multiple concurrent calls
        tasks = [manager.get_model() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should return the same model object
        for result in results:
            assert result == mock_model
            assert result is results[0]  # All are the same object
        
        # Pipeline should only be called once despite concurrent requests
        mock_pipeline.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.models.pipeline')
    async def test_get_model_handles_exceptions(self, mock_pipeline):
        """Test that get_model handles loading exceptions."""
        mock_pipeline.side_effect = Exception("Model loading failed")
        
        manager = ModelManager()
        
        # Should raise the original exception
        with pytest.raises(Exception, match="Model loading failed"):
            await manager.get_model()
        
        # Model should still be None after failed load
        assert manager.model is None