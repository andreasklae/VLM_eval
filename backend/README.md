# Image Recognition Module

Multi-approach image recognition system for identifying visual content including landmarks, buildings, monuments, artworks, paintings, statues, viewpoints, and other notable subjects.

## Approaches

1. **GPT Vision Direct** - Uses Azure OpenAI gpt-4o vision to directly identify visual content
2. **GPT Vision + Search** - Two-stage: describes image in detail, then searches Wikipedia/Google/web/vector store
3. **Google Cloud Vision** - Uses Google's Vision API with multiple detection types (landmark, object, label, web)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file or set environment variables:

```bash
# Azure OpenAI (required for GPT Vision approaches)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o  # Must support vision

# OpenAI Direct API (required for Agents SDK web search in GPT Vision + Search)
OPENAI_DIRECT_API_KEY=your-direct-openai-api-key

# Google Cloud Vision (optional)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Google Custom Search (optional, enhances GPT Vision + Search approach)
GOOGLE_API_KEY=your-google-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
```

### 3. Google Cloud Vision Setup

1. Go to https://console.cloud.google.com/
2. Create or select a project
3. Enable "Cloud Vision API"
4. Go to IAM & Admin → Service Accounts
5. Create service account with "Cloud Vision API User" role
6. Create JSON key and download
7. Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of the JSON key

**Free tier:** 1,000 units/month, $300 free credits for new accounts.

## FastAPI Server

The module includes a FastAPI server that exposes image recognition as a REST API.

### Starting the Server

```bash
# Using the startup script
python run_server.py

# Or directly with uvicorn
uvicorn image_recognition.server:app --reload

# Custom host/port
python run_server.py --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000` by default.

### API Endpoints

#### `GET /`
API information and available endpoints.

#### `GET /health`
Health check endpoint.

#### `GET /approaches`
List all available recognition approaches and their availability status.

**Response:**
```json
[
  {
    "name": "GPT Vision Direct",
    "available": true
  },
  {
    "name": "GPT Vision + Search",
    "available": true
  },
  {
    "name": "Google Cloud Vision",
    "available": false
  }
]
```

#### `POST /recognize`
Recognize visual content in an uploaded image.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `image` file (multipart file upload)
- Query parameter (optional): `approaches` - Comma-separated list of approach names (e.g., `?approaches=GPT Vision Direct,Google Cloud Vision`). If not provided, all available approaches will be used.

**Response:**
```json
{
  "image_filename": "IMG_8664.JPG",
  "timestamp": "2026-01-23T16:29:03.359386",
  "processing_time_seconds": 19.629,
  "approaches": [
    {
      "approach": "GPT Vision Direct",
      "identified": "Great Pyramid of Giza, Giza, Egypt",
      "confidence": 1.0,
      "success": true,
      "error": null,
      "details": {
        "reasoning": "...",
        "features": [...],
        "location": "Giza, Egypt",
        "type": "landmark"
      }
    }
  ]
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/recognize" \
  -F "image=@path/to/image.jpg"

# With specific approaches
curl -X POST "http://localhost:8000/recognize?approaches=GPT Vision Direct" \
  -F "image=@path/to/image.jpg"
```

**Example using Python:**
```python
import httpx

with open("image.jpg", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/recognize",
        files={"image": ("image.jpg", f, "image/jpeg")}
    )
    result = response.json()
    print(result)
```

### Batch Testing via API

The batch test script in `testing/Image_search/batch_test.py` uses the API:

```bash
# Make sure the server is running first
python run_server.py

# In another terminal, run batch tests
cd testing/Image_search
python batch_test.py

# With custom server URL
python batch_test.py --server-url http://localhost:8000
```

## Usage

### Command Line

```bash
# Run recognition on an image
python run_recognition.py path/to/image.jpg

# Output as JSON
python run_recognition.py path/to/image.jpg --json

# List available approaches
python run_recognition.py --list-approaches
```

### Python API

```python
import asyncio
from image_recognition import recognize_image, get_available_approaches

# List available approaches
approaches = get_available_approaches()
for a in approaches:
    print(f"- {a.name}")

# Run recognition
async def main():
    results = await recognize_image("path/to/image.jpg")
    for result in results:
        if result.success:
            print(f"[{result.approach}] {result.identified}")
            if result.confidence:
                print(f"  Confidence: {result.confidence:.0%}")
        else:
            print(f"[{result.approach}] Error: {result.error}")

asyncio.run(main())
```

### Using Specific Approaches

```python
from image_recognition.gpt_vision_direct import GPTVisionDirectApproach
from image_recognition.runner import recognize_image

# Run only specific approaches
approach = GPTVisionDirectApproach()
result = await recognize_image("image.jpg", approaches=[approach])
```

## Output Format

Each approach returns a `RecognitionResult`:

```python
@dataclass
class RecognitionResult:
    approach: str           # Name of the approach
    identified: str | None  # What was identified (e.g., "Eiffel Tower, Paris")
    confidence: float | None  # 0-1 confidence score
    details: dict           # Approach-specific details
    error: str | None       # Error message if failed
```

## Architecture

```
image_recognition/
├── __init__.py           # Package exports
├── base.py               # Base classes (RecognitionResult, ImageRecognitionApproach)
├── config.py             # Settings from environment
├── runner.py             # Parallel execution runner
├── server.py             # FastAPI server (API endpoints)
├── run_server.py         # Server startup script
├── run_recognition.py    # CLI entry point
├── gpt_vision_direct/    # Approach 1: Direct GPT-4o vision
├── gpt_vision_search/    # Approach 2: Description + search
│   ├── approach.py       # Main approach logic
│   ├── search_wikipedia.py
│   ├── search_google.py
│   └── search_web.py
└── google_cloud_vision/  # Approach 3: Google Cloud Vision API
```

## Extending

### Adding a New Search Backend

1. Create `search_<name>.py` in `gpt_vision_search/`
2. Implement `is_available()` and `search_<name>()` functions
3. Add to `_search_all_backends()` in `approach.py`

### Adding a New Approach

1. Create new directory under `image_recognition/`
2. Implement class extending `ImageRecognitionApproach`
3. Add import to `runner.py` in `get_available_approaches()`

## Vector Store / RAG (Future)

A vector/semantic search backend could be added in the future to complement keyword-based search:

1. Build a landmark database from sources (Wikipedia, UNESCO, Riksantikvaren)
2. Generate embeddings using OpenAI embeddings API
3. Store in vector database (e.g., Chroma, Pinecone, or OpenAI's vector store)
4. Create `search_vector.py` in `gpt_vision_search/` implementing `is_available()` and `search_vector_store()`
5. Register in `_search_all_backends()` in `approach.py`
