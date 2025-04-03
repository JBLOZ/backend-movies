from typing import Any, List, Optional, Dict
from fastapi import HTTPException, Query, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from db import Movie, Comment, get_session
from auth import authenticator
from utils import get_logger

logger = get_logger("movie_controller")

# Pydantic models for API requests and responses
class MovieCreate(BaseModel):
    title: str
    director: str
    year: int
    genre: str


class MovieController:
    @staticmethod
    def list_movies(db: Session = Depends(get_session)) -> List[Dict[str, Any]]:
        """
        Devuelve una lista con todas las películas registradas en la base de datos.
        """
        logger.debug("Listando todas las películas")
        movies = db.exec(select(Movie)).all()
        # Convert Pydantic models to dictionaries
        return [{"id": m.id, "title": m.title} for m in movies]

    @staticmethod
    def search_movies(title: str = Query(...), db: Session = Depends(get_session)) -> List[Dict[str, Any]]:
        """
        Busca películas por título.
        
        Devuelve todas las películas que contengan la cadena a buscar en el título 
        (en cualquier posición y sin distinción de mayúsculas y minúsculas).
        """
        logger.debug(f"Buscando películas con título: {title}")
        query = select(Movie).where(Movie.title.ilike(f"%{title}%"))
        movies = db.exec(query).all()
        logger.debug(f"Encontradas {len(movies)} películas con título que contiene: {title}")
        # Convert Pydantic models to dictionaries
        return [{"id": m.id, "title": m.title} for m in movies]
        
    @staticmethod
    def get_movie(id: int, db: Session = Depends(get_session)) -> Dict[str, Any]:
        """
        Devuelve los datos de la película con el id especificado.
        """
        logger.debug(f"Consultando película con id: {id}")
        movie = db.get(Movie, id)
        if not movie:
            logger.warning(f"Película con id {id} no encontrada")
            raise HTTPException(status_code=404, detail="Movie not found")
        # Return a dictionary instead of a Pydantic model
        return {
            "id": movie.id,
            "title": movie.title,
            "director": movie.director,
            "year": movie.year,
            "genre": movie.genre
        }
        
    @staticmethod
    async def create_movie(
        movie: MovieCreate, 
        db: Session = Depends(get_session),
        auth: dict = Depends(authenticator)
    ) -> Dict[str, Any]:
        """
        Crea una nueva película en la base de datos.
        Requiere autenticación mediante token JWT.
        """
        logger.debug(f"Creando nueva película: {movie.title}")
        # Create a new Movie instance from the MovieCreate DTO
        movie_obj = Movie(
            title=movie.title,
            director=movie.director,
            year=movie.year,
            genre=movie.genre
        )
        db.add(movie_obj)
        db.commit()
        db.refresh(movie_obj)
        
        # Return a dictionary instead of a Pydantic model
        return {
            "id": movie_obj.id,
            "title": movie_obj.title,
            "director": movie_obj.director,
            "year": movie_obj.year,
            "genre": movie_obj.genre
        }
        
    @staticmethod
    async def delete_movie(
        id: int, 
        db: Session = Depends(get_session),
        auth: dict = Depends(authenticator)
    ) -> dict[str, str]:
        """
        Elimina la película con el id especificado de la base de datos.
        
        Requiere autenticación mediante token JWT.
        Si la película tiene comentarios asociados, también se eliminarán.
        """
        logger.debug(f"Intentando eliminar película con id: {id}")
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