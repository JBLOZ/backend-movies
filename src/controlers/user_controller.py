from typing import Any
from fastapi import HTTPException
from sqlmodel import Session, select
from db import User, Comment
from pydantic import BaseModel
from utils import get_logger

logger = get_logger("user_controller")

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserController:
    @staticmethod
    def list_users(db: Session) -> list[dict[str, Any]]:
        """
        Devuelve una lista con todos los usuarios registrados en la base de datos.
        """
        logger.debug("Listando todos los usuarios")
        users = db.exec(select(User)).all()
        return [{"id": u.id, "username": u.username} for u in users]

    @staticmethod
    def get_user(id: int, db: Session) -> User:
        """
        Devuelve los datos del usuario con el id especificado.
        """
        logger.debug(f"Consultando usuario con id: {id}")
        user = db.get(User, id)
        if not user:
            logger.warning(f"Usuario con id {id} no encontrado")
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def create_user(user_data: UserCreate, db: Session, hash_password_func) -> User:
        """
        Crea un nuevo usuario en la base de datos y devuelve los datos del usuario sin la contraseña.
        """
        logger.debug(f"Intentando crear usuario: {user_data.username}")
        existing_user = db.exec(select(User).where(User.username == user_data.username)).first()
        if existing_user:
            logger.warning(f"Intento de crear usuario con nombre ya existente: {user_data.username}")
            raise HTTPException(
                status_code=409,
                detail="Username already exists. Please choose another username."
            )
        hashed_password = hash_password_func(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.debug(f"Usuario creado correctamente: {new_user.username} (ID: {new_user.id})")
        
        return new_user

    @staticmethod
    def get_comments_by_user(id: int, db: Session) -> list[dict[str, Any]]:
        """
        Devuelve una lista con todos los comentarios del usuario con el id especificado.
        """
        user = db.get(User, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        from db.models import Movie
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
        logger.debug(f"Comentarios del usuario {user.username} (ID: {user.id}) cargados correctamente")
        return results