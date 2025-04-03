"""
Paquete de routers para la aplicación de películas.

Este paquete contiene todos los routers que definen los endpoints 
de la API, separando las rutas por recursos.

Módulos:
- user_router: Endpoints relacionados con usuarios
- movie_router: Endpoints relacionados con películas 
- comment_router: Endpoints relacionados con comentarios
- auth_router: Endpoints relacionados con autenticación
"""

from .user_router import user_router
from .movie_router import movie_router
from .comment_router import comment_router
from .auth_router import auth_router

# Para acceso directo desde routers.*
__all__ = ['user_router', 'movie_router', 'comment_router', 'auth_router']