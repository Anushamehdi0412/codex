document.addEventListener('click', async (e) => {
  if (!e.target.matches('.fav-btn')) return;
  const id = e.target.dataset.id;
  const res = await fetch(`/api/favorites/${id}`, { method: 'POST' });
  if (res.ok) {
    e.target.textContent = '♥ Saved';
  }
});
