"""Create the prototype PostgreSQL schema."""
from app.db import Base, engine
import app.models  # noqa: F401 - registers all model tables

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("AROGYASETU database schema initialized.")
