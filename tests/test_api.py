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


class TestHealthEndpoint:
    @patch('app.main.model_manager.get_model')
    def test_health_check_model_loaded(self, mock_get_model, client):
        """Test health check when model is loaded."""
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["checks"]["model_loaded"] is True
        assert data["checks"]["service"] == "healthy"

    @patch('app.main.model_manager.get_model')
    def test_health_check_model_not_loaded(self, mock_get_model, client):
        """Test health check when model fails to load."""
        mock_get_model.side_effect = Exception("Model loading failed")
        
        response = client.get("/api/v1/health")
        
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unavailable"
        assert data["reason"] == "Model not loaded"
        assert data["checks"]["model_loaded"] is False
        assert data["checks"]["service"] == "degraded"


class TestMetricsEndpoint:
    def test_metrics_endpoint_format(self, client):
        """Test that metrics endpoint returns Prometheus format."""
        response = client.get("/api/v1/metrics")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        
        content = response.text
        assert "app_requests_total" in content
        assert "app_errors_total" in content
        assert "app_request_duration_ms" in content
        assert "app_model_loaded" in content
        
        # Check Prometheus format structure
        assert "# HELP app_requests_total" in content
        assert "# TYPE app_requests_total counter" in content

    def test_metrics_count_requests(self, client):
        """Test that metrics correctly count requests."""
        # Make the metrics request first to get baseline
        response = client.get("/api/v1/metrics")
        initial_content = response.text
        
        # Extract initial count (this is a simplified extraction)
        import re
        match = re.search(r'app_requests_total (\d+)', initial_content)
        initial_count = int(match.group(1)) if match else 0
        
        # Make additional requests
        client.get("/")
        client.get("/api/v1/health")
        
        # Check updated metrics
        response = client.get("/api/v1/metrics")
        updated_content = response.text
        
        match = re.search(r'app_requests_total (\d+)', updated_content)
        updated_count = int(match.group(1)) if match else 0
        
        # Should have increased by at least 3 (2 new requests + the metrics request)
        assert updated_count >= initial_count + 3