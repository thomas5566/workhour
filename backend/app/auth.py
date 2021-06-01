from fastapi_login import LoginManager
# from app import config
from app.database import SessionLocal
from app import models
import os

# SECRET = config.settings.SECRET
SECRET = str(os.urandom(24).hex)
login_manager = LoginManager(SECRET, '/login')

@login_manager.user_loader
def get_user(user_id: int):
	db = SessionLocal()
	return db.query(models.User).filter(models.User.id == user_id).first()