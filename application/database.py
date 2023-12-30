#db object is created so that it can be imported 
from sqlalchemy.ext.declarative import declarative_base #database models to normal python classes
from flask_sqlalchemy import SQLAlchemy

engine = None
Base = declarative_base()
db = SQLAlchemy()