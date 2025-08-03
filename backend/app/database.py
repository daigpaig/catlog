from sqlmodel import SQLModel, create_engine

sqlite_file_name = "database.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo = True)

def init_db():
    from models.db_models import UserProfileDB
    SQLModel.metadata.create_all(engine)