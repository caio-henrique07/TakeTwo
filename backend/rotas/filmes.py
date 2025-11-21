from fastapi import APIRouter
import httpx

router = APIRouter(prefix="/movies", tags=["Filmes"])

TMDB_API_KEY = "995fb88d7c5e211d67d59faae0b52cb3"  # chave tmdb
TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def fetch_tmdb(endpoint: str):
    """Buscar dados da API TMDb"""
    url = f"{TMDB_BASE_URL}{endpoint}"
    params = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
    
    print(f"🔍 Buscando: {url}")  # Debug
    print(f"🔑 API Key: {TMDB_API_KEY[:10]}...")  # Debug (mostra só início)
    print(f"📋 Params: {params}")  # Debug
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        print(f"✅ Resposta: {data.get('total_results', 0)} resultados")  # Debug
        return data

@router.get("/popular")
async def get_popular_movies(page: int = 1):
    """Filmes populares"""
    data = await fetch_tmdb(f"/movie/popular?page={page}")
    return data

@router.get("/search")
async def search_movies(q: str, page: int = 1):
    """Buscar filmes"""
    try:
        # Passa só o endpoint base, params vão separados
        url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "pt-BR",
            "query": q,  # ← ADICIONA O QUERY NOS PARAMS
            "page": page
        }
        
        print(f"🔍 Buscando: {url}")
        print(f"📋 Query: {q}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            print(f"✅ Resposta: {data.get('total_results', 0)} resultados")
            
            if "results" not in data:
                return {"results": []}
            return data
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return {"results": []}

@router.get("/{movie_id}")
async def get_movie_details(movie_id: int):
    """Detalhes de um filme"""
    data = await fetch_tmdb(f"/movie/{movie_id}")
    return data