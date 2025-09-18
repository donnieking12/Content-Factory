# AI Content Factory - Setup Guide

## Prerequisites

Before you can run the AI Content Factory application, you need to install the following dependencies:

### 1. Python 3.10+

The application requires Python 3.10 or higher.

**Windows:**
1. Download Python from the official website: https://www.python.org/downloads/
2. Run the installer and make sure to check "Add Python to PATH" during installation
3. Verify installation by opening a new terminal and running:
   ```
   python --version
   ```

**macOS:**
1. Install Homebrew if you haven't already: https://brew.sh/
2. Install Python:
   ```
   brew install python
   ```

**Linux (Ubuntu/Debian):**
```
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. Docker (Optional but Recommended)

Docker is recommended for running the application with all its services.

**Download Docker Desktop:**
- Windows/macOS: https://www.docker.com/products/docker-desktop
- Linux: https://docs.docker.com/engine/install/

### 3. FFmpeg

FFmpeg is required for video processing.

**Windows:**
1. Download from https://www.gyan.dev/ffmpeg/builds/
2. Extract and add to your PATH

**macOS:**
```
brew install ffmpeg
```

**Linux:**
```
sudo apt install ffmpeg
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd content-factory-ai
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file with your actual credentials:
- Supabase URL and Key
- Social media API keys
- AI Avatar service credentials

### 5. Database Setup

The application uses Supabase as the database. You've already provided your connection string, which has been configured in the application.

To set up the database tables:

1. Make sure your Supabase key is set in the `.env` file:
   ```
   SUPABASE_KEY=your_actual_supabase_key_here
   ```

2. Run the database setup script:
   ```bash
   python setup_db.py
   ```

3. Verify that the tables were created in your Supabase dashboard.

### 6. Redis Setup

For Celery, you'll need Redis. You can:

1. Use Docker:
   ```bash
   docker run -d -p 6379:6379 redis
   ```

2. Or install Redis locally:
   - Windows: https://redis.io/download/
   - macOS: `brew install redis`
   - Linux: `sudo apt install redis`

## Running the Application

### Option 1: Using Docker (Recommended)

```bash
docker-compose up -d
```

This will start all services:
- Web application on port 8000
- Database
- Redis
- Celery worker
- Celery beat

### Option 2: Manual Setup

1. Start the web application:
   ```bash
   python run.py
   ```
   
   Or with uvicorn directly:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Start the Celery worker (in a separate terminal):
   ```bash
   celery -A celery_worker.celery_app worker --loglevel=info
   ```

3. Start the Celery beat scheduler (in a separate terminal):
   ```bash
   celery -A celery_worker.celery_app beat --loglevel=info
   ```

## Running Tests

```bash
pytest tests/
```

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Migration message"
```

Apply migrations:
```bash
alembic upgrade head
```

## Development Commands

The project includes a Makefile with common commands:

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Check code style
make lint

# Type check
make type-check

# Run Celery worker
make celery-worker

# Run Celery beat
make celery-beat

# Start with Docker
make docker-up

# Stop Docker services
make docker-down
```

## API Documentation

Once the application is running, you can access:

- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Module not found errors**: Make sure your virtual environment is activated
2. **Database connection errors**: Verify your Supabase credentials in `.env`
3. **Redis connection errors**: Ensure Redis is running
4. **Port already in use**: Change the port in docker-compose.yml or run.py

### Windows-Specific Issues

1. **Execution Policy**: If you encounter script execution errors:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Python not found**: Make sure Python is added to your PATH during installation

## Next Steps

For detailed next steps on implementing the business logic and deploying the application, please refer to [NEXT_STEPS.md](NEXT_STEPS.md).

1. Implement the actual business logic in the service modules
2. Add your social media API credentials to `.env`
3. Set up your AI avatar service
4. Customize the product discovery logic
5. Implement video generation algorithms
6. Add more tests