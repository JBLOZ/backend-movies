# src/main.py
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlmodel import Session, select
import uvicorn
from datetime import datetime, timedelta
from pydantic import BaseModel
from db import get_session, create_db_and_tables, drop_db_and_tables, seed_users, seed_movies
from db.models import User, Movie, Comment, MovieCreate
from ia import SentimentModel  # Se actualiza la importación para que coincida con la estructura del pythonpath
from auth.jwt import authenticator, create_jwt_token  # se actualiza la importación
from auth.password import hash_password, verify_password  # se actualiza la importación


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configurar logging
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        filename='logs/movies.log',
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicializar la base de datos
    try:
        logging.info("Creando tablas y datos iniciales...")
        create_db_and_tables()
        seed_users()
        seed_movies()
        logging.info("Base de datos inicializada correctamente")
    except Exception as e:
        logging.error(f"Error al inicializar la base de datos: {str(e)}")
        raise
    
    yield
    
    # Tareas de limpieza al cerrar la app
    logging.info("Aplicación terminando...")

app = FastAPI(lifespan=lifespan)

### Endpoints de Usuarios ###

@app.get("/users", response_model=list[User])
def list_users(db: Session = Depends(get_session)):
    users = db.exec(select(User)).all()
    # Solo se devuelven id y username en la respuesta
    return [{"id": u.id, "username": u.username} for u in users]

@app.get("/users/{id}")
def get_user(id: int, db: Session = Depends(get_session)):
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Devuelve id, username y email
    return {"id": user.id, "username": user.username, "email": user.email}

# Add this with your other models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Add this endpoint after your other user endpoints
@app.post("/users", status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_session)):
    """Create a new user with validation for existing usernames"""
    # Check if username already exists
    existing_user = db.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists. Please choose another username."
        )
    
    # Hash the password

    hashed_password = hash_password(user_data.password)
    

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password
    )
    

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "password": hashed_password[:7] + "*" * (len(hashed_password) - 8)
    }

### Endpoints de Películas ###

@app.get("/movies")
def list_movies(db: Session = Depends(get_session)):
    movies = db.exec(select(Movie)).all()
    # Devuelve solo id y title
    return [{"id": m.id, "title": m.title} for m in movies]

@app.get("/movies/search")
def search_movies(title: str = Query(...), db: Session = Depends(get_session)):
    query = select(Movie).where(Movie.title.ilike(f"%{title}%"))
    movies = db.exec(query).all()
    return [{"id": m.id, "title": m.title} for m in movies]

@app.get("/movies/{id}")
def get_movie(id: int, db: Session = Depends(get_session)):
    movie = db.get(Movie, id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {
        "id": movie.id,
        "title": movie.title,
        "director": movie.director,
        "year": movie.year,
        "genre": movie.genre
    }

@app.post("/movies", status_code=201)
def create_movie(movie: MovieCreate, db: Session = Depends(get_session)):
    movie_obj = Movie.from_orm(movie)
    db.add(movie_obj)
    db.commit()
    db.refresh(movie_obj)
    return {
        "id": movie_obj.id,
        "title": movie_obj.title,
        "director": movie_obj.director,
        "year": movie_obj.year,
        "genre": movie_obj.genre
    }

@app.delete("/movies/{id}")
def delete_movie(id: int, db: Session = Depends(get_session)):
    movie = db.get(Movie, id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    # Se eliminan también los comentarios asociados
    comments = db.exec(select(Comment).where(Comment.movie_id == id)).all()
    for c in comments:
        db.delete(c)
    db.delete(movie)
    db.commit()
    return {"detail": "Movie deleted successfully"}

### Endpoints de Comentarios ###

@app.get("/users/{id}/comments")
def get_comments_by_user(id: int, db: Session = Depends(get_session)):
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Se consultan los comentarios y se unen con la información de la película
    comments = db.exec(select(Comment).where(Comment.user_id == id)).all()
    results = []
    for c in comments:
        movie = db.get(Movie, c.movie_id)
        results.append({
            "movie_id": c.movie_id,
            "title": movie.title if movie else None,
            "user_id": c.user_id,
            "username": user.username,
            "text": c.text,
            "sentiment": c.sentiment
        })
    return results

@app.get("/movies/{id}/comments")
def get_comments_by_movie(id: int, db: Session = Depends(get_session)):
    movie = db.get(Movie, id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    comments = db.exec(select(Comment).where(Comment.movie_id == id)).all()
    results = []
    for c in comments:
        user = db.get(User, c.user_id)
        results.append({
            "movie_id": c.movie_id,
            "title": movie.title,
            "user_id": c.user_id,
            "username": user.username if user else None,
            "text": c.text,
            "sentiment": c.sentiment
        })
    return results

@app.post("/movies/{id}/comments", status_code=201)
def add_comment(id: int, comment_data: dict, db: Session = Depends(get_session)):
    """
    Se espera en el cuerpo un JSON con:
      - user_id: int
      - text: str
    El campo sentiment se genera automáticamente.
    """
    movie = db.get(Movie, id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    user_id = comment_data.get("user_id")
    text = comment_data.get("text")
    if user_id is None or text is None:
        raise HTTPException(status_code=422, detail="user_id and text are required")
    
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    sentiment = SentimentModel.analyze_sentiment(text)
    new_comment = Comment(movie_id=id, user_id=user_id, text=text, sentiment=sentiment)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return {
        "movie_id": new_comment.movie_id,
        "title": movie.title,
        "user_id": new_comment.user_id,
        "username": user.username,
        "text": new_comment.text,
        "sentiment": new_comment.sentiment
    }

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(login_data: LoginRequest, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == login_data.username)).first()
    from auth.password import verify_password
    
    # Buscar el usuario por nombre de usuario
    user = db.exec(select(User).where(User.username == login_data.username)).first()
    
    # Verificar si el usuario existe y la contraseña es correcta
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Crear token JWT
    token_data = {
        "sub": str(user.id),
        "username": user.username
    }
    token = create_jwt_token(token_data)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
