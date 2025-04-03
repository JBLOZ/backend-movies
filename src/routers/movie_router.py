from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Any
from db import get_session
from auth import authenticator
from controlers import MovieController, MovieCreate

# Crear router para películas
movie_router = APIRouter(
    prefix="/movies",
    tags=["movies"],
    responses={404: {"description": "Movie not found"}}
)

@movie_router.get(
    "",
    summary="Listar todas las películas",
    description="""
    Devuelve una lista con todas las películas registradas en la base de datos.
    Por motivos de eficiencia, solo se incluyen los campos id y título en la respuesta.
    """
)
def list_movies(db: Session = Depends(get_session)) -> list[dict[str, Any]]:
    """
    Devuelve una lista con todas las películas registradas en la base de datos.
    """
    return MovieController.list_movies(db)

@movie_router.get(
    "/search",
    summary="Buscar películas por título",
    description="""
    Busca películas que contengan el texto especificado en su título.
    
    La búsqueda es insensible a mayúsculas/minúsculas y busca coincidencias parciales.
    Por ejemplo, buscar "star" encontrará "Star Wars", "Starship Troopers", etc.
    """
)
def search_movies(title: str = Query(...), db: Session = Depends(get_session)) -> list[dict[str, Any]]:
    """
    Busca películas por título.
    """
    return MovieController.search_movies(title, db)

@movie_router.get(
    "/{id}",
    summary="Obtener detalles de una película",
    description="""
    Devuelve los datos completos de la película con el id especificado.
    
    Incluye información como título, director, año y género.
    """
)
def get_movie(id: int, db: Session = Depends(get_session)) -> dict[str, Any]:
    """
    Devuelve los datos de la película con el id especificado.
    """
    return MovieController.get_movie(id, db)

@movie_router.post(
    "", 
    status_code=201,
    summary="Crear una nueva película",
    description="""
    Añade una nueva película a la base de datos.
    
    Requiere autenticación con token JWT.
    Requiere proporcionar todos los datos obligatorios de la película: título,
    director, año y género.
    """
)
async def create_movie(
    movie: MovieCreate, 
    db: Session = Depends(get_session),
    _: dict = Depends(authenticator)
) -> dict[str, Any]:
    """
    Crea una nueva película en la base de datos.
    """
    return await MovieController.create_movie(movie, db)

@movie_router.delete(
    "/{id}",
    summary="Eliminar una película",
    description="""
    Elimina la película con el id especificado de la base de datos.
    
    Requiere autenticación con token JWT.
    Esta operación también eliminará todos los comentarios asociados a la película.
    Es una operación irreversible.
    """
)
async def delete_movie(
    id: int, 
    db: Session = Depends(get_session),
    _: dict = Depends(authenticator)
) -> dict[str, str]:
    """
    Elimina la película con el id especificado de la base de datos.
    """
    return await MovieController.delete_movie(id, db)