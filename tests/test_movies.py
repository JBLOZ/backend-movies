import unittest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from auth import authenticator
from db import get_session, Movie

class TestMoviesEndpoints(unittest.TestCase):

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
                Movie(id=1, title="Inception", director="Christopher Nolan", year=2010, genre="Sci-Fi"),
                Movie(id=2, title="The Matrix", director="Lana Wachowski, Lilly Wachowski", year=1999, genre="Sci-Fi"),
                Movie(id=3, title="Interstellar", director="Christopher Nolan", year=2014, genre="Sci-Fi")
            ])
            session.commit()

    def test_get_movies_empty(self):
        response = self.client.get("/movies")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 0)

    def test_get_movies(self):
        self.seed_db()
        response = self.client.get("/movies")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 3)
        movies = response.json()
        self.assertEqual(movies[0]['id'], 1)
        self.assertEqual(movies[0]['title'], 'Inception')
        self.assertEqual(movies[1]['id'], 2)
        self.assertEqual(movies[1]['title'], 'The Matrix')
        self.assertEqual(movies[2]['id'], 3)
        self.assertEqual(movies[2]['title'], 'Interstellar')

    def test_get_movie(self):
        self.seed_db()
        response = self.client.get("/movies/1")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)
        movie = response.json()
        self.assertEqual(movie['title'], 'Inception')
        self.assertEqual(movie['director'], 'Christopher Nolan')
        self.assertEqual(movie['year'], 2010)
        self.assertEqual(movie['genre'], 'Sci-Fi')
    
    def test_get_movie_not_found(self):
        self.seed_db()
        response = self.client.get("/movies/4")
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), {"detail": "Movie not found"})

    def test_search_movie(self):
        self.seed_db()
        response = self.client.get("/movies/search?title=cept")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 1)
        movie = response.json()[0]
        self.assertEqual(movie['id'], 1)
        self.assertEqual(movie['title'], 'Inception')

    def test_search_movie_no_results(self):
        self.seed_db()
        response = self.client.get("/movies/search?title=Tenet")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 0)

    def test_create_movie(self):
        response = self.client.post("/movies", json={"title": "Tenet", "director": "Christopher Nolan", "year": 2020, "genre": "Sci-Fi"})
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.json(), dict)
        movie = response.json()
        self.assertEqual(movie['id'], 1)
        self.assertEqual(movie['title'], 'Tenet')
        self.assertEqual(movie['director'], 'Christopher Nolan')
        self.assertEqual(movie['year'], 2020)
        self.assertEqual(movie['genre'], 'Sci-Fi')
        movie = self.session.get(Movie, 1)
        self.assertIsNotNone(movie)
        self.assertEqual(movie.title, 'Tenet')
        self.assertEqual(movie.director, 'Christopher Nolan')
        self.assertEqual(movie.year, 2020)
        self.assertEqual(movie.genre, 'Sci-Fi')

    def test_create_movie_missing_fields(self):
        response = self.client.post("/movies", json={"title": "Tenet", "director": "Christopher Nolan", "year": 2020})
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/movies", json={"title": "Tenet", "director": "Christopher Nolan", "genre": "Sci-Fi"})
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/movies", json={"title": "Tenet", "year": 2020, "genre": "Sci-Fi"})
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/movies", json={"director": "Christopher Nolan", "year": 2020, "genre": "Sci-Fi"})
        self.assertEqual(response.status_code, 422)

    def test_delete_movie(self):
        self.seed_db()
        response = self.client.delete("/movies/1")
        self.assertEqual(response.status_code, 200)
        movie = self.session.get(Movie, 1)
        self.assertIsNone(movie)
    
    def test_delete_movie_not_found(self):
        self.seed_db()
        response = self.client.delete("/movies/4")
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), {"detail": "Movie not found"})
    