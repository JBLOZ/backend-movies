from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Any
from db import get_session
from controlers import AuthController, LoginRequest

# Crear router para autenticación
auth_router = APIRouter(
    tags=["authentication"]
)

@auth_router.post(
    "/login",
    summary="Iniciar sesión",
    description="""
    Endpoint de autenticación que valida las credenciales del usuario y devuelve un token JWT.
    
    El token JWT puede ser utilizado para autenticar solicitudes posteriores a endpoints protegidos.
    El token incluye información básica del usuario como su ID y nombre de usuario.
    """
)
async def login(login_data: LoginRequest, db: Session = Depends(get_session)) -> dict[str, Any]:
    """
    Endpoint de autenticación que valida las credenciales y devuelve un token JWT.
    """
    return await AuthController.login(login_data, db)