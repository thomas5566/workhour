from fastapi_login import LoginManager
# from app import config
from .database import SessionLocal
# from app import models
from .models import User
import os

# SECRET = config.settings.SECRET
SECRET = str(os.urandom(24).hex)
login_manager = LoginManager(SECRET, '/user/login')


@login_manager.user_loader
def get_user(user_id: int):
    db = SessionLocal()
    return db.query(User).filter(User.id == user_id).first()
