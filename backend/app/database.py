from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from app import config
import urllib
import os

# SQLALCHEMY_DATABASE_URL = config.settings.DATABASE_URL

# For office local postgresql
host_server = os.environ.get('host_server', '10.133.6.45') # Server Name
db_server_port = urllib.parse.quote_plus(
    str(os.environ.get('db_server_port', '5432'))) # Server Port
database_name = os.environ.get('database_name', 'workhour') # Database Name
db_username = urllib.parse.quote_plus(
    str(os.environ.get('db_username', 'postgres'))) 
db_password = urllib.parse.quote_plus(
    str(os.environ.get('db_password', '1234')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode', 'prefer')))
SQLALCHEMY_DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(
    db_username, db_password, host_server, db_server_port, database_name, ssl_mode)

# For Docker image postgresql
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/workhour"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
