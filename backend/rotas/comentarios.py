from fastapi import APIRouter, HTTPException
from database import get_db
from models import Comentario
from schemas import ComentarioCreate

router = APIRouter(prefix="/comments", tags=["Comentários"])

@router.get("/{movie_id}")
async def get_comments(movie_id: int):
    """Listar comentários de um filme"""
    db = next(get_db())
    comentarios = db.query(Comentario).filter(
        Comentario.movie_id == movie_id
    ).order_by(Comentario.created_at.desc()).all()
    
    return [{
        "id": c.id,
        "username": c.username,
        "comment": c.comment,
        "created_at": c.created_at.strftime("%d/%m/%Y %H:%M")
    } for c in comentarios]

@router.post("")
async def add_comment(comentario: ComentarioCreate):
    """Adicionar comentário"""
    db = next(get_db())
    
    new_comment = Comentario(
        movie_id=comentario.movie_id,
        username=comentario.username,
        comment=comentario.comment
    )
    db.add(new_comment)
    db.commit()
    return {"message": "Comentário adicionado"}

@router.delete("/{comment_id}")
async def delete_comment(comment_id: int):
    """Deletar comentário"""
    db = next(get_db())
    comentario = db.query(Comentario).filter(Comentario.id == comment_id).first()
    
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    
    db.delete(comentario)
    db.commit()
    return {"message": "Comentário removido"}