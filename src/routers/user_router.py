from fastapi import APIRouter, Depends
from sqlmodel import Session
from db import get_session
from controlers import UserController, UserResponse, UserCreate
from auth import hash_password

# Crear router para usuarios
user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "User not found"}}
)

@user_router.get(
    "",
    response_model=list[dict],
    summary="Listar todos los usuarios",
    description="""
    Devuelve una lista con todos los usuarios registrados en la base de datos.
    Solo se incluyen los campos id y username por razones de seguridad y privacidad.
    """
)
def list_users(db: Session = Depends(get_session)):
    return UserController.list_users(db)

@user_router.get(
    "/{id}",
    response_model=UserResponse,
    summary="Obtener un usuario por ID",
    description="""
    Devuelve los datos del usuario con el id especificado.
    Incluye información como el nombre de usuario y correo electrónico, pero no la contraseña.
    """
)
def get_user(id: int, db: Session = Depends(get_session)):
    return UserController.get_user(id, db)

@user_router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="Crear un nuevo usuario",
    description="""
    Crea un nuevo usuario en la base de datos y devuelve los datos del usuario creado sin la contraseña.
    La contraseña es automáticamente hasheada antes de almacenarse para mayor seguridad.
    Comprueba que el nombre de usuario no exista previamente en el sistema.
    """
)
def create_user(user_data: UserCreate, db: Session = Depends(get_session)):
    return UserController.create_user(user_data, db, hash_password)

@user_router.get(
    "/{id}/comments",
    summary="Obtener comentarios de un usuario",
    description="""
    Devuelve una lista con todos los comentarios realizados por el usuario con el id especificado.
    Incluye información tanto del comentario como de la película a la que se refiere.
    """
)
def get_comments_by_user(id: int, db: Session = Depends(get_session)):
    return UserController.get_comments_by_user(id, db)