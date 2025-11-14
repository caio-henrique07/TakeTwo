# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
import httpx

TMDB_API_KEY = "995fb88d7c5e211d67d59faae0b52cb3"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Favorito(Base):
    __tablename__ = "favoritos"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Avaliacao(Base):
    __tablename__ = "avaliacoes"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, index=True)
    rating = Column(Float)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class FavoritoCreate(BaseModel):
    movie_id: int

class AvaliacaoCreate(BaseModel):
    movie_id: int
    rating: float
    comment: str | None = None

app = FastAPI(title="TakeTwo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def fetch_tmdb(endpoint: str, extra_params: dict | None = None):
    """Centraliza chamadas para TMDb"""
    url = f"{TMDB_BASE_URL}{endpoint}"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR"
    }

    if extra_params:
        params.update(extra_params)

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        return res.json()

@app.get("/")
async def root():
    return {"message": "TakeTwo API - Funcionando!"}

@app.get("/movies/popular")
async def get_popular_movies(page: int = 1):
    return await fetch_tmdb("/movie/popular", {"page": page})

@app.get("/movies/search")
async def search_movies(q: str, page: int = 1):
    data = await fetch_tmdb("/search/movie", {"query": q, "page": page})
    return {"results": data.get("results", [])}

@app.get("/movies/{movie_id}")
async def movie_details(movie_id: int):
    return await fetch_tmdb(f"/movie/{movie_id}")

@app.get("/favorites")
async def get_favorites():
    db = next(get_db())
    favoritos = db.query(Favorito).all()

    result = []
    for fav in favoritos:
        movie_data = await fetch_tmdb(f"/movie/{fav.movie_id}")
        result.append({
            "id": fav.id,
            "movie": movie_data,
            "created_at": fav.created_at
        })
    return result

@app.post("/favorites")
async def add_favorite(favorito: FavoritoCreate):
    db = next(get_db())

    exists = db.query(Favorito).filter_by(movie_id=favorito.movie_id).first()
    if exists:
        raise HTTPException(400, "Já está nos favoritos")

    new = Favorito(movie_id=favorito.movie_id)
    db.add(new)
    db.commit()
    return {"message": "Adicionado aos favoritos"}

@app.delete("/favorites/{movie_id}")
async def remove_favorite(movie_id: int):
    db = next(get_db())
    fav = db.query(Favorito).filter_by(movie_id=movie_id).first()

    if not fav:
        raise HTTPException(404, "Não encontrado nos favoritos")

    db.delete(fav)
    db.commit()
    return {"message": "Removido dos favoritos"}

@app.get("/ratings")
async def get_ratings():
    db = next(get_db())
    avals = db.query(Avaliacao).all()

    result = []
    for aval in avals:
        movie_data = await fetch_tmdb(f"/movie/{aval.movie_id}")
        result.append({
            "id": aval.id,
            "movie": movie_data,
            "rating": aval.rating,
            "comment": aval.comment,
            "created_at": aval.created_at
        })
    return result

@app.post("/ratings")
async def add_rating(avaliacao: AvaliacaoCreate):
    db = next(get_db())

    exists = db.query(Avaliacao).filter_by(movie_id=avaliacao.movie_id).first()
    if exists:
        exists.rating = avaliacao.rating
        exists.comment = avaliacao.comment
        db.commit()
        return {"message": "Avaliação atualizada"}

    new = Avaliacao(
        movie_id=avaliacao.movie_id,
        rating=avaliacao.rating,
        comment=avaliacao.comment
    )
    db.add(new)
    db.commit()
    return {"message": "Avaliação adicionada"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
