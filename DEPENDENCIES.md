# Instrucciones para activar el modelo de análisis de sentimientos de Hugging Face

El modelo de análisis de sentimientos se puede ejecutar en dos versiones: una para CPU y otra para GPU. El modo elegido se determina automáticamente en función de la disponibilidad de la GPU en tu sistema y de las dependencias instaladas.

## Versión para CPU

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers
```

## Versión para GPU:

```bash
pip install torch
pip install transformers
```

Además, deberás comentar esta línea en el archivo `src/ia/sentiment_analysis.py` que fuerza la ejecución en CPU:

```python
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
```

## Comprobación del modelo

Puedes comprobar su funcionamiento ejecutando la función main en `src/ia/sentiment_analysis.py`. 
