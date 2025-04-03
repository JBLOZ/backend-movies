import os
import json
import random
from sqlmodel import SQLModel, create_engine, Session, select, func
from contextlib import contextmanager
from .models import User, Movie, Comment
from utils import get_logger

logger = get_logger("db")

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod").lower()
# Configurar logger


# Leer la URL de conexión desde el entorno; si no se define, usar la de localhost
DB_URL = os.getenv("DB_URL", "mysql+pymysql://user:password@db/movies")
engine = create_engine(DB_URL)


if ENVIRONMENT == "dev":
    # Rutas a los archivos JSON
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    USERS_JSON = os.path.join(DATA_DIR, 'users.json')
    MOVIES_JSON = os.path.join(DATA_DIR, 'movies.json')
    COMMENTS_JSON = os.path.join(DATA_DIR, 'comments.json')

def create_db_and_tables():
    """Crea las tablas en la base de datos."""
    logger.debug("Creando tablas en la base de datos...")
    SQLModel.metadata.create_all(engine)
    logger.info("Tablas creadas exitosamente")

def drop_db_and_tables():
    """Elimina todas las tablas de la base de datos."""
    logger.warning("¡ELIMINANDO todas las tablas de la base de datos!")
    SQLModel.metadata.drop_all(engine)
    logger.info("Tablas eliminadas")


# For use with 'with' statement
@contextmanager
def get_session_context():
    """Contexto para usar en bloques 'with'."""
    with Session(engine) as session:
        yield session

# For use with FastAPI dependencies
def get_session():
    """Generador de sesiones para usar con dependencias de FastAPI."""
    with Session(engine) as session:
        yield session

def seed_default_data():
    """
    Inicializa la base de datos con datos desde archivos JSON si está vacía.
    
    Esta función comprueba si la base de datos tiene datos. Si está vacía,
    carga los datos desde los archivos JSON predefinidos.
    """
    with Session(engine) as session:
        # Comprobar si ya hay datos
        user_count = session.exec(select(func.count()).select_from(User)).one()
        movie_count = session.exec(select(func.count()).select_from(Movie)).one()
        
        if user_count > 0 and movie_count > 0:
            logger.info(f"Base de datos ya inicializada: {user_count} usuarios, {movie_count} películas")
            return
        
        # Crear usuarios, películas y comentarios
        logger.debug("Inicializando la base de datos con datos desde JSON...")
        
        # 1. Crear usuarios desde JSON
        users = load_users_from_json(session)
        
        # 2. Crear películas desde JSON
        movies = load_movies_from_json(session)
        
        # 3. Crear comentarios generados
        if users and movies:
            generate_comments(session, users, movies)
            
        logger.debug("Base de datos inicializada con datos de JSON")

def load_users_from_json(session):
    """
    Carga usuarios desde el archivo JSON a la base de datos.
    
    Args:
        session: Sesión de base de datos activa
        
    Returns:
        list: Lista de usuarios creados
    """
    from auth.password import hash_password
    
    logger.debug(f"Cargando usuarios desde {USERS_JSON}")
    
    try:
        with open(USERS_JSON, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
            
        users = []
        for data in user_data:
            user = User(
                username=data["username"],
                email=data["email"],
                password=hash_password(data["password"])
            )
            users.append(user)
        
        session.add_all(users)
        session.commit()
        
        # Actualizar los objetos con los IDs asignados
        for user in users:
            session.refresh(user)
        
        logger.debug(f"Creados {len(users)} usuarios desde user.json")
        return users
        
    except Exception as e:
        logger.error(f"Error al cargar usuarios desde JSON: {e}")
        return []

def load_movies_from_json(session):
    """
    Carga películas desde el archivo JSON a la base de datos.
    
    Args:
        session: Sesión de base de datos activa
        
    Returns:
        list: Lista de películas creadas
    """
    logger.debug(f"Cargando películas desde {MOVIES_JSON}")
    
    try:
        with open(MOVIES_JSON, 'r', encoding='utf-8') as f:
            movie_data = json.load(f)
            
        movies = []
        for data in movie_data:
            movie = Movie(
                title=data["title"],
                director=data["director"],
                year=data["year"],
                genre=data["genre"]
            )
            movies.append(movie)
        
        session.add_all(movies)
        session.commit()
        
        # Actualizar los objetos con los IDs asignados
        for movie in movies:
            session.refresh(movie)
        
        logger.debug(f"Creadas {len(movies)} películas desde movie.json")
        return movies
        
    except Exception as e:
        logger.error(f"Error al cargar películas desde JSON: {e}")
        return []

def generate_comments(session, users, movies):
    """
    Genera comentarios aleatorios usando las plantillas del archivo JSON.
    
    Args:
        session: Sesión de base de datos activa
        users: Lista de usuarios para relacionar con los comentarios
        movies: Lista de películas para relacionar con los comentarios
    """
    logger.debug(f"Generando comentarios aleatorios usando plantillas de {COMMENTS_JSON}")
    
    try:
        with open(COMMENTS_JSON, 'r', encoding='utf-8') as f:
            comment_templates = json.load(f)
        
        positive_comments = comment_templates.get("positive", [])
        negative_comments = comment_templates.get("negative", [])
        neutral_comments = comment_templates.get("neutral", [])
        
        if not positive_comments or not negative_comments or not neutral_comments:
            logger.error("Formato incorrecto en el archivo de comentarios")
            return []
        
        comments = []
        
        # Asegurar que cada película tenga al menos un comentario
        for movie in movies:
            user = random.choice(users)
            comment_type = random.choice(["positive", "negative", "neutral"])
            
            if comment_type == "positive":
                text = random.choice(positive_comments)
                sentiment = "positive"
            elif comment_type == "negative":
                text = random.choice(negative_comments)
                sentiment = "negative"
            else:
                text = random.choice(neutral_comments)
                sentiment = "neutral"
            
            comment = Comment(
                movie_id=movie.id,
                user_id=user.id,
                text=text,
                sentiment=sentiment
            )
            comments.append(comment)
        
        # Añadir algunos comentarios adicionales aleatorios
        for _ in range(75):  # Crear 75 comentarios adicionales
            movie = random.choice(movies)
            user = random.choice(users)
            
            comment_type = random.choice(["positive", "negative", "neutral"])
            
            if comment_type == "positive":
                text = random.choice(positive_comments)
                sentiment = "positive"
            elif comment_type == "negative":
                text = random.choice(negative_comments)
                sentiment = "negative"
            else:
                text = random.choice(neutral_comments)
                sentiment = "neutral"
            
            comment = Comment(
                movie_id=movie.id,
                user_id=user.id,
                text=text,
                sentiment=sentiment
            )
            comments.append(comment)
        
        # Guardar comentarios en la base de datos
        session.add_all(comments)
        session.commit()
        
        logger.debug(f"Generados {len(comments)} comentarios aleatorios")
        return comments
    
    except Exception as e:
        logger.error(f"Error al generar comentarios: {e}")
        return []
