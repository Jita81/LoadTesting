from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import redis.asyncio as redis
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis
if os.getenv('REDIS_URL'):
    # Railway Redis URL format: redis://default:password@host:port
    redis_url = os.getenv('REDIS_URL')
    print(f"Connecting to Redis using URL: {redis_url.split('@')[1]}")  # Only print host:port part
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        print("Redis client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Redis client: {str(e)}")
        raise e
else:
    # Local development Redis
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', 6379))
    print(f"Connecting to Redis at {host}:{port}")
    try:
        redis_client = redis.Redis(
            host=host,
            port=port,
            password=os.getenv('REDIS_PASSWORD', None),
            db=0,
            decode_responses=True
        )
        print("Redis client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Redis client: {str(e)}")
        raise e

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/api/health")
async def health_check():
    try:
        # Test Redis connection
        await redis_client.ping()
        return JSONResponse({"status": "healthy"})
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

@app.post("/api/log-click")
async def log_click():
    timestamp = time.time()
    async with redis_client.pipeline(transaction=True) as pipe:
        await pipe.zadd('click_timestamps', {str(timestamp): timestamp})
        await pipe.incr('total_clicks')
        await pipe.execute()
    return JSONResponse({"status": "success"})

@app.get("/api/stats")
async def get_stats():
    total_clicks = await redis_client.get('total_clicks')
    total_clicks = int(total_clicks) if total_clicks else 0
    
    now = time.time()
    recent_clicks = await redis_client.zcount(
        'click_timestamps',
        now - 1,
        now
    )
    
    return JSONResponse({
        "total_clicks": total_clicks,
        "clicks_per_second": recent_clicks
    })

@app.on_event("startup")
async def startup_event():
    try:
        print("Testing Redis connection...")
        await redis_client.ping()
        print("Redis connection successful!")
        await redis_client.flushdb()
        print("Redis database flushed.")
    except Exception as e:
        print(f"Redis connection failed: {str(e)}")
        raise e 