from pydantic import BaseModel

class FavoritoCreate(BaseModel):
    movie_id: int

class AvaliacaoCreate(BaseModel):
    movie_id: int
    rating: float
    comment: str = None

class ComentarioCreate(BaseModel):
    movie_id: int
    username: str = "Usuário Demo"
    comment: str