"""
Paquete de controladores para la aplicación de películas.

Este paquete contiene todos los controladores que implementan la lógica de negocio
para manipular los diferentes recursos de la aplicación (usuarios, películas, comentarios, etc.)
y definen las rutas de la API.

Cada controlador tiene su propio router que se exporta desde este módulo.
"""

from .user_controller import UserController, UserCreate, UserResponse
from .movie_controller import MovieController, MovieCreate
from .comment_controller import CommentController, CommentCreate, CommentResponse
from .auth_controller import AuthController, LoginRequest

# Para facilitar la importación en el archivo main.py
__all__ = ['UserController', 'UserCreate', 'UserResponse', 'MovieController', 'MovieCreate', 'CommentController', 'AuthController', 'CommentCreate', 'CommentResponse','LoginRequest']