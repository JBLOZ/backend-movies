from typing import Any
from fastapi import FastAPI, HTTPException
import torch
import random
from contextlib import asynccontextmanager
from transformers import pipeline
from pydantic import BaseModel
from utils import get_logger  # Importar directamente la función get_logger del módulo correcto  

logger = get_logger("inference_service")
# Variable global para almacenar el pipeline
model_pipeline = None

# Modelos de datos para la API
class PredictionRequest(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    label: str
    score: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_pipeline
    # Initialize sentiment analysis with fallback
    try:
        device = 0 if torch.cuda.is_available() else -1

        logger.info(f"Using device: {'cuda' if device == 0 else 'cpu'}")

        
        # Usar un modelo más preciso para español
        model_pipeline = pipeline(
            "text-classification", 
            model="pysentimiento/robertuito-sentiment-analysis",  
            device=device
        )
        logger.info("Successfully loaded improved Spanish sentiment analysis model (pysentimiento/robertuito)")
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        model_pipeline = None
    
    # Este yield debe estar fuera del bloque try-except
    yield
    
    # Cleanup
    if model_pipeline:
        del model_pipeline
        logger.debug("Model pipeline released")


# Create FastAPI app for the inference service
app = FastAPI(
    title="Servicio de Análisis de Sentimiento",
    description="API para analizar el sentimiento de textos en español, especializada en reseñas de películas",
    version="1.0.0",
    lifespan=lifespan
)

@app.post(
    "/predict", 
    response_model=PredictionResponse,
    summary="Analizar sentimiento de un texto",
    description="""
    Analiza el sentimiento de un texto en español utilizando un modelo de aprendizaje automático.
    
    El modelo utilizado es 'pysentimiento/robertuito-sentiment-analysis', especializado en textos en español.
    El sistema añade automáticamente contexto relacionado con películas para mejorar la precisión del análisis.
    """
)
async def predict(data: PredictionRequest) -> dict[str, Any]:
    """
    Endpoint para analizar el sentimiento de un texto en español.
    
    Utiliza un modelo preentrenado de análisis de sentimientos para clasificar
    el texto proporcionado como positivo, negativo o neutro, añadiendo contexto
    específico de reseñas de películas.
    
    Args:
        data (PredictionRequest): Objeto que contiene el campo 'text' con el texto a analizar
        
    Returns:
        dict: Contiene 'label' (etiqueta de sentimiento) y 'score' (confianza de la predicción)
        
    Raises:
        HTTPException: Si no se proporciona el campo 'text' (400)
    """
    original_text = data.text
    logger.info(f"Texto recibido: '{original_text}'")
    
    # Añadir contexto de película al texto para que el modelo lo entienda mejor
    
    
    try:
        if not model_pipeline:
            # Random fallback if model isn't loaded
            labels = ["positive", "negative", "neutral"]
            random_label = random.choice(labels)
            logger.warning(f"Modelo no cargado, retornando etiqueta aleatoria {random_label}")
            return {"label": random_label, "score": -1}
        
        # Usar el texto con contexto para la predicción
        result = model_pipeline(original_text)
        prediction = result[0]
        
        # Mapear las etiquetas del modelo español a las etiquetas estándar
        # Este modelo usa etiquetas en inglés (POS, NEG, NEU)
        label_mapping = {
            "POS": "positive",
            "NEG": "negative",
            "NEU": "neutral"
        }
        
        label = prediction["label"]
        mapped_label = label_mapping.get(label, label).lower()
        
        logger.info(f"Resultado de la prediccion: {prediction}, etiqueta: {mapped_label}")
        return {"label": mapped_label, "score": prediction["score"]}
    except Exception as e:
        # Random fallback if prediction fails
        labels = ["positive", "negative", "neutral"]
        random_label = random.choice(labels)
        logger.error(f"Error en la prediccion: {e}, retornando etiqueta aleatoria: {random_label}")
        return {"label": random_label, "score": -1}

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar estado del servicio",
    description="""
    Endpoint de verificación de salud del servicio de análisis de sentimiento.
    
    Comprueba si el servicio está funcionando correctamente y si el modelo 
    de análisis de sentimiento se ha cargado con éxito.
    """
)
async def health() -> dict[str, Any]:
    """
    Endpoint de comprobación de salud del servicio.
    
    Permite verificar si el servicio está funcionando y si el modelo 
    de análisis de sentimiento se ha cargado correctamente.
    
    Returns:
        dict: Estado del servicio y si el modelo está cargado
    """
    return {"status": "ok", "model_loaded": model_pipeline is not None}
