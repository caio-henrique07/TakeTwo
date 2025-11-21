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
      await loadComments(movieId);  // ← ADICIONE ESTA LINHA
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

  let comments = [];
  let recommendations = [];
  let recommendationsMessage = '';
  let newComment = '';
  let username = 'Usuário Demo';
  
  function handleRate() {
    if (tempRating > 0) {
      addRating(selectedMovie.id, tempRating, tempComment);
      tempRating = 0;
      tempComment = '';
    }
  }

  async function loadComments(movieId) {
    const res = await fetch(`${API_URL}/comments/${movieId}`);
    comments = await res.json();
  }

  async function addComment(movieId) {
    if (!newComment.trim()) return;
    
    await fetch(`${API_URL}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        movie_id: movieId, 
        username: username,
        comment: newComment 
      })
    });
    
    newComment = '';
    loadComments(movieId);
    alert('Comentário adicionado!');
  }

  async function deleteComment(commentId, movieId) {
    if (!confirm('Deletar comentário?')) return;
    
    await fetch(`${API_URL}/comments/${commentId}`, { method: 'DELETE' });
    loadComments(movieId);
    alert('Comentário removido!');
  }

  async function loadRecommendations() {
  loading = true;
  const res = await fetch(`${API_URL}/recommendations`);
  const data = await res.json();
  recommendations = data.results || [];
  recommendationsMessage = data.message || '';
  loading = false;
}

function goToRecommendations() {
  currentPage = 'recommendations';
  loadRecommendations();
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
      <button on:click={goToRecommendations} class:active={currentPage === 'recommendations'}>
        🎯 Para Você
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

          <!-- SEÇÃO DE COMENTÁRIOS -->
          <div class="comments-section">
            <h3>💬 Comentários ({comments.length})</h3>
            
            <div class="add-comment">
              <input 
                type="text" 
                bind:value={username} 
                placeholder="Seu nome..."
                class="username-input"
              />
              <textarea 
                bind:value={newComment} 
                placeholder="Escreva seu comentário..."
                rows="3"
              ></textarea>
              <button on:click={() => addComment(selectedMovie.id)}>
                Enviar Comentário
              </button>
            </div>

            <div class="comments-list">
              {#if comments.length === 0}
                <p class="empty">Seja o primeiro a comentar!</p>
              {:else}
                {#each comments as comment}
                  <div class="comment-item">
                    <div class="comment-header">
                      <strong>👤 {comment.username}</strong>
                      <span class="comment-date">{comment.created_at}</span>
                    </div>
                    <p class="comment-text">{comment.comment}</p>
                    <button 
                      class="delete-comment" 
                      on:click={() => deleteComment(comment.id, selectedMovie.id)}
                    >
                      🗑️ Deletar
                    </button>
                  </div>
                {/each}
              {/if}
            </div>
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

  {#if currentPage === 'recommendations'}
    <div class="container">
      <div class="recommendations-header">
        <h2>🎯 Recomendado Para Você</h2>
        {#if recommendationsMessage}
          <p class="rec-message">{recommendationsMessage}</p>
        {/if}
      </div>

      {#if loading}
        <p class="loading">Carregando recomendações...</p>
      {:else if recommendations.length === 0}
        <div class="empty-recommendations">
          <p class="empty">Favorite ou avalie filmes para receber recomendações personalizadas! ⭐</p>
          <button on:click={goToHome} class="btn-go-home">Explorar Filmes</button>
        </div>
      {:else}
        <div class="movie-grid">
          {#each recommendations as movie}
            <button type="button" class="movie-card" on:click={() => getMovieDetails(movie.id)}>
              {#if movie.poster_path}
                <img src="{IMG_BASE}{movie.poster_path}" alt={movie.title} />
              {:else}
                <div class="no-poster">🎬</div>
              {/if}
              <h3>{movie.title}</h3>
              <p>⭐ {movie.vote_average.toFixed(1)}</p>
            </button>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    background: #0a0a0a;
    color: #fff;
    scroll-behavior: smooth;
  }

  main {
    min-height: 100vh;
  }

  /* NAVBAR */
  nav {
    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #c41e3a;
    box-shadow: 0 4px 20px rgba(196, 30, 58, 0.3);
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(10px);
  }

  nav h1 {
    margin: 0;
    background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2rem;
    font-weight: bold;
    text-shadow: 0 0 30px rgba(212, 175, 55, 0.5);
  }

  .nav-links button {
    background: transparent;
    border: 2px solid transparent;
    color: #fff;
    margin-left: 1rem;
    cursor: pointer;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    transition: all 0.3s ease;
    font-size: 1rem;
    font-weight: 500;
  }

  .nav-links button:hover {
    background: rgba(196, 30, 58, 0.2);
    border-color: #c41e3a;
    transform: translateY(-2px);
  }

  .nav-links button.active {
    background: linear-gradient(135deg, #c41e3a 0%, #a01828 100%);
    border-color: #c41e3a;
    box-shadow: 0 4px 15px rgba(196, 30, 58, 0.4);
  }

  /* CONTAINER */
  .container {
    max-width: 1400px;
    margin: 2rem auto;
    padding: 0 2rem;
    animation: fadeIn 0.5s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* SEARCH BAR */
  .search-bar {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .search-bar input {
    flex: 1;
    padding: 1rem 1.5rem;
    font-size: 1rem;
    border: 2px solid #5c5c5c;
    background: #1a1a1a;
    color: #fff;
    border-radius: 12px;
    transition: all 0.3s ease;
    outline: none;
  }

  .search-bar input:focus {
    border-color: #c41e3a;
    box-shadow: 0 0 20px rgba(196, 30, 58, 0.3);
    transform: translateY(-2px);
  }

  .search-bar button {
    padding: 1rem 2.5rem;
    background: linear-gradient(135deg, #c41e3a 0%, #a01828 100%);
    border: none;
    color: #fff;
    font-size: 1rem;
    cursor: pointer;
    border-radius: 12px;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(196, 30, 58, 0.3);
  }

  .search-bar button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(196, 30, 58, 0.5);
  }

  .search-bar button:active {
    transform: translateY(0);
  }

  /* MOVIE GRID */
  .movie-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 2rem;
  }

  .movie-card {
    cursor: pointer;
    transition: all 0.3s ease;
    animation: cardFadeIn 0.5s ease;
    position: relative;
  }

  @keyframes cardFadeIn {
    from {
      opacity: 0;
      transform: scale(0.9);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  .movie-card:hover {
    transform: translateY(-10px) scale(1.03);
    z-index: 10;
  }

  .movie-card img {
    width: 100%;
    border-radius: 12px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.6);
    transition: all 0.3s ease;
  }

  .movie-card:hover img {
    box-shadow: 0 12px 40px rgba(196, 30, 58, 0.4);
  }

  .movie-card h3 {
    margin: 0.8rem 0 0.3rem 0;
    font-size: 1.05rem;
    font-weight: 600;
  }

  .movie-card p {
    color: #d4af37;
    font-weight: bold;
    font-size: 1.1rem;
  }

  /* DETAILS */
  .details {
    max-width: 1000px;
  }

  .details-content {
    display: flex;
    gap: 2.5rem;
    margin-top: 2rem;
    animation: fadeIn 0.5s ease;
  }

  .poster-large {
    width: 350px;
    border-radius: 16px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.7);
    transition: all 0.3s ease;
  }

  .poster-large:hover {
    transform: scale(1.05);
    box-shadow: 0 15px 50px rgba(196, 30, 58, 0.3);
  }

  .details-info {
    flex: 1;
  }

  .details-info h1 {
    margin: 0;
    background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5rem;
  }

  .tagline {
    font-style: italic;
    color: #999;
    margin: 0.5rem 0 1.5rem;
    font-size: 1.1rem;
  }

  .details-info p {
    line-height: 1.8;
    font-size: 1.05rem;
  }

  .overview {
    line-height: 1.8;
    margin: 1.5rem 0;
    color: #ddd;
  }

  .actions {
    margin: 2rem 0;
  }

  .btn-favorite {
    padding: 1rem 2.5rem;
    background: linear-gradient(135deg, #c41e3a 0%, #a01828 100%);
    border: none;
    color: #fff;
    cursor: pointer;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(196, 30, 58, 0.3);
  }

  .btn-favorite:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 25px rgba(196, 30, 58, 0.5);
  }

  /* RATING */
  .rating-form {
    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
    padding: 2rem;
    border-radius: 16px;
    margin-top: 2rem;
    border: 2px solid #333;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
  }

  .rating-form h3 {
    color: #d4af37;
    margin-bottom: 1rem;
  }

  .stars {
    display: flex;
    gap: 0.8rem;
    margin: 1.5rem 0;
  }

  .star {
    font-size: 2.5rem;
    cursor: pointer;
    opacity: 0.3;
    transition: all 0.3s ease;
    filter: grayscale(100%);
  }

  .star:hover {
    transform: scale(1.2) rotate(15deg);
    opacity: 0.7;
  }

  .star.filled {
    opacity: 1;
    filter: grayscale(0%);
    text-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
  }

  .rating-form textarea {
    width: 100%;
    padding: 1rem;
    margin: 1rem 0;
    background: #0a0a0a;
    border: 2px solid #5c5c5c;
    color: #fff;
    border-radius: 12px;
    font-family: inherit;
    resize: vertical;
    font-size: 1rem;
    transition: all 0.3s ease;
    outline: none;
  }

  .rating-form textarea:focus {
    border-color: #d4af37;
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);
  }

  .rating-form button {
    padding: 1rem 2.5rem;
    background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
    border: none;
    color: #0a0a0a;
    cursor: pointer;
    border-radius: 12px;
    font-weight: bold;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
  }

  .rating-form button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 25px rgba(212, 175, 55, 0.5);
  }

  .rating-form button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
  }

  /* RATINGS LIST */
  .ratings-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .rating-item {
    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
    padding: 1.5rem;
    border-radius: 16px;
    display: flex;
    gap: 1.5rem;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    animation: cardFadeIn 0.5s ease;
  }

  .rating-item:hover {
    border-color: #c41e3a;
    transform: translateX(10px);
    box-shadow: 0 8px 30px rgba(196, 30, 58, 0.2);
  }

  .rating-item img {
    width: 120px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
  }

  .rating-info h3 {
    margin: 0 0 0.5rem 0;
    color: #d4af37;
  }

  .comment {
    font-style: italic;
    color: #999;
    margin-top: 0.5rem;
    line-height: 1.6;
  }

  .back-btn {
    background: #5c5c5c;
    border: none;
    color: #fff;
    padding: 0.8rem 1.5rem;
    cursor: pointer;
    border-radius: 10px;
    transition: all 0.3s ease;
    font-weight: 600;
  }

  .back-btn:hover {
    background: #c41e3a;
    transform: translateX(-5px);
  }

  /* LOADING */
  .loading {
    text-align: center;
    color: #d4af37;
    padding: 4rem 2rem;
    font-size: 1.5rem;
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  .empty {
    text-align: center;
    color: #999;
    padding: 4rem 2rem;
    font-size: 1.2rem;
    animation: fadeIn 0.5s ease;
  }

  /* COMENTÁRIOS */
  .comments-section {
    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
    padding: 2rem;
    border-radius: 16px;
    margin-top: 2rem;
    border: 2px solid #333;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
  }

  .comments-section h3 {
    margin: 0 0 1.5rem 0;
    color: #d4af37;
    font-size: 1.8rem;
  }

  .add-comment {
    background: #0a0a0a;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
  }

  .username-input {
    width: 100%;
    padding: 0.9rem;
    margin-bottom: 1rem;
    background: #1a1a1a;
    border: 2px solid #5c5c5c;
    color: #fff;
    border-radius: 10px;
    font-family: inherit;
    transition: all 0.3s ease;
    outline: none;
  }

  .username-input:focus {
    border-color: #d4af37;
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);
  }

  .add-comment textarea {
    width: 100%;
    padding: 0.9rem;
    margin-bottom: 1rem;
    background: #1a1a1a;
    border: 2px solid #5c5c5c;
    color: #fff;
    border-radius: 10px;
    font-family: inherit;
    resize: vertical;
    transition: all 0.3s ease;
    outline: none;
  }

  .add-comment textarea:focus {
    border-color: #d4af37;
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);
  }

  .add-comment button {
    padding: 0.9rem 2rem;
    background: linear-gradient(135deg, #c41e3a 0%, #a01828 100%);
    border: none;
    color: #fff;
    cursor: pointer;
    border-radius: 10px;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(196, 30, 58, 0.3);
  }

  .add-comment button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(196, 30, 58, 0.5);
  }

  .comments-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .comment-item {
    background: #0a0a0a;
    padding: 1.2rem;
    border-radius: 12px;
    border-left: 4px solid #d4af37;
    transition: all 0.3s ease;
    animation: cardFadeIn 0.5s ease;
  }

  .comment-item:hover {
    transform: translateX(8px);
    border-left-width: 6px;
    box-shadow: 0 4px 20px rgba(212, 175, 55, 0.2);
  }

  .comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
  }

  .comment-header strong {
    color: #d4af37;
    font-size: 1.1rem;
  }

  .comment-date {
    font-size: 0.9rem;
    color: #999;
  }

  .comment-text {
    color: #ddd;
    line-height: 1.6;
    margin: 0.5rem 0;
  }

  .delete-comment {
    background: #5c5c5c;
    border: none;
    color: #fff;
    padding: 0.5rem 1rem;
    cursor: pointer;
    border-radius: 8px;
    font-size: 0.9rem;
    margin-top: 0.5rem;
    transition: all 0.3s ease;
  }

  .delete-comment:hover {
    background: #c41e3a;
    transform: translateY(-2px);
  }

  /* RECOMENDAÇÕES */
  .recommendations-header {
    text-align: center;
    margin-bottom: 3rem;
    animation: fadeIn 0.5s ease;
  }

  .recommendations-header h2 {
    background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3rem;
    margin-bottom: 1rem;
    text-shadow: 0 0 40px rgba(212, 175, 55, 0.3);
  }

  .rec-message {
    color: #999;
    font-size: 1.2rem;
    font-style: italic;
  }

  .empty-recommendations {
    text-align: center;
    padding: 5rem 2rem;
    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
    border-radius: 20px;
    margin-top: 2rem;
    border: 2px solid #333;
    animation: fadeIn 0.5s ease;
  }

  .empty-recommendations .empty {
    font-size: 1.3rem;
    margin-bottom: 2rem;
  }

  .btn-go-home {
    padding: 1.2rem 3rem;
    background: linear-gradient(135deg, #c41e3a 0%, #a01828 100%);
    border: none;
    color: #fff;
    cursor: pointer;
    border-radius: 12px;
    font-size: 1.2rem;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(196, 30, 58, 0.4);
  }

  .btn-go-home:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 8px 30px rgba(212, 175, 55, 0.5);
    background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
    color: #0a0a0a;
  }

  .no-poster {
    width: 100%;
    aspect-ratio: 2/3;
    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 4rem;
    border-radius: 12px;
    border: 2px solid #333;
  }

  /* RESPONSIVO */
  @media (max-width: 768px) {
    nav {
      flex-direction: column;
      gap: 1rem;
    }

    .nav-links {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.5rem;
    }

    .nav-links button {
      margin: 0;
      font-size: 0.9rem;
      padding: 0.5rem 1rem;
    }

    .details-content {
      flex-direction: column;
    }

    .poster-large {
      width: 100%;
      max-width: 300px;
      margin: 0 auto;
    }

    .movie-grid {
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 1rem;
    }
  }
</style>