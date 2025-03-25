import os
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
from .models import User, Movie, Comment

# Leer la URL de conexión desde el entorno; si no se define, usar la de localhost
DB_URL = os.getenv("DB_URL", "mysql+pymysql://user:password@db/movies")
engine = create_engine(DB_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)

# For use with 'with' statement
@contextmanager
def get_session_context():
    with Session(engine) as session:
        yield session

# For use with FastAPI dependencies
def get_session():
    with Session(engine) as session:
        yield session  # Notice we're using yield, not return

def seed_users():
    from auth.password import hash_password
    
    with Session(engine) as session:
        users = [
            User(username="Alice", email="alice@example.com", 
                 password=hash_password("password123")),
            User(username="Bob", email="bob@example.com", 
                 password=hash_password("password456")),
            User(username="Charlie", email="charlie@example.com", 
                 password=hash_password("password789")),
        ]
        session.add_all(users)
        session.commit()


def seed_movies():
    with Session(engine) as session:
        movies = [
            Movie(title="Inception", director="Christopher Nolan", year=2010, genre="Sci-Fi"),
            Movie(title="The Matrix", director="Lana Wachowski, Lilly Wachowski", year=1999, genre="Sci-Fi"),
            Movie(title="Interstellar", director="Christopher Nolan", year=2014, genre="Sci-Fi"),
            Movie(title="The Godfather", director="Francis Ford Coppola", year=1972, genre="Drama"),
            Movie(title="Pulp Fiction", director="Quentin Tarantino", year=1994, genre="Crime")
        ]
        session.add_all(movies)
        session.commit()
