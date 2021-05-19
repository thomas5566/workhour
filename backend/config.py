from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "WorkHour"
    ADMIN_EMAIL: str
    DATABASE_URL: str
    SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()