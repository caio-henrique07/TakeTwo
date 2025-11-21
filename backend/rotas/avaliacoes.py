from fastapi import APIRouter
from database import get_db
from models import Avaliacao
from schemas import AvaliacaoCreate
from rotas.filmes import fetch_tmdb

router = APIRouter(prefix="/ratings", tags=["Avaliações"])

@router.get("")
async def get_ratings():
    """Listar avaliações"""
    db = next(get_db())
    avaliacoes = db.query(Avaliacao).all()
    
    movies = []
    for aval in avaliacoes:
        movie_data = await fetch_tmdb(f"/movie/{aval.movie_id}")
        movies.append({
            "id": aval.id,
            "movie": movie_data,
            "rating": aval.rating,
            "comment": aval.comment,
            "created_at": aval.created_at
        })
    return movies

@router.post("")
async def add_rating(avaliacao: AvaliacaoCreate):
    """Adicionar avaliação"""
    db = next(get_db())
    
    existing = db.query(Avaliacao).filter(Avaliacao.movie_id == avaliacao.movie_id).first()
    if existing:
        existing.rating = avaliacao.rating
        existing.comment = avaliacao.comment
        db.commit()
        return {"message": "Avaliação atualizada"}
    
    new_rating = Avaliacao(
        movie_id=avaliacao.movie_id,
        rating=avaliacao.rating,
        comment=avaliacao.comment
    )
    db.add(new_rating)
    db.commit()
    return {"message": "Avaliação adicionada"}