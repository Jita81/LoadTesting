# Click Counter Load Testing App

A FastAPI and Redis-based application for testing high-frequency click event processing. The application includes a web interface for manual testing and a load testing script for performance evaluation.

## Features
- FastAPI backend with Redis for data storage
- Real-time click counting and rate calculation
- Load testing script with configurable rates
- Web interface for manual testing

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
API_URL=http://localhost:8080
```

3. Run the server:
```bash
uvicorn server:app --host 0.0.0.0 --port 8080
```

4. Run load tests:
```bash
python load_test.py
``` 