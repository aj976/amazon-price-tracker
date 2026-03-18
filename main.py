from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import products, tracking

app = FastAPI(title="Amazon Price Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracking.router)
app.include_router(products.router)