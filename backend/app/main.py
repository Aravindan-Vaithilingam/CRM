from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
app.include_router(api_router, prefix='/api/v1')

@app.get('/health')
def health():
    return {'status': 'ok'}
