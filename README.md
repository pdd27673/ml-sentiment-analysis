# 🤖 ML Sentiment Analysis API

A production-ready FastAPI service for real-time sentiment analysis using DistilBERT, featuring comprehensive monitoring, containerization, and a beautiful web interface.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg)
![Tests](https://img.shields.io/badge/tests-30%20passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### 🧠 **AI-Powered Sentiment Analysis**
- **DistilBERT Model**: State-of-the-art transformer model for accurate sentiment classification
- **Real-time Processing**: Fast inference with lazy loading and thread-safe model management
- **High Accuracy**: 99%+ confidence scores on clear positive/negative sentiment

### 🚀 **Production-Ready API**
- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **Input Validation**: Pydantic schemas with comprehensive error handling
- **Request Tracing**: Unique request IDs for distributed system observability
- **CORS Support**: Configurable cross-origin resource sharing

### 📊 **Monitoring & Observability**
- **Health Checks**: `/api/v1/health` endpoint for load balancer integration
- **Prometheus Metrics**: `/api/v1/metrics` endpoint with request counts, latency, and error rates
- **Structured Logging**: JSON-formatted logs with request correlation IDs
- **Performance Tracking**: Automatic latency and throughput monitoring

### 🐳 **Containerization**
- **Multi-stage Dockerfile**: Optimized images with model pre-downloading
- **Docker Compose**: One-command deployment with volume management
- **Health Checks**: Built-in container health monitoring
- **Security**: Non-root user execution and minimal attack surface

### 🎨 **Interactive Demo UI**
- **Beautiful Interface**: Responsive web UI with gradient design
- **Real-time Results**: Instant sentiment analysis with confidence scores
- **Example Texts**: Pre-loaded examples for quick testing
- **Error Handling**: User-friendly validation and error messages

### 🧪 **Comprehensive Testing**
- **30 Test Cases**: Unit, integration, and API endpoint testing
- **Mocked Models**: Fast test execution without model loading
- **Coverage**: All major components and error scenarios
- **CI Ready**: Pytest configuration for automated testing

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- 2GB+ RAM for model loading

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ml-python
```

### 2. Development Setup
```bash
# Create virtual environment
make venv

# Install dependencies
make install

# Run the application
make run
```

### 3. Docker Deployment (Recommended)
```bash
# Build and start services
docker-compose up --build

# Or run in background
docker-compose up -d
```

### 4. Access the Application
- **Demo UI**: http://localhost:8000/static/demo.html
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Metrics**: http://localhost:8000/api/v1/metrics

## 📖 API Documentation

### Analyze Sentiment
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "text": "I love this amazing product!"
}
```

**Response:**
```json
{
  "label": "POSITIVE",
  "score": 0.9998891353607178,
  "text": "I love this amazing product!",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "ok",
  "checks": {
    "model_loaded": true,
    "service": "healthy"
  }
}
```

### Prometheus Metrics
```http
GET /api/v1/metrics
```

**Response:**
```
# HELP app_requests_total Total number of HTTP requests
# TYPE app_requests_total counter
app_requests_total 42

# HELP app_errors_total Total number of HTTP errors
# TYPE app_errors_total counter
app_errors_total 0
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Demo UI       │───▶│   FastAPI App    │───▶│  DistilBERT     │
│  (Static HTML)  │    │  (main.py)       │    │   Pipeline      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │                 │
                   ┌───▼────┐    ┌──────▼──────┐
                   │ Metrics│    │   Logging   │
                   │ Monitor│    │ Middleware  │
                   └────────┘    └─────────────┘
```

### Key Components

- **`app/main.py`**: FastAPI application with routing and middleware
- **`app/models.py`**: Thread-safe model management with lazy loading
- **`app/schemas.py`**: Pydantic models for request/response validation
- **`app/middleware.py`**: Logging and metrics collection middleware
- **`app/config.py`**: Environment-based configuration management
- **`static/demo.html`**: Interactive web interface
- **`docker/`**: Containerization and deployment configuration

## 🧪 Testing

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage report
make test-coverage

# Run specific test file
pytest tests/test_api.py -v
```

### Test Coverage
- **API Endpoints**: All REST endpoints with success/error scenarios
- **Model Management**: Lazy loading, concurrency, error handling
- **Input Validation**: Pydantic schema validation edge cases
- **Monitoring**: Health checks and metrics collection
- **Exception Handling**: Custom exception hierarchy

## 🔧 Configuration

### Environment Variables
```bash
# Application settings
APP_NAME="ML Model Service"
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Model configuration
MODEL_NAME="distilbert-base-uncased-finetuned-sst-2-english"
MODEL_CACHE_DIR="./model_cache"

# Input validation
MAX_TEXT_LENGTH=1000
MIN_TEXT_LENGTH=1
MAX_REQUEST_SIZE=1048576
```

### Docker Environment
The application automatically configures for containerized deployment with:
- Model pre-downloading during build
- Volume mounting for model persistence
- Health check configuration
- Security hardening

## 📊 Performance

### Benchmarks
- **First Request**: ~2-3 seconds (model loading)
- **Subsequent Requests**: ~50-100ms (95th percentile)
- **Throughput**: 100+ requests/second (after warmup)
- **Memory Usage**: ~512MB under normal load
- **Model Size**: ~250MB (DistilBERT)

### Optimization Features
- **Lazy Loading**: Model loads only on first request
- **Thread Safety**: Concurrent request handling with asyncio
- **Caching**: Model persistence across requests
- **Minimal Dependencies**: Optimized Docker layers

## 🔒 Security

### Security Features
- **Input Validation**: Comprehensive sanitization and size limits
- **Non-root Execution**: Docker containers run as unprivileged user
- **No Sensitive Logging**: Request data excluded from logs
- **CORS Configuration**: Configurable cross-origin policies
- **Request Size Limits**: Protection against large payload attacks

### Security Best Practices
- Regular dependency updates
- Minimal container attack surface
- Structured error responses (no stack traces in production)
- Request ID correlation for security monitoring

## 🚦 Monitoring & Alerting

### Available Metrics
- `app_requests_total`: Total HTTP requests processed
- `app_errors_total`: Total 5xx error responses
- `app_request_duration_ms`: Average response latency
- `app_model_loaded`: Model availability status

### Integration Examples

**Prometheus Configuration:**
```yaml
- job_name: 'ml-sentiment-api'
  static_configs:
    - targets: ['localhost:8000']
  metrics_path: /api/v1/metrics
```

**Grafana Dashboard Queries:**
```promql
# Request rate
rate(app_requests_total[5m])

# Error rate
rate(app_errors_total[5m]) / rate(app_requests_total[5m])

# Average latency
app_request_duration_ms
```

## 🛠️ Development

### Project Structure
```
ml-python/
├── app/                    # Application source code
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── models.py          # ML model management
│   ├── schemas.py         # Pydantic models
│   ├── middleware.py      # Logging and metrics
│   ├── exceptions.py      # Custom exceptions
│   └── config.py          # Configuration
├── tests/                 # Test suite
│   ├── test_api.py        # API endpoint tests
│   ├── test_models.py     # Model management tests
│   ├── test_schemas.py    # Schema validation tests
│   └── test_exceptions.py # Exception handling tests
├── static/                # Static web assets
│   └── demo.html          # Interactive demo UI
├── docker/                # Docker configuration
│   └── Dockerfile         # Multi-stage build
├── scripts/               # Utility scripts
│   └── download_model.py  # Model pre-download
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Service orchestration
├── Makefile              # Development commands
└── pytest.ini           # Test configuration
```

### Adding New Features
1. **New Endpoints**: Add routes in `app/main.py`
2. **Data Models**: Define schemas in `app/schemas.py`
3. **Business Logic**: Implement in dedicated modules
4. **Tests**: Add corresponding test cases
5. **Documentation**: Update API docs and README

### Code Quality
- **Type Hints**: Full type annotation coverage
- **Async/Await**: Modern Python async patterns
- **Error Handling**: Comprehensive exception management
- **Logging**: Structured JSON logging throughout
- **Testing**: High test coverage with mocking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugging Face**: For the excellent Transformers library and pre-trained models
- **FastAPI**: For the modern, fast web framework
- **DistilBERT**: For the efficient and accurate sentiment analysis model
- **Docker**: For containerization and deployment simplification

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Demo**: [Interactive Demo](http://localhost:8000/static/demo.html)

---

**Built with ❤️ using FastAPI, DistilBERT, and modern DevOps practices**