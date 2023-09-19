import uvicorn as uvicorn
import sys
import os
sys.path.append(os.path.abspath(".."))

from app.api import user, task, workhour, expentask, expen, authentication, route_login, department, daysoff, cstshop
from app.database import engine, Base
from app.dependency import create_default_data
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


# For DEV only, remove below 4 lines in production
# from app.dependency import create_default_data
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)
# create_default_data()

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"/api/openapi.json",
)

# Set all CORS enabled origins
# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

origins = ["*"]
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://0.0.0.0:8080",
    "http://10.133.6.45",
    "http://10.133.6.45:80",
    "http://127.0.0.1:8000",
    "http://172.25.108.49:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

router = APIRouter()
# Now add the router to the app
app.include_router(router, prefix=settings.API_V1_STR)

# app.include_router(authentication.router)
app.include_router(user.router, prefix=settings.API_V1_STR)
app.include_router(department.router, prefix=settings.API_V1_STR)
app.include_router(task.router, prefix=settings.API_V1_STR)
app.include_router(workhour.router, prefix=settings.API_V1_STR)
app.include_router(expentask.router, prefix=settings.API_V1_STR)
app.include_router(expen.router, prefix=settings.API_V1_STR)
app.include_router(daysoff.router, prefix=settings.API_V1_STR)
app.include_router(cstshop.router, prefix=settings.API_V1_STR)
# app.include_router(route_login.router)


@app.get("/api")
async def root():
    return RedirectResponse(url='/api/user')

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, prefix=settings.API_V1_STR)
