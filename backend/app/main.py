import sys
import os
sys.path.append(os.path.abspath(".."))

import uvicorn as uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.api import user, task, workhour, expentask, expen, department, daysoff
from app.dependency import create_default_data
from app.database import engine, Base



# from app.models.base_class import Base
# from app.models.database import engine


# For DEV only, remove below 4 lines in production
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)
# create_default_data()

app = FastAPI()

origins = ["*"]
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8082",
    "http://0.0.0.0:8080",
    "http://192.168.0.123:8080",
    "http://192.168.2.178:8080"
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


@app.get("/")
async def root():
    return "Hello FastAPI"

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000)
