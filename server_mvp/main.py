from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize FastAPI app
app = FastAPI(title="Evaly MVP API", version="1.0.0")

# 2. Setup CORS (Cross-Origin Resource Sharing)
# This allows our React Frontend (running on a different port) to talk to this Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL e.g. ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Create a basic Health Check Route
@app.get("/")
def read_root():
    return {"message": "Welcome to Evaly MVP Backend 🚀", "status": "Online"}

@app.get("/api/ping")
def ping():
    return {"ping": "pong!"}
