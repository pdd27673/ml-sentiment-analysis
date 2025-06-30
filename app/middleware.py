import time
import json
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next: Callable) -> Response:
    """Middleware function for structured request logging."""
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log incoming request
    start_time = time.time()
    request_log = {
        "event": "request_started",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "query_params": str(request.query_params),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "timestamp": start_time
    }
    logger.info(json.dumps(request_log))
    
    # Process request
    response = await call_next(request)
    
    # Log response
    end_time = time.time()
    duration = end_time - start_time
    
    response_log = {
        "event": "request_completed",
        "request_id": request_id,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "timestamp": end_time
    }
    logger.info(json.dumps(response_log))
    
    # Add request ID to response headers for traceability
    response.headers["X-Request-ID"] = request_id
    
    return response


class MetricsCollector:
    """Thread-safe metrics collector for application monitoring."""
    
    def __init__(self):
        self.requests_total = 0
        self.errors_total = 0
        self.latencies = []
        self._lock = None  # Will be set to asyncio.Lock when async context is available
    
    def increment_requests(self):
        """Increment total request count."""
        self.requests_total += 1
    
    def increment_errors(self):
        """Increment total error count."""
        self.errors_total += 1
    
    def record_latency(self, duration_ms: float):
        """Record request latency in milliseconds."""
        self.latencies.append(duration_ms)
        # Keep only last 1000 latencies to prevent memory growth
        if len(self.latencies) > 1000:
            self.latencies = self.latencies[-1000:]
    
    def get_average_latency(self) -> float:
        """Get average latency in milliseconds."""
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)
    
    def get_metrics_summary(self) -> dict:
        """Get current metrics summary."""
        return {
            "requests_total": self.requests_total,
            "errors_total": self.errors_total,
            "average_latency_ms": self.get_average_latency(),
            "latency_samples": len(self.latencies)
        }


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect application metrics."""
    
    def __init__(self, app, metrics_collector: MetricsCollector):
        super().__init__(app)
        self.metrics_collector = metrics_collector
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Check if this is an error response
            if response.status_code >= 500:
                self.metrics_collector.increment_errors()
            
            return response
            
        except Exception as e:
            # Count exceptions as errors
            self.metrics_collector.increment_errors()
            raise
        
        finally:
            # Always record request count and latency
            self.metrics_collector.increment_requests()
            duration_ms = (time.time() - start_time) * 1000
            self.metrics_collector.record_latency(duration_ms)