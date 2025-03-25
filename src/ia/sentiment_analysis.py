from fastapi import FastAPI, HTTPException
import logging
import random
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='logs/inference.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SentimentModel:
    @staticmethod
    def analyze_sentiment(text):
        """Static method to analyze sentiment - calls the inference service"""
        try:
            # Try to call the inference service
            response = requests.post("http://inference_service:8001/predict", 
                                    json={"text": text})
            if response.status_code == 200:
                result = response.json()
                return result["label"]
            else:
                logging.error(f"Error calling inference service: {response.status_code}")
        except Exception as e:
            logging.error(f"Exception calling inference service: {e}")
        
        # Fallback to random if inference service fails
        labels = ["positive", "negative", "neutral"]
        return random.choice(labels)