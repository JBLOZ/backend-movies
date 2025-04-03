from typing import Any
from fastapi import HTTPException, status, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from db import User, get_session
from auth import verify_password, create_jwt_token
from utils import get_logger

logger = get_logger("auth_controller")

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthController:
    @staticmethod
    async def login(
        login_data: LoginRequest, 
        db: Session = Depends(get_session)
    ) -> dict[str, Any]:
        """
        Endpoint de autenticación que valida las credenciales y devuelve un token JWT.
        """
        user = db.exec(select(User).where(User.username == login_data.username)).first()
        
        if not user or not verify_password(login_data.password, user.password):
            logger.warning(f"Intento de inicio de sesión fallido para el usuario: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
            
        token_data = {
            "sub": str(user.id),
            "username": user.username
        }
        logger.debug(f"Token data: {token_data}")
        token = create_jwt_token(token_data)

        logger.debug(f"Usuario {user.id} autenticado correctamente")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username
        }