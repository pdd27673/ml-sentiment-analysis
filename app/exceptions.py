class MLServiceError(Exception):
    """Base exception for ML service errors."""
    pass


class ValidationError(MLServiceError):
    """Raised when input validation fails."""
    pass


class ModelError(MLServiceError):
    """Raised when model loading or prediction fails."""
    pass