from typing import Any, List, Optional
from fastapi import HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from db import Comment, User, Movie, get_session
from auth import authenticator
from utils import get_logger
from ia import SentimentModel

logger = get_logger("comment_controller")

# Pydantic models for API requests and responses
class CommentCreate(BaseModel):
    user_id: int
    text: str

class CommentResponse(BaseModel):
    movie_id: int
    title: str
    user_id: int
    username: Optional[str] = None
    text: str
    sentiment: str

class CommentController:
    @staticmethod
    def get_comments_by_movie(id: int, db: Session = Depends(get_session)) -> List[CommentResponse]:
        """
        Devuelve una lista con todos los comentarios de la película con el id especificado.
        """
        movie = db.get(Movie, id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        comments = db.exec(select(Comment).where(Comment.movie_id == id)).all()
        
        results = []
        for c in comments:
            user = db.get(User, c.user_id)
            results.append(CommentResponse(
                movie_id=c.movie_id,
                title=movie.title,
                user_id=c.user_id,
                username=user.username if user else None,
                text=c.text,
                sentiment=c.sentiment
            ))
        return results

    @staticmethod
    async def add_comment(
        id: int, 
        comment: CommentCreate, 
        db: Session = Depends(get_session),
        auth: dict = Depends(authenticator)
    ) -> CommentResponse:
        """
        Añade un nuevo comentario a la película con el id especificado.
        
        Requiere autenticación mediante token JWT.
        El campo sentiment se rellenará automáticamente usando el modelo de análisis de sentimiento.
        """
        movie = db.get(Movie, id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Use the movie_id from the path parameter
        movie_id = id
        
        # Get user_id from the request body (CommentCreate model)
        user_id = comment.user_id
        
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.debug(f"Usuario {user.username} añadiendo comentario a película {movie.title}")
        
        sentiment = SentimentModel.analyze_sentiment(comment.text)
        new_comment = Comment(
            movie_id=movie_id, 
            user_id=user_id, 
            text=comment.text, 
            sentiment=sentiment
        )
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        return CommentResponse(
            movie_id=new_comment.movie_id,
            title=movie.title,
            user_id=new_comment.user_id,
            username=user.username,
            text=new_comment.text,
            sentiment=new_comment.sentiment
        )