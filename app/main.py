from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from .config import settings
from .schemas import SentimentRequest, SentimentResponse
from .models import ModelManager
from .exceptions import MLServiceError, ModelError, ValidationError
from .middleware import log_requests, MetricsCollector, MetricsMiddleware
import uuid

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Initialize model manager
model_manager = ModelManager()

# Initialize metrics collector and add to app state
metrics_collector = MetricsCollector()
app.state.metrics_collector = metrics_collector
app.state.model_loaded = False

# Add middleware
app.middleware("http")(log_requests)
app.add_middleware(MetricsMiddleware, metrics_collector=metrics_collector)


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


@app.get("/api/v1/health")
async def health_check(response: Response):
    """Health check endpoint that verifies model status."""
    try:
        # Check if model is loaded by attempting to get it
        model = await model_manager.get_model()
        if model is not None:
            app.state.model_loaded = True
            return {
                "status": "ok",
                "checks": {
                    "model_loaded": True,
                    "service": "healthy"
                }
            }
    except Exception:
        app.state.model_loaded = False
    
    # Model is not available
    response.status_code = 503
    return {
        "status": "unavailable",
        "reason": "Model not loaded",
        "checks": {
            "model_loaded": False,
            "service": "degraded"
        }
    }


@app.get("/api/v1/metrics", response_class=PlainTextResponse)
async def metrics_endpoint(request: Request):
    """Prometheus-compatible metrics endpoint."""
    collector = request.app.state.metrics_collector
    
    # Format metrics in Prometheus exposition format
    metrics_text = f"""# HELP app_requests_total Total number of HTTP requests
# TYPE app_requests_total counter
app_requests_total {collector.requests_total}

# HELP app_errors_total Total number of HTTP errors (5xx responses)
# TYPE app_errors_total counter
app_errors_total {collector.errors_total}

# HELP app_request_duration_ms Average request duration in milliseconds
# TYPE app_request_duration_ms gauge
app_request_duration_ms {collector.get_average_latency()}

# HELP app_model_loaded Whether the ML model is currently loaded
# TYPE app_model_loaded gauge
app_model_loaded {int(request.app.state.model_loaded)}
"""
    
    return metrics_text


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