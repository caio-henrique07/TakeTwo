from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

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

class Comentario(Base):
    __tablename__ = "comentarios"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, index=True)
    username = Column(String, default="Usuário Demo")
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)