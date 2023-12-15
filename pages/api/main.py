from routers import patch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users

app = FastAPI()

origins = [
    "http://115.68.193.117:4000",
    "http://localhost:4000",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
    "http://10.10.13.20:8000",
    "http://115.68.193.117:8000",
    "http://127.0.0.1:8000",
    "http://10.10.13.20:3000",
    "http://115.68.193.117:3000",
    "http://115.68.193.117:4000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization",'Access-Control-Allow-Origin'],
)

app.include_router(patch.router)
app.include_router(users.router)