import pytest
from pydantic import ValidationError
from app.schemas import SentimentRequest, SentimentResponse


class TestSentimentRequest:
    def test_valid_request(self):
        """Test valid sentiment request."""
        request = SentimentRequest(text="This is a valid text")
        assert request.text == "This is a valid text"

    def test_empty_text_fails(self):
        """Test that empty text raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SentimentRequest(text="")
        assert "at least 1 character" in str(exc_info.value)

    def test_too_long_text_fails(self):
        """Test that text over 1000 characters raises validation error."""
        long_text = "a" * 1001
        with pytest.raises(ValidationError) as exc_info:
            SentimentRequest(text=long_text)
        assert "at most 1000 characters" in str(exc_info.value)

    def test_max_length_text_passes(self):
        """Test that text exactly 1000 characters passes."""
        max_text = "a" * 1000
        request = SentimentRequest(text=max_text)
        assert len(request.text) == 1000

    def test_single_character_passes(self):
        """Test that single character passes."""
        request = SentimentRequest(text="a")
        assert request.text == "a"


class TestSentimentResponse:
    def test_valid_response(self):
        """Test valid sentiment response."""
        response = SentimentResponse(
            label="POSITIVE",
            score=0.95,
            text="This is positive",
            request_id="test-123"
        )
        assert response.label == "POSITIVE"
        assert response.score == 0.95
        assert response.text == "This is positive"
        assert response.request_id == "test-123"

    def test_response_without_request_id(self):
        """Test that request_id is optional."""
        response = SentimentResponse(
            label="NEGATIVE",
            score=0.85,
            text="This is negative"
        )
        assert response.label == "NEGATIVE"
        assert response.score == 0.85
        assert response.text == "This is negative"
        assert response.request_id is None