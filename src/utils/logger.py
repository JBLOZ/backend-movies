"""
Módulo de configuración centralizada de logging.

Este módulo proporciona funciones para configurar y obtener loggers
con una configuración consistente en toda la aplicación.
"""

import os
import logging

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado con un formato y nivel consistente.
    
    Esta función configura un nuevo logger o devuelve uno existente con:
    - Un nivel basado en la variable de entorno ENVIRONMENT
    - Un handler para mostrar logs en la consola
    - Un handler para escribir logs en un archivo
    
    Args:
        name (str): Nombre del logger (normalmente nombre del módulo)
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Detectar el perfil de ejecución (dev o prod)
    environment = os.getenv("ENVIRONMENT", "prod").lower()
    
    # Crear un logger específico
    logger = logging.getLogger(name)
    
    # Evitar configurar el logger múltiples veces
    if logger.hasHandlers():
        return logger
    
    # Configurar el nivel de logging según el entorno
    if environment == "dev":
        logger.setLevel(logging.DEBUG)
    else:  # producción
        logger.setLevel(logging.WARNING)
    
    # Configurar el handler para la consola
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('      %(levelname)-7s %(message)s'))
    
    # Configurar el handler para el archivo
    file_handler = logging.FileHandler('logs/movies.log', mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Añadir los handlers al logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    
    # Registrar la configuración inicial
    logger.info(f"Logger '{name}' configurado - Perfil: {environment}")
    
    return logger