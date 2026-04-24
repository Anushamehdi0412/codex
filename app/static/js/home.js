// Lightweight autoplay highlighting for featured cards
const slides = [...document.querySelectorAll('.slide')];
let idx = 0;
setInterval(() => {
  if (!slides.length) return;
  slides.forEach((s) => (s.style.outline = 'none'));
  slides[idx].style.outline = '3px solid rgba(201,162,74,0.8)';
  idx = (idx + 1) % slides.length;
}, 2200);
