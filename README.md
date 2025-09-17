# AI Content Factory

An automated system that discovers trending products, clones viral video formats, generates new video scripts using AI, creates videos using an AI avatar service, and publishes them to multiple social media platforms.

## Core Tech Stack

- Language: Python 3.10+
- Framework: FastAPI
- Asynchronous Tasks: Celery with Redis
- Database: PostgreSQL with SQLAlchemy (and Alembic for migrations) - replaced with Supabase
- Data Validation: Pydantic
- Video Processing: FFmpeg (using the ffmpeg-python library)
- Containerization: Docker

## Project Structure

```
content-factory-ai/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── products.py
│   │   │   ├── videos.py
│   │   │   └── social_media.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   ├── video.py
│   │   └── social_media.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   ├── video.py
│   │   └── social_media.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── product_discovery.py
│   │   ├── video_generation.py
│   │   ├── ai_avatar.py
│   │   └── social_media_publisher.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_products.py
│   └── test_videos.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── celery_worker.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── run.py
├── Makefile
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (recommended)
- FFmpeg

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd content-factory-ai
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

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

### Running the Application

#### Using Docker (Recommended)

```bash
docker-compose up -d
```

#### Using Python directly

```bash
python run.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload
```

### Running Background Tasks

Start the Celery worker:

```bash
celery -A celery_worker.celery_app worker --loglevel=info
```

Start the Celery beat scheduler (for periodic tasks):

```bash
celery -A celery_worker.celery_app beat --loglevel=info
```

### Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Migration message"
```

Apply migrations:

```bash
alembic upgrade head
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create a product
- `GET /api/v1/products/{id}` - Get a product
- `PUT /api/v1/products/{id}` - Update a product
- `DELETE /api/v1/products/{id}` - Delete a product
- `GET /api/v1/videos/` - List videos
- `POST /api/v1/videos/` - Create a video
- `GET /api/v1/videos/{id}` - Get a video
- `PUT /api/v1/videos/{id}` - Update a video
- `DELETE /api/v1/videos/{id}` - Delete a video
- `GET /api/v1/social-media/` - List social media posts
- `POST /api/v1/social-media/` - Create a social media post
- `GET /api/v1/social-media/{id}` - Get a social media post
- `PUT /api/v1/social-media/{id}` - Update a social media post
- `DELETE /api/v1/social-media/{id}` - Delete a social media post

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
```

### Linting

```bash
flake8 .
```

### Type Checking

```bash
mypy app/
```

## Project Components

### Product Discovery
The system discovers trending products from various sources and stores them in the database.

### Video Generation
AI-powered video script generation and AI avatar-based video creation.

### Social Media Publishing
Publish videos to TikTok, Instagram, YouTube, and other platforms.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.