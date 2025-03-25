import unittest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from auth import authenticator
from db import get_session, User

class TestUserEndpoints(unittest.TestCase):

    def setUp(self):
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(engine)
        self.session = Session(engine)
        def get_session_override():
            yield self.session
        app.dependency_overrides[get_session] = get_session_override
        
        self.mock_auth = MagicMock()
        self.mock_auth.return_value = True
        self.patcher = patch.object(authenticator, "__call__", self.mock_auth)
        self.patcher.start()

        app.lifespan = AsyncMock(return_value=None)
        self.client = TestClient(app)       
    
    def tearDown(self):
        app.dependency_overrides.clear()
        self.patcher.stop()
    
    def seed_db(self):
        with self.session as session:
            session.add_all([
                User(username="Alice", email="alice@example.com", password="password123"),
                User(username="Bob", email="bob@example.com", password="password456"),
                User(username="Charlie", email="charlie@example.com", password="password789")
            ])
            session.commit()

    def test_get_users_empty(self):
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 0)

    def test_get_users(self):
        self.seed_db()
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 3)
        user = response.json()[0]
        self.assertIsInstance(user, dict)
        self.assertEqual(user, {"id": 1, "username": "Alice"})
        user = response.json()[1]
        self.assertIsInstance(user, dict)
        self.assertEqual(user, {"id": 2, "username": "Bob"})
        user = response.json()[2]
        self.assertIsInstance(user, dict)
        self.assertEqual(user, {"id": 3, "username": "Charlie"})

    def test_get_user(self):
        self.seed_db()
        response = self.client.get("/users/1")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), {"id": 1, "username": "Alice", "email": "alice@example.com"})
    
    def test_get_user_not_found(self):
        self.seed_db()
        response = self.client.get("/users/4")
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), {"detail": "User not found"})