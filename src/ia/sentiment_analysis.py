from utils import get_logger
import random
import requests
import os

logger = get_logger("sentiment_analysis")

class SentimentModel:
    """
    Clase para el análisis de sentimientos de textos.
    
    Esta clase proporciona métodos para analizar el sentimiento de textos utilizando
    un servicio de inferencia externo que implementa el modelo de análisis.
    Si el servicio no está disponible, se utiliza una selección aleatoria como respaldo.
    """
    
    @staticmethod
    def analyze_sentiment(text):
        """
        Analiza el sentimiento del texto proporcionado.
        
        Este método envía una petición al servicio de inferencia para obtener un análisis
        de sentimiento del texto. Intenta conectarse a diferentes URLs en caso de fallo.
        Si ninguna conexión tiene éxito, se devuelve una clasificación aleatoria como respaldo.
        
        Args:
            text (str): Texto a analizar
            
        Returns:
            str: Etiqueta de sentimiento ('positive', 'negative', 'neutral')
        """
        try:
            inference_host = os.environ.get("INFERENCE_HOST", "host.docker.internal")
            url = f"http://{inference_host}:8001/predict"

            text_with_context = f"Mi opinión sobre esta película: {text}"
            logger.debug(f"Se manda al modelo: '{text_with_context}'")
            
            logger.debug(f"Sending request to: {url}")
            response = requests.post(url, json={"text": text_with_context}, timeout=5)
            if response.status_code == 200:
                result = response.json()
                return result["label"]
        except Exception as e:
            logger.error(f"Error connecting to inference service at {url}: {e}")
        
        # Fallback to random if inference service fails
        labels = ["positive", "negative", "neutral"]
        random_choice = random.choice(labels)
        logger.warning(f"Using random fallback: {random_choice}")
        return random_choice