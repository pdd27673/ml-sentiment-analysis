from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .config import settings
from .schemas import SentimentRequest, SentimentResponse
from .models import ModelManager
from .exceptions import MLServiceError, ModelError, ValidationError
import uuid

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Initialize model manager
model_manager = ModelManager()


@app.exception_handler(MLServiceError)
async def ml_service_exception_handler(request: Request, exc: MLServiceError):
    """Global exception handler for ML service errors."""
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "type": exc.__class__.__name__,
            "path": request.url.path
        }
    )


@app.get("/")
async def root():
    return {"message": "ML Model Service is running", "status": "healthy"}


@app.post("/api/v1/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest) -> SentimentResponse:
    """Analyze sentiment of input text."""
    request_id = str(uuid.uuid4())
    
    try:
        # Get the model
        model = await model_manager.get_model()
        
        # Perform sentiment analysis
        result = model(request.text)[0]
        
        return SentimentResponse(
            label=result["label"],
            score=result["score"],
            text=request.text,
            request_id=request_id
        )
    
    except Exception as e:
        # Wrap any unexpected errors as ModelError
        if isinstance(e, MLServiceError):
            raise  # Re-raise our own exceptions
        else:
            raise ModelError(f"Model prediction failed: {str(e)}")