from fastapi import APIRouter
from database import get_db
from models import Favorito, Avaliacao
from rotas.filmes import fetch_tmdb

router = APIRouter(prefix="/recommendations", tags=["Recomendações"])

@router.get("")
async def get_recommendations():
    """Gerar recomendações INTELIGENTES baseadas em favoritos e avaliações"""
    db = next(get_db())
    
    # Pegar filmes favoritos e bem avaliados (4+ estrelas)
    favoritos = db.query(Favorito).all()
    avaliacoes_altas = db.query(Avaliacao).filter(Avaliacao.rating >= 4).all()
    
    print(f"📊 Favoritos: {len(favoritos)}")
    print(f"⭐ Avaliações altas: {len(avaliacoes_altas)}")
    
    # Coletar IDs únicos de filmes que o usuário gostou
    movie_ids = set()
    for fav in favoritos:
        movie_ids.add(fav.movie_id)
    for aval in avaliacoes_altas:
        movie_ids.add(aval.movie_id)
    
    print(f"🎬 Total de filmes que você gostou: {len(movie_ids)}")
    
    # Se não tem nenhum filme, retorna populares
    if not movie_ids:
        data = await fetch_tmdb("/movie/popular")
        return {
            "message": "Avalie ou favorite filmes para receber recomendações personalizadas!",
            "results": data.get("results", [])[:12]
        }
    
    # === ESTRATÉGIA PRINCIPAL: FILMES SIMILARES (Machine Learning do TMDb) ===
    recomendacoes = []
    recomendacoes_ids = set()
    
    print("🤖 Buscando filmes SIMILARES (ML do TMDb)...")
    for movie_id in list(movie_ids):
        try:
            data = await fetch_tmdb(f"/movie/{movie_id}/similar")
            if "results" in data:
                print(f"✅ Encontrados {len(data['results'])} similares para filme {movie_id}")
                for movie in data["results"]:
                    # Filtrar por qualidade mínima
                    if (movie["id"] not in movie_ids and 
                        movie["id"] not in recomendacoes_ids and
                        movie.get("vote_average", 0) >= 6.5 and
                        movie.get("vote_count", 0) >= 100):
                        recomendacoes.append(movie)
                        recomendacoes_ids.add(movie["id"])
        except Exception as e:
            print(f"❌ Erro ao buscar similares de {movie_id}: {e}")
            continue
    
    print(f"🎯 Recomendações por similaridade: {len(recomendacoes)}")
    
    # === ESTRATÉGIA SECUNDÁRIA: SE NÃO TEM SUFICIENTE, BUSCA POR GÊNEROS ===
    if len(recomendacoes) < 15:
        print("🎭 Complementando com busca por gêneros...")
        generos = set()
        
        # Pegar gêneros dos filmes favoritos
        for movie_id in list(movie_ids)[:3]:
            try:
                movie_data = await fetch_tmdb(f"/movie/{movie_id}")
                if "genres" in movie_data:
                    for genre in movie_data["genres"]:
                        generos.add(genre["id"])
            except:
                continue
        
        # Buscar filmes dos mesmos gêneros
        for genre_id in list(generos)[:2]:
            if len(recomendacoes) >= 20:
                break
            try:
                data = await fetch_tmdb(
                    f"/discover/movie?with_genres={genre_id}&sort_by=popularity.desc&vote_average.gte=7.0&vote_count.gte=300"
                )
                if "results" in data:
                    for movie in data["results"][:10]:
                        if (movie["id"] not in movie_ids and 
                            movie["id"] not in recomendacoes_ids):
                            recomendacoes.append(movie)
                            recomendacoes_ids.add(movie["id"])
                            if len(recomendacoes) >= 20:
                                break
            except:
                continue
    
    # Ordenar por nota (melhores primeiro)
    recomendacoes.sort(key=lambda x: x.get("vote_average", 0), reverse=True)
    
    print(f"🎯 TOTAL FINAL de recomendações: {len(recomendacoes)}")
    
    return {
        "message": f"Baseado em {len(movie_ids)} filmes que você gostou!",
        "results": recomendacoes[:20]
    }