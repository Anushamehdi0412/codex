const grid = document.getElementById('galleryGrid');
const loader = document.getElementById('loading');
const searchInput = document.getElementById('searchInput');
const categorySelect = document.getElementById('categorySelect');

function cardTemplate(item) {
  return `<article class="design-card">
      <img src="${item.image_url}" alt="${item.description}" data-view="${item.image_url}" />
      <div class="design-info">
        <h3>${item.category}</h3>
        <p>${item.description}</p>
        <button class="fav-btn" data-id="${item.id}">${item.liked ? '♥ Saved' : '♡ Save'}</button>
      </div>
    </article>`;
}

async function loadCategories() {
  const res = await fetch('/api/categories');
  const categories = await res.json();
  categories.forEach((c) => {
    const option = document.createElement('option');
    option.value = c;
    option.textContent = c;
    categorySelect.appendChild(option);
  });
}

async function loadDesigns() {
  loader.style.display = 'block';
  const params = new URLSearchParams({ q: searchInput.value, category: categorySelect.value });
  const res = await fetch(`/api/designs?${params}`);
  const data = await res.json();
  grid.innerHTML = data.map(cardTemplate).join('') || '<p>No designs found.</p>';
  loader.style.display = 'none';
}

[searchInput, categorySelect].forEach((el) => el.addEventListener('input', loadDesigns));

const lightbox = document.getElementById('lightbox');
const lightboxImage = document.getElementById('lightboxImage');

document.addEventListener('click', async (e) => {
  if (e.target.matches('img[data-view]')) {
    lightboxImage.src = e.target.dataset.view;
    lightbox.classList.remove('hidden');
  }
  if (e.target.matches('#closeLightbox') || e.target === lightbox) {
    lightbox.classList.add('hidden');
  }

  if (e.target.matches('.fav-btn')) {
    const id = e.target.dataset.id;
    const shouldSave = !e.target.textContent.includes('Saved');
    const res = await fetch(`/api/favorites/${id}`, { method: shouldSave ? 'POST' : 'DELETE' });
    if (res.ok) {
      e.target.textContent = shouldSave ? '♥ Saved' : '♡ Save';
    } else {
      alert('Please login to save favorites.');
      if (res.status === 302 || res.status === 401) window.location.href = '/login';
    }
  }
});

loadCategories().then(loadDesigns);
