
from fastapi import FastAPI

app = FastAPI(
    title="AI Document Assistant",
    description="Ask questions about PDF documents.",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "message": "Welcome to the AI Document Assistant!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
