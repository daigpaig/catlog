import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from database import engine
from sqlmodel import Session
from models.db_models import UserProfileDB

test_user = UserProfileDB(
    netid="wpe1403",
    majors=["Data Science"],
    minors=["Italian", "Transportation & Logistics"],
    classes_already_taken=["STAT 202", "ECON 201"],
    vocational_interests=["tech", "data analytics"],
    favorite_profs=["Dr. X", "Dr. Y"],
    disliked_profs=["Prof. Z"],
    earliest_class_time="10:00",
    locked_classes=["STAT 303-3", "ITALIAN 101", "MATH 240"]
)

with Session(engine) as session:
    session.add(test_user)
    session.commit()

print("Test user added.")