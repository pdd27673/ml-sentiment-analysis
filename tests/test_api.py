import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.exceptions import ModelError


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_model():
    """Create a mock sentiment analysis model."""
    mock = Mock()
    mock.return_value = [{"label": "POSITIVE", "score": 0.9999}]
    return mock


class TestRootEndpoint:
    def test_root_endpoint(self, client):
        """Test the root endpoint returns healthy status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ML Model Service is running"
        assert data["status"] == "healthy"


class TestAnalyzeEndpoint:
    @patch('app.main.model_manager.get_model')
    def test_analyze_positive_sentiment(self, mock_get_model, client, mock_model):
        """Test analyze endpoint with positive sentiment."""
        mock_get_model.return_value = mock_model
        
        response = client.post(
            "/api/v1/analyze",
            json={"text": "I love this product!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "POSITIVE"
        assert data["score"] == 0.9999
        assert data["text"] == "I love this product!"
        assert "request_id" in data
        assert data["request_id"] is not None

    @patch('app.main.model_manager.get_model')
    def test_analyze_negative_sentiment(self, mock_get_model, client):
        """Test analyze endpoint with negative sentiment."""
        mock_model = Mock()
        mock_model.return_value = [{"label": "NEGATIVE", "score": 0.8765}]
        mock_get_model.return_value = mock_model
        
        response = client.post(
            "/api/v1/analyze",
            json={"text": "This is terrible and I hate it"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "NEGATIVE"
        assert data["score"] == 0.8765
        assert data["text"] == "This is terrible and I hate it"

    def test_analyze_empty_text_validation(self, client):
        """Test that empty text is rejected."""
        response = client.post(
            "/api/v1/analyze",
            json={"text": ""}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_analyze_too_long_text_validation(self, client):
        """Test that text over 1000 characters is rejected."""
        long_text = "a" * 1001
        response = client.post(
            "/api/v1/analyze",
            json={"text": long_text}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_analyze_missing_text_field(self, client):
        """Test that missing text field is rejected."""
        response = client.post(
            "/api/v1/analyze",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_analyze_invalid_json(self, client):
        """Test that invalid JSON is rejected."""
        response = client.post(
            "/api/v1/analyze",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error

    @patch('app.main.model_manager.get_model')
    def test_analyze_model_error_handling(self, mock_get_model, client):
        """Test that model errors are properly handled."""
        mock_get_model.side_effect = Exception("Model failed to load")
        
        response = client.post(
            "/api/v1/analyze",
            json={"text": "Test text"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Model prediction failed" in data["detail"]
        assert data["type"] == "ModelError"
        assert data["path"] == "/api/v1/analyze"

    @patch('app.main.model_manager.get_model')
    def test_analyze_prediction_error_handling(self, mock_get_model, client):
        """Test that prediction errors are properly handled."""
        mock_model = Mock()
        mock_model.side_effect = Exception("Prediction failed")
        mock_get_model.return_value = mock_model
        
        response = client.post(
            "/api/v1/analyze",
            json={"text": "Test text"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Model prediction failed" in data["detail"]
        assert "Prediction failed" in data["detail"]