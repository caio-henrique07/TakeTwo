from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from rotas import filmes, favoritos, avaliacoes, comentarios, recomendacoes

# Criar tabelas
Base.metadata.create_all(bind=engine)

# App
app = FastAPI(title="TakeTwo API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(filmes.router)
app.include_router(favoritos.router)
app.include_router(avaliacoes.router)
app.include_router(comentarios.router)
app.include_router(recomendacoes.router)

@app.get("/")
async def root():
    return {"message": "TakeTwo API - Funcionando!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)