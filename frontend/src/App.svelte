<script>
  import { onMount } from 'svelte';

  const API_URL = 'http://localhost:8000';
  const IMG_BASE = 'https://image.tmdb.org/t/p/w500';

  let currentPage = 'home';
  let movies = [];
  let selectedMovie = null;
  let favorites = [];
  let ratings = [];
  let searchQuery = '';
  let loading = false;

  // ===== FUNÇÕES API =====
  async function fetchPopularMovies() {
    loading = true;
    const res = await fetch(`${API_URL}/movies/popular`);
    const data = await res.json();
    movies = data.results || [];
    loading = false;
  }

  async function searchMovies() {
    if (!searchQuery.trim()) {
      fetchPopularMovies();
      return;
    }

    loading = true;

    const res = await fetch(
      `${API_URL}/movies/search?q=` + encodeURIComponent(searchQuery)
    );

    const data = await res.json();
    movies = data.results || [];
    loading = false;
  }


  async function getMovieDetails(movieId) {
    loading = true;
    const res = await fetch(`${API_URL}/movies/${movieId}`);
    selectedMovie = await res.json();
    currentPage = 'details';
    loading = false;
  }

  async function loadFavorites() {
    const res = await fetch(`${API_URL}/favorites`);
    favorites = await res.json();
  }

  async function toggleFavorite(movieId) {
    const isFavorited = favorites.some(f => f.movie.id === movieId);
    
    if (isFavorited) {
      await fetch(`${API_URL}/favorites/${movieId}`, { method: 'DELETE' });
      alert('Removido dos favoritos!');
    } else {
      await fetch(`${API_URL}/favorites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ movie_id: movieId })
      });
      alert('Adicionado aos favoritos!');
    }
    loadFavorites();
  }

  async function loadRatings() {
    const res = await fetch(`${API_URL}/ratings`);
    ratings = await res.json();
  }

  async function addRating(movieId, rating, comment) {
    await fetch(`${API_URL}/ratings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ movie_id: movieId, rating, comment })
    });
    alert('Avaliação salva!');
    loadRatings();
  }

  onMount(() => {
    fetchPopularMovies();
    loadFavorites();
    loadRatings();
  });

  function goToHome() {
    currentPage = 'home';
    fetchPopularMovies();
  }

  function goToFavorites() {
    currentPage = 'favorites';
    loadFavorites();
  }

  function goToRatings() {
    currentPage = 'ratings';
    loadRatings();
  }

  let tempRating = 0;
  let tempComment = '';
  
  function handleRate() {
    if (tempRating > 0) {
      addRating(selectedMovie.id, tempRating, tempComment);
      tempRating = 0;
      tempComment = '';
    }
  }
</script>

<main>
  <nav>
    <h1>🎬 TakeTwo</h1>
    <div class="nav-links">
      <button on:click={goToHome} class:active={currentPage === 'home'}>Home</button>
      <button on:click={goToFavorites} class:active={currentPage === 'favorites'}>
        Favoritos ({favorites.length})
      </button>
      <button on:click={goToRatings} class:active={currentPage === 'ratings'}>
        Minhas Avaliações ({ratings.length})
      </button>
    </div>
  </nav>

  {#if currentPage === 'home'}
    <div class="container">
      <div class="search-bar">
        <input
          type="text"
          bind:value={searchQuery}
          on:keyup={(e) => e.key === 'Enter' && searchMovies()}
          placeholder="Buscar filmes..."
        />
        <button on:click={searchMovies}>Buscar</button>
      </div>

      {#if loading}
        <p class="loading">Carregando...</p>
      {:else}
        <div class="movie-grid">
          {#each movies as movie}
            <button type="button" class="movie-card" on:click={() => getMovieDetails(movie.id)}>
              <img src="{IMG_BASE}{movie.poster_path}" alt={movie.title} />
              <h3>{movie.title}</h3>
              <p>⭐ {movie.vote_average.toFixed(1)}</p>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  {/if}

  {#if currentPage === 'details' && selectedMovie}
    <div class="container details">
      <button on:click={goToHome} class="back-btn">← Voltar</button>
      
      <div class="details-content">
        <img src="{IMG_BASE}{selectedMovie.poster_path}" alt={selectedMovie.title} class="poster-large" />
        
        <div class="details-info">
          <h1>{selectedMovie.title}</h1>
          <p class="tagline">{selectedMovie.tagline || ''}</p>
          <p><strong>Ano:</strong> {selectedMovie.release_date?.split('-')[0]}</p>
          <p><strong>Duração:</strong> {selectedMovie.runtime} min</p>
          <p><strong>Nota TMDb:</strong> ⭐ {selectedMovie.vote_average.toFixed(1)}/10</p>
          <p class="overview">{selectedMovie.overview}</p>

          <div class="actions">
            <button on:click={() => toggleFavorite(selectedMovie.id)} class="btn-favorite">
              {favorites.some(f => f.movie.id === selectedMovie.id) ? '❤️ Remover dos Favoritos' : '🤍 Adicionar aos Favoritos'}
            </button>
          </div>

          <div class="rating-form">
            <h3>Avaliar este filme:</h3>
            <div class="stars">
              {#each [1, 2, 3, 4, 5] as star}
                <button 
                  type="button"
                  class="star" 
                  class:filled={star <= tempRating}
                  on:click={() => tempRating = star}
                  aria-label="Rate {star} star"
                >
                  ⭐
                </button>
              {/each}
            </div>
            <textarea bind:value={tempComment} placeholder="Comentário opcional..."></textarea>
            <button on:click={handleRate} disabled={tempRating === 0}>Salvar Avaliação</button>
          </div>
        </div>
      </div>
    </div>
  {/if}

  {#if currentPage === 'favorites'}
    <div class="container">
      <h2>Meus Favoritos</h2>
      {#if favorites.length === 0}
        <p class="empty">Você ainda não tem favoritos.</p>
      {:else}
        <div class="movie-grid">
          {#each favorites as fav}
            <button type="button" class="movie-card" on:click={() => getMovieDetails(fav.movie.id)}>
              <img src="{IMG_BASE}{fav.movie.poster_path}" alt={fav.movie.title} />
              <h3>{fav.movie.title}</h3>
              <p>⭐ {fav.movie.vote_average.toFixed(1)}</p>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  {/if}

  {#if currentPage === 'ratings'}
    <div class="container">
      <h2>Minhas Avaliações</h2>
      {#if ratings.length === 0}
        <p class="empty">Você ainda não avaliou nenhum filme.</p>
      {:else}
        <div class="ratings-list">
          {#each ratings as rating}
            <div class="rating-item">
              <img src="{IMG_BASE}{rating.movie.poster_path}" alt={rating.movie.title} />
              <div class="rating-info">
                <h3>{rating.movie.title}</h3>
                <p class="stars">{'⭐'.repeat(rating.rating)}</p>
                {#if rating.comment}
                  <p class="comment">"{rating.comment}"</p>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Arial', sans-serif;
    background: #0a0a0a;
    color: #fff;
  }

  main {
    min-height: 100vh;
  }

  nav {
    background: #1a1a1a;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #c41e3a;
  }

  nav h1 {
    margin: 0;
    color: #d4af37;
    font-size: 2rem;
  }

  .nav-links button {
    background: none;
    border: none;
    color: #fff;
    margin-left: 1rem;
    cursor: pointer;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background 0.3s;
  }

  .nav-links button:hover,
  .nav-links button.active {
    background: #c41e3a;
  }

  .container {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 2rem;
  }

  .search-bar {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .search-bar input {
    flex: 1;
    padding: 0.75rem;
    font-size: 1rem;
    border: 2px solid #5c5c5c;
    background: #1a1a1a;
    color: #fff;
    border-radius: 4px;
  }

  .search-bar button {
    padding: 0.75rem 2rem;
    background: #c41e3a;
    border: none;
    color: #fff;
    font-size: 1rem;
    cursor: pointer;
    border-radius: 4px;
  }

  .movie-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 2rem;
  }

  .movie-card {
    cursor: pointer;
    transition: transform 0.3s;
    background: none;
    border: none;
    padding: 0;
    text-align: left;
  }

  .movie-card:hover {
    transform: scale(1.05);
  }

  .movie-card img {
    width: 100%;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
  }

  .movie-card h3 {
    margin: 0.5rem 0;
    font-size: 1rem;
  }

  .details {
    max-width: 900px;
  }

  .details-content {
    display: flex;
    gap: 2rem;
    margin-top: 2rem;
  }

  .poster-large {
    width: 300px;
    border-radius: 8px;
  }

  .details-info {
    flex: 1;
  }

  .details-info h1 {
    margin: 0;
    color: #d4af37;
  }

  .tagline {
    font-style: italic;
    color: #999;
    margin: 0.5rem 0 1rem;
  }

  .overview {
    line-height: 1.6;
    margin: 1rem 0;
  }

  .actions {
    margin: 2rem 0;
  }

  .btn-favorite {
    padding: 0.75rem 2rem;
    background: #c41e3a;
    border: none;
    color: #fff;
    cursor: pointer;
    border-radius: 4px;
    font-size: 1rem;
  }

  .rating-form {
    background: #1a1a1a;
    padding: 1.5rem;
    border-radius: 8px;
    margin-top: 2rem;
  }

  .stars {
    display: flex;
    gap: 0.5rem;
    margin: 1rem 0;
  }

  .star {
    font-size: 2rem;
    cursor: pointer;
    opacity: 0.3;
    transition: opacity 0.2s;
  }

  .star.filled {
    opacity: 1;
  }

  .rating-form textarea {
    width: 100%;
    padding: 0.75rem;
    margin: 1rem 0;
    background: #0a0a0a;
    border: 2px solid #5c5c5c;
    color: #fff;
    border-radius: 4px;
    font-family: inherit;
    resize: vertical;
  }

  .rating-form button {
    padding: 0.75rem 2rem;
    background: #d4af37;
    border: none;
    color: #0a0a0a;
    cursor: pointer;
    border-radius: 4px;
    font-weight: bold;
  }

  .rating-form button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .ratings-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .rating-item {
    background: #1a1a1a;
    padding: 1rem;
    border-radius: 8px;
    display: flex;
    gap: 1rem;
  }

  .rating-item img {
    width: 100px;
    border-radius: 4px;
  }

  .rating-info h3 {
    margin: 0 0 0.5rem 0;
  }

  .comment {
    font-style: italic;
    color: #999;
    margin-top: 0.5rem;
  }

  .back-btn {
    background: #5c5c5c;
    border: none;
    color: #fff;
    padding: 0.5rem 1rem;
    cursor: pointer;
    border-radius: 4px;
  }

  .loading, .empty {
    text-align: center;
    color: #999;
    padding: 2rem;
  }
</style>