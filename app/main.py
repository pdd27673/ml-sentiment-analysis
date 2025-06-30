from fastapi import FastAPI
from .config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)


@app.get("/")
async def root():
    return {"message": "ML Model Service is running", "status": "healthy"}