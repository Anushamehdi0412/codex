const favGrid = document.getElementById('favoritesGrid');
async function loadFavorites() {
  const res = await fetch('/api/favorites');
  if (!res.ok) return (window.location.href = '/login');
  const items = await res.json();
  favGrid.innerHTML = items.map((d) => `
    <article class="design-card">
      <img src="${d.image_url}" alt="${d.description}" />
      <div class="design-info"><h3>${d.category}</h3><p>${d.description}</p></div>
    </article>`).join('') || '<p>No favorites yet.</p>';
}
loadFavorites();
