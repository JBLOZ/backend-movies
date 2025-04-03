from fastapi import APIRouter, Depends
from sqlmodel import Session
from db import get_session
from controlers import CommentController, CommentCreate, CommentResponse
from auth import authenticator

# Crear router para comentarios
comment_router = APIRouter(
    prefix="/movies",
    tags=["comments"],
    responses={404: {"description": "Movie or User not found"}}
)

@comment_router.get(
    "/{id}/comments",
    summary="Obtener comentarios de una película",
    description="""
    Devuelve una lista con todos los comentarios asociados a la película con el id especificado.
    
    Incluye información del usuario que realizó cada comentario y el análisis de sentimiento.
    """,
    response_model=list[CommentResponse]
)
def get_comments_by_movie(id: int, db: Session = Depends(get_session)):
    """
    Devuelve una lista con todos los comentarios de la película con el id especificado.
    """
    return CommentController.get_comments_by_movie(id, db)

@comment_router.post(
    "/{id}/comments", 
    status_code=201,
    summary="Añadir comentario a una película",
    description="""
    Añade un nuevo comentario a la película con el id especificado.
    
    Requiere autenticación con token JWT.
    El comentario debe contener un texto y el ID del usuario que lo realiza.
    El sistema analizará automáticamente el sentimiento del comentario utilizando
    un modelo de aprendizaje automático para clasificarlo como positivo, negativo o neutro.
    """,
    response_model=CommentResponse
)
async def add_comment(
    id: int, 
    comment: CommentCreate, 
    db: Session = Depends(get_session),
    auth: dict = Depends(authenticator)
) -> CommentResponse:
    """
    Añade un nuevo comentario a la película con el id especificado.
    """
    return await CommentController.add_comment(id, comment, db, auth)