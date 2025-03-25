# src/auth/jwt.py
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "mi_clave_secreta"  # Cambia esto por una clave segura en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            token = credentials.credentials
            try:
                # Se decodifica el token; si falla se lanzará una excepción
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                # Puedes agregar validaciones adicionales sobre el payload si fuera necesario
                return payload
            except jwt.PyJWTError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token JWT inválido o expirado"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Credenciales no válidas"
            )

def create_jwt_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

authenticator = JWTBearer()
