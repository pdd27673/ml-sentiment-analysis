import pytest
from app.exceptions import MLServiceError, ValidationError, ModelError


class TestCustomExceptions:
    def test_ml_service_error_base_class(self):
        """Test that MLServiceError is the base exception."""
        error = MLServiceError("Base error")
        assert str(error) == "Base error"
        assert isinstance(error, Exception)

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from MLServiceError."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, MLServiceError)
        assert isinstance(error, Exception)

    def test_model_error_inheritance(self):
        """Test that ModelError inherits from MLServiceError."""
        error = ModelError("Model failed")
        assert str(error) == "Model failed"
        assert isinstance(error, MLServiceError)
        assert isinstance(error, Exception)

    def test_exception_hierarchy_catching(self):
        """Test that we can catch all custom exceptions with base class."""
        # This simulates how our exception handler works
        def raise_validation_error():
            raise ValidationError("Invalid input")
        
        def raise_model_error():
            raise ModelError("Model loading failed")
        
        # Both should be caught by MLServiceError handler
        with pytest.raises(MLServiceError):
            raise_validation_error()
        
        with pytest.raises(MLServiceError):
            raise_model_error()

    def test_specific_exception_catching(self):
        """Test that we can catch specific exception types."""
        with pytest.raises(ValidationError):
            raise ValidationError("Specific validation error")
        
        with pytest.raises(ModelError):
            raise ModelError("Specific model error")