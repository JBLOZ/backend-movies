import os
from utils import get_logger
from contextlib import asynccontextmanager
from fastapi import FastAPI
from db import get_session, create_db_and_tables, drop_db_and_tables, seed_default_data
from routers import user_router, movie_router, comment_router, auth_router


# Obtener logger configurado para la aplicación principal
logger = get_logger("movies_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de contexto que controla el ciclo de vida de la aplicación.
    
    Se ejecuta al iniciar y finalizar la aplicación, permitiendo realizar
    tareas de inicialización y limpieza como la configuración de la base de datos.
    
    Args:
        app (FastAPI): Instancia de la aplicación FastAPI
    """
    # Inicializar la base de datos
    try:
        logger.info("Inicializando la base de datos...")
        
        if os.getenv("ENVIRONMENT", "prod").lower() == "dev":
            logger.warning("Perfil de desarrollo detectado: recreando tablas y datos")
            # En desarrollo: borrar tablas primero (para usar descomentar), luego crearlas de nuevo y cargar datos
            # drop_db_and_tables()
            create_db_and_tables()
            # Cargar los datos predeterminados en modo dev
            seed_default_data()
            logger.info("Base de datos reinicializada correctamente para desarrollo")
        else:
            logger.info("Perfil de producción detectado: manteniendo datos existentes")
            # En producción solo garantizamos que existan las tablas, pero no modificamos datos
            create_db_and_tables()
            logger.info("Base de datos verificada correctamente para producción")
        
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        raise
    
    yield
    
    # Tareas de limpieza al cerrar la app
    logger.info("Aplicación terminando...")

app = FastAPI(
    title="Movies API",
    description="API para gestionar películas, usuarios y comentarios",
    version="1.0.0",
    lifespan=lifespan
)
# Incluir todos los routers directamente desde los controladores
app.include_router(user_router)
app.include_router(movie_router)
app.include_router(comment_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    """
    Endpoint raíz que proporciona información básica de la API.
    """
    return {
        "message": "Bienvenido a la API de Películas",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": [
            "/users", 
            "/movies",
            "/login"
        ]
    }
