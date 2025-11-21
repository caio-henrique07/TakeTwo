from fastapi import APIRouter, HTTPException
from database import get_db
from models import Favorito
from schemas import FavoritoCreate
from rotas.filmes import fetch_tmdb

router = APIRouter(prefix="/favorites", tags=["Favoritos"])

@router.get("")
async def get_favorites():
    """Listar favoritos"""
    db = next(get_db())
    favoritos = db.query(Favorito).all()
    
    movies = []
    for fav in favoritos:
        movie_data = await fetch_tmdb(f"/movie/{fav.movie_id}")
        movies.append({
            "id": fav.id,
            "movie": movie_data,
            "created_at": fav.created_at
        })
    return movies

@router.post("")
async def add_favorite(favorito: FavoritoCreate):
    """Adicionar aos favoritos"""
    db = next(get_db())
    
    existing = db.query(Favorito).filter(Favorito.movie_id == favorito.movie_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Já está nos favoritos")
    
    new_fav = Favorito(movie_id=favorito.movie_id)
    db.add(new_fav)
    db.commit()
    return {"message": "Adicionado aos favoritos"}

@router.delete("/{movie_id}")
async def remove_favorite(movie_id: int):
    """Remover dos favoritos"""
    db = next(get_db())
    favorito = db.query(Favorito).filter(Favorito.movie_id == movie_id).first()
    
    if not favorito:
        raise HTTPException(status_code=404, detail="Não encontrado nos favoritos")
    
    db.delete(favorito)
    db.commit()
    return {"message": "Removido dos favoritos"}