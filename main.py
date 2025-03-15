from fastapi import FastAPI
from routes import router

app = FastAPI()

# ✅ Include routes from routes.py
app.include_router(router)
