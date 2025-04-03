backend-jbl42
├── DEPENDENCIES.md
├── Dockerfile
├── Dockerfile.dev
├── Dockerfile.inference
├── Dockerfile.inference.dev
├── ENDPOINTS.md
├── README.md
├── docker-compose.yml
├── docs
│   └── uml.svg
├── estructura.md
├── logs
│   └── inference.log
├── postman_collection.json
├── requirements.inference.txt
├── requirements.txt
├── scripts
│   ├── inference_run.sh
│   ├── run.sh
│   └── wait-for-it.sh
├── src
│   ├── __pycache__
│   │   └── main.cpython-312.pyc
│   ├── auth
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── jwt.cpython-312.pyc
│   │   │   └── password.cpython-312.pyc
│   │   ├── jwt.py
│   │   └── password.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── db.cpython-312.pyc
│   │   │   └── models.cpython-312.pyc
│   │   ├── db.py
│   │   └── models.py
│   ├── ia
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── inference_service.cpython-312.pyc
│   │   │   └── sentiment_analysis.cpython-312.pyc
│   │   ├── inference_service.py
│   │   └── sentiment_analysis.py
│   └── main.py
└── tests
    ├── __pycache__
    │   ├── test_comments.cpython-313.pyc
    │   ├── test_movies.cpython-313.pyc
    │   └── test_users.cpython-313.pyc
    ├── test_comments.py
    ├── test_movies.py
    └── test_users.py