backend-jbl42
├── DEPENDENCIES.md
├── Dockerfile
├── Dockerfile.dev
├── Dockerfile.inference
├── ENDPOINTS.md
├── README.md
├── docker-compose.yml
├── docs
│   └── uml.svg
├── estructura.md
├── logs
│   └── movies.log
├── postman_collection.json
├── requirements.inference.txt
├── requirements.txt
├── salida.txt
├── scripts
│   ├── inference_run.sh
│   ├── run.sh
│   └── wait-for-it.sh
├── src
│   ├── __pycache__
│   │   ├── main.cpython-312.pyc
│   │   └── main.cpython-313.pyc
│   ├── auth
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-313.pyc
│   │   │   ├── jwt.cpython-313.pyc
│   │   │   └── password.cpython-313.pyc
│   │   ├── jwt.py
│   │   └── password.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── __init__.cpython-313.pyc
│   │   │   ├── db.cpython-312.pyc
│   │   │   ├── db.cpython-313.pyc
│   │   │   ├── models.cpython-312.pyc
│   │   │   └── models.cpython-313.pyc
│   │   ├── db.py
│   │   └── models.py
│   ├── ia
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── __init__.cpython-313.pyc
│   │   │   ├── sentiment_analysis.cpython-312.pyc
│   │   │   └── sentiment_analysis.cpython-313.pyc
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