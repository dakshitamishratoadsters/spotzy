from sqlmodel import SQLModel
from src.db.database import engine
from src.db.models import *
def init_db():
    SQLModel.metadata.create_all(engine)