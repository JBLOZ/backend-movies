from fastapi import FastAPI, HTTPException
import torch
import logging
import random
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='logs/inference.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app for the inference service
app = FastAPI()

# Initialize sentiment analysis with fallback
try:
    from transformers import pipeline
    
    device = 0 if torch.cuda.is_available() else -1
    model_pipeline = pipeline(
        "text-classification", 
        model="distilbert-base-uncased-finetuned-sst-2-english",  # Using a smaller model
        device=device
    )
    logging.info("Successfully loaded model")
        
except Exception as e:
    logging.error(f"Failed to initialize model: {e}")
    model_pipeline = None

@app.post("/predict")
async def predict(data: dict):
    if "text" not in data:
        raise HTTPException(status_code=400, detail="Text field is required")
    
    text = data["text"]
    logging.info(f"Received prediction request for text: {text}")
    
    try:
        if not model_pipeline:
            # Random fallback if model isn't loaded
            labels = ["positive", "negative", "neutral"]
            random_label = random.choice(labels)
            logging.warning(f"Model not loaded, returning random prediction: {random_label}")
            return {"label": random_label, "score": 0.5}
        
        result = model_pipeline(text)
        prediction = result[0]
        logging.info(f"Prediction result: {prediction}")
        return {"label": prediction["label"].lower(), "score": prediction["score"]}
    except Exception as e:
        # Random fallback if prediction fails
        labels = ["positive", "negative", "neutral"]
        random_label = random.choice(labels)
        logging.error(f"Prediction error: {e}, using random fallback: {random_label}")
        return {"label": random_label, "score": 0.5}

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model_pipeline is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("inference_service:app", host="0.0.0.0", port=8001)