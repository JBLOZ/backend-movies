from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

# Database entities (SQLModel)
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(..., max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    comments: List["Comment"] = Relationship(back_populates="user")

class Movie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(..., max_length=255)
    director: str = Field(..., max_length=255)
    year: int = Field(...)
    genre: str = Field(..., max_length=100)
    comments: List["Comment"] = Relationship(back_populates="movie")

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    movie_id: int = Field(..., foreign_key="movie.id")
    user_id: int = Field(..., foreign_key="user.id")
    text: str = Field(...)
    sentiment: str = Field(...)
    movie: Optional[Movie] = Relationship(back_populates="comments")
    user: Optional[User] = Relationship(back_populates="comments")



