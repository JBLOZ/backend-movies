import unittest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, select
from sqlmodel.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from auth import authenticator
from db import get_session, User, Movie, Comment

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
            session.add_all([
                Movie(id=1, title="Inception", director="Christopher Nolan", year=2010, genre="Sci-Fi"),
                Movie(id=2, title="The Matrix", director="Lana Wachowski, Lilly Wachowski", year=1999, genre="Sci-Fi"),
                Movie(id=3, title="Interstellar", director="Christopher Nolan", year=2014, genre="Sci-Fi")
            ])
            session.add_all([
                Comment(text="Great movie", sentiment="positive", movie_id=1, user_id=1),
                Comment(text="Not bad", sentiment="neutral", movie_id=1, user_id=2),
                Comment(text="Awesome movie", sentiment="positive", movie_id=2, user_id=1),
                Comment(text="Hated it", sentiment="negative", movie_id=2, user_id=2),
            ])
            session.commit()

    def test_get_user_comments(self):
        self.seed_db()
        response = self.client.get("/users/2/comments")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 2)
        comments = response.json()
        self.assertEqual(comments[0]['movie_id'], 1)
        self.assertEqual(comments[0]['title'], 'Inception')
        self.assertEqual(comments[0]['user_id'], 2)
        self.assertEqual(comments[0]['username'], 'Bob')
        self.assertEqual(comments[0]['text'], 'Not bad')
        self.assertEqual(comments[0]['sentiment'], 'neutral')
        self.assertEqual(comments[1]['movie_id'], 2)
        self.assertEqual(comments[1]['title'], 'The Matrix')
        self.assertEqual(comments[1]['user_id'], 2)
        self.assertEqual(comments[1]['username'], 'Bob')
        self.assertEqual(comments[1]['text'], 'Hated it')
        self.assertEqual(comments[1]['sentiment'], 'negative')
    
    def test_get_user_comments_user_not_found(self):
        self.seed_db()
        response = self.client.get("/users/4/comments")
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), {"detail": "User not found"})
    
    def test_get_user_comments_empty(self):
        self.seed_db()
        response = self.client.get("/users/3/comments")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 0)

    def test_get_movie_comments(self):
        self.seed_db()
        response = self.client.get("/movies/1/comments")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 2)
        comments = response.json()
        self.assertEqual(comments[0]['movie_id'], 1)
        self.assertEqual(comments[0]['title'], 'Inception')
        self.assertEqual(comments[0]['user_id'], 1)
        self.assertEqual(comments[0]['username'], 'Alice')
        self.assertEqual(comments[0]['text'], 'Great movie')
        self.assertEqual(comments[0]['sentiment'], 'positive')
        self.assertEqual(comments[1]['movie_id'], 1)
        self.assertEqual(comments[1]['title'], 'Inception')
        self.assertEqual(comments[1]['user_id'], 2)
        self.assertEqual(comments[1]['username'], 'Bob')
        self.assertEqual(comments[1]['text'], 'Not bad')
        self.assertEqual(comments[1]['sentiment'], 'neutral')
    
    def test_get_movie_comments_empty(self):
        self.seed_db()
        response = self.client.get("/movies/3/comments")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 0)
    
    def test_get_movie_comments_movie_not_found(self):
        self.seed_db()
        response = self.client.get("/movies/4/comments")
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), {"detail": "Movie not found"})

    def test_add_comment_user_not_found(self):
        self.seed_db()
        response = self.client.post("/movies/1/comments", json={"user_id": 4, "text": "Amazing movie"})
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), {"detail": "User not found"})

    def test_add_comment_movie_not_found(self):
        self.seed_db()
        response = self.client.post("/movies/4/comments", json={"user_id": 2, "text": "Amazing movie"})
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), {"detail": "Movie not found"})

    @patch('ia.SentimentModel.analyze_sentiment')
    def test_add_comment(self, mock_analyze_sentiment):
        mock_analyze_sentiment.return_value = 'sentiment'
        self.seed_db()
        response = self.client.post("/movies/3/comments", json={"user_id": 1, "text": "Amazing movie"})
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.json(), dict)
        comment = response.json()
        self.assertEqual(comment['movie_id'], 3)
        self.assertEqual(comment['user_id'], 1)
        self.assertEqual(comment['username'], 'Alice')
        self.assertEqual(comment['text'], 'Amazing movie')
        self.assertEqual(comment['sentiment'], 'sentiment')
        comment = self.session.exec(select(Comment).where(Comment.user_id == 1, Comment.movie_id == 3)).first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.text, 'Amazing movie')
        self.assertEqual(comment.user.username, 'Alice')
        self.assertEqual(comment.sentiment, 'sentiment')
    
    def test_add_comment_missing_fields(self):
        self.seed_db()
        response = self.client.post("/movies/1/comments", json={"text": "Amazing movie"})
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/movies/1/comments", json={"user_id": 2})
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/movies/1/comments", json={})
        self.assertEqual(response.status_code, 422)

    def test_delete_movie_deletes_comments(self):
        self.seed_db()
        comment = self.session.exec(select(Comment).where(Comment.user_id == 1, Comment.movie_id == 1)).first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.text, 'Great movie')
        response = self.client.delete("/movies/1")
        self.assertEqual(response.status_code, 200)
        comment = self.session.exec(select(Comment).where(Comment.user_id == 1, Comment.movie_id == 1)).first()
        self.assertIsNone(comment)
