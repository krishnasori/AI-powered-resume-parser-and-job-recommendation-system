from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# For now, we will use a local SQLite file for development. 
# It takes only 1 line of code to swap this to a live Cloud PostgreSQL URL later!
SQLALCHEMY_DATABASE_URL = "sqlite:///./saas_app.db"

# Create the database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session maker to talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This Base class is what all our database models will inherit from
Base = declarative_base()

# Dependency to get the database session in our API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()