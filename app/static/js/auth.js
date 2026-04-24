async function handleAuth(formId, endpoint) {
  const form = document.getElementById(formId);
  if (!form) return;
  const msg = document.getElementById('authMsg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    const res = await fetch(endpoint, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
    });
    const payload = await res.json();
    msg.textContent = payload.error || payload.message;
    msg.style.color = res.ok ? 'green' : '#8b0000';
    if (res.ok) setTimeout(() => (window.location.href = payload.redirect), 500);
  });
}
handleAuth('loginForm', '/api/login');
handleAuth('signupForm', '/api/signup');
