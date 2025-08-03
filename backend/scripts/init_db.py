import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from database import engine
from models.db_models import UserProfileDB
from sqlmodel import SQLModel

SQLModel.metadata.create_all(engine)
print("Database tables created")

print(sys.path)