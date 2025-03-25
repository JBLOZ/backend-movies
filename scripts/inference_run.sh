#!/bin/bash
uvicorn ia.inference_service:app --host 0.0.0.0 --port 8001
