# src/auth/jwt.py
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from utils import get_logger

logger = get_logger("jwt_auth")

SECRET_KEY = "mi_clave_secreta"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class JWTBearer(HTTPBearer):
    """
    Clase para verificar y validar tokens JWT en las peticiones HTTP.
    
    Esta clase extiende HTTPBearer de FastAPI y se encarga de verificar que el token JWT
    proporcionado en el encabezado de autorización sea válido y no haya expirado.
    """
    
    async def __call__(self, request: Request):
        """
        Verifica el token JWT en el encabezado de autorización de la petición.
        
        Args:
            request (Request): Petición HTTP entrante
            
        Returns:
            dict: Payload decodificado del token JWT
            
        Raises:
            HTTPException: Si el token no es válido o ha expirado (403)
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            token = credentials.credentials
            try:
                # Se decodifica el token; si falla se lanzará una excepción
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                return payload
            except jwt.PyJWTError:
                logger.warning(f"Token JWT inválido o expirado")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token JWT inválido o expirado"
                )
        else:
            logger.warning(f"Credenciales no válidas")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Credenciales no válidas"
            )

def create_jwt_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Crea un token JWT con los datos proporcionados.
    
    Args:
        data (dict): Datos a incluir en el token (claims)
        expires_delta (timedelta, optional): Tiempo de expiración personalizado.
            Si no se proporciona, se usa el valor predeterminado ACCESS_TOKEN_EXPIRE_MINUTES.
            
    Returns:
        str: Token JWT generado
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    logger.debug(f"Token data creado por el usuario: {data['username']}")
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Instancia de JWTBearer para ser usada como dependencia en los endpoints
authenticator = JWTBearer()
