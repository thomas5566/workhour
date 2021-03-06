import uvicorn as uvicorn
import sys
import os
sys.path.append(os.path.abspath(".."))

from app.api import user, task, workhour, expentask, expen, authentication, route_login, department, daysoff
from app.database import engine, Base
from app.dependency import create_default_data
from app.api import user, task, workhour, expentask, expen, department, daysoff
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



# For DEV only, remove below 4 lines in production
# from app.dependency import create_default_data
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
# create_default_data()

app = FastAPI()

origins = ["*"]
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://0.0.0.0:8080",
    "http://192.168.0.123:8080",
    "http://192.168.0.124:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

# app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(department.router)
app.include_router(task.router)
app.include_router(workhour.router)
app.include_router(expentask.router)
app.include_router(expen.router)
app.include_router(daysoff.router)
# app.include_router(route_login.router)


@app.get("/")
async def root():
    return "Hello FastAPI"

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000)
