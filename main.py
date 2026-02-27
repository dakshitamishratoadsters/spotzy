from fastapi import FastAPI
from src.api.v1.routes.routes import router as router

app = FastAPI()
app.include_router(router)