# Token Counter API & Frontend

A FastAPI-based Python application that provides a REST API to count tokens in a given text input, along with a Streamlit frontend for easy interaction. This tool helps anticipate token usage for AI-powered features and can be integrated into different environments.

## Features

### API Features
- Count tokens for text inputs using various AI model tokenizers
- Batch processing capability for multiple text inputs
- Environment-specific configurations (dev, qa, prod)
- Basic authentication for API access
- Rate limiting to prevent abuse

### Frontend Features
- User-friendly interface for token counting
- Support for single text and batch processing
- Model selection dropdown
- Real-time token counting with visual feedback
- Results visualization with metrics and data tables
- View raw API responses

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TokenCounter.git
cd TokenCounter
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (use `.env.example` as a template):
```bash
cp .env.example .env
```

## Usage

### Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

### Running the Frontend

After starting the API server, run the Streamlit frontend:

```bash
streamlit run frontend/app.py
```

The frontend will be available at http://localhost:8501.

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Endpoints

- `GET /v1/health` - Health check
- `POST /v1/tokens/count` - Count tokens for a single text
- `POST /v1/tokens/batch-count` - Count tokens for multiple texts

### Frontend Interface

The Streamlit interface provides two main tabs:

1. **Single Text** - Enter a single text and get token count
2. **Batch Processing** - Enter multiple texts (one per line) and get counts for all

The sidebar includes:
- Model selection
- API connection status
- Security information
- Debug/configuration details

### Testing the Batch API Endpoint

To test the batch endpoint with multiple texts:

```bash
curl -X POST "http://localhost:8000/v1/tokens/batch-count" \
     -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ=" \
     -H "Content-Type: application/json" \
     -d '{
        "texts": [
            {"text": "Hello world!", "text_id": "text1"},
            {"text": "This is a second example with more tokens.", "text_id": "text2"},
            {"text": "The third example has even more tokens to count for this test.", "text_id": "text3"}
        ],
        "model": "gpt-3.5-turbo"
     }'
```

#### Important Note About Models

While the OpenAPI schema shows that you can specify a model per text item, the current implementation only uses the top-level `model` parameter for all texts in a batch. Any `model` values specified at the individual text level are ignored.

To process texts with different models, use separate batch requests for each model or multiple single-text requests.

### Example API Request

```bash
curl -X POST "http://localhost:8000/v1/tokens/count" \
     -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ=" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world!", "model": "gpt-3.5-turbo"}'
```

Response:
```json
{
  "token_count": 3,
  "model": "gpt-3.5-turbo",
  "processing_time_ms": 2
}
```

## Configuration

The application uses environment variables for configuration:

- `ENVIRONMENT` - Environment (dev, qa, prod)
- `API_USERNAME` - Username for API authentication
- `API_PASSWORD` - Password for API authentication 
- `API_HOST` - The base URL of the API (frontend only, default: "http://localhost:8000")

Both the API and frontend use the same `.env` file located at the project root.

## Data Privacy & Security

### Local Processing Only

The Token Counter API processes all text data entirely within your environment:

- **No Outbound Data Transfer**: The application never sends any of your text data to external services.
- **Local Tokenization**: While we use OpenAI's `tiktoken` library, this library runs locally on your server and does not transmit data to OpenAI.
- **No External API Calls**: The tokenization process makes no external API calls or network requests.
- **No Telemetry or Analytics**: The application doesn't include any analytics, telemetry, or external logging that would send data outside your environment.

This makes the tool suitable for processing sensitive or confidential information, as all data remains within your controlled environment.

## Running Tests

The project uses pytest for testing the application functionality. The test suite includes:

### Test Categories
- **API Tests**: Verify endpoints, authentication, and responses
- **Token Counter Tests**: Test the core token counting functionality
- **Performance Tests**: Ensure the application meets performance requirements
- **Environment Tests**: Validate environment-specific configurations

### Running Tests

Run all tests:
```bash
pytest
```

Run specific test files:
```bash
pytest tests/test_api.py
pytest tests/test_token_counter.py
pytest tests/test_performance.py
pytest tests/test_env.py
```

Run tests with verbose output:
```bash
pytest -v
```

### Test Configuration

The test setup includes:
- `conftest.py`: Configures the Python path for tests
- `pytest.ini`: Defines test discovery patterns
- `setup.py`: Makes the package installable for testing

### Troubleshooting Tests

If you encounter authentication errors during testing:
- Ensure your `.env` file has the correct credentials
- The tests use environment variables for authentication
- Run tests from the project root directory

If performance tests are failing:
- Tests may run slower in CI environments than local development
- Adjust thresholds in `test_performance.py` if necessary

## Docker

### Running Individual Containers

Build and run the API:
```bash
docker build -t token-counter-api .
docker run -p 8000:8000 -e ENVIRONMENT=prod token-counter-api
```

Build and run the frontend:
```bash
cd frontend
docker build -t token-counter-frontend .
docker run -p 8501:8501 -e API_HOST=http://localhost:8000 -e API_USERNAME=admin -e API_PASSWORD=securepassword token-counter-frontend
```

### Using Docker Compose (Recommended)

For a complete setup with both API and frontend:

1. Build and start both containers:
```bash
docker-compose up -d
```

2. Access the services:
   - API: http://localhost:8000
   - Frontend: http://localhost:8501

3. Stop the services:
```bash
docker-compose down
```

## License

[MIT](LICENSE)

# Generated by Copilot
