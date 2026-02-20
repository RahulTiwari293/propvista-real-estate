// Animated counters on homepage
document.querySelectorAll('.stat-num').forEach(el => {
  const target = +el.dataset.target;
  if (!target) return;
  let n = 0;
  const step = Math.ceil(target / 60);
  const t = setInterval(() => {
    n = Math.min(n + step, target);
    el.textContent = n.toLocaleString();
    if (n >= target) clearInterval(t);
  }, 20);
});

// Navbar scroll effect
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.style.background = window.scrollY > 50
      ? 'rgba(15,17,23,0.98)'
      : 'rgba(15,17,23,0.95)';
  });
}

// Auto-dismiss toasts
document.querySelectorAll('.toast').forEach(t => {
  setTimeout(() => t.classList.remove('show'), 4000);
});
