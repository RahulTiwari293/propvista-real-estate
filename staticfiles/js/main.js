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

// Auto-dismiss alerts
document.querySelectorAll('.alert').forEach(a => {
  setTimeout(() => {
    a.classList.remove('show');
    a.remove();
  }, 5000);
});

// ── Search Modal ─────────────────────────────────────────────
const overlay = document.getElementById('searchOverlay');
const openBtn = document.getElementById('searchTrigger');
const closeBtn = document.getElementById('searchClose');
const searchInput = document.getElementById('searchInput');
const suggestions = document.getElementById('searchSuggestions');

function openSearch() {
  if (!overlay) return;
  overlay.classList.add('open');
  document.body.classList.add('search-open');
  setTimeout(() => searchInput && searchInput.focus(), 200);
}

function closeSearch() {
  if (!overlay) return;
  overlay.classList.remove('open');
  document.body.classList.remove('search-open');
}

if (openBtn) openBtn.addEventListener('click', openSearch);
if (closeBtn) closeBtn.addEventListener('click', closeSearch);

// Close on backdrop click
if (overlay) {
  overlay.addEventListener('click', e => {
    if (e.target === overlay) closeSearch();
  });
}

// Close on Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeSearch();
});

// Live search input → filter suggestions
if (searchInput && suggestions) {
  const allItems = suggestions.querySelectorAll('.suggestion-item');

  searchInput.addEventListener('input', () => {
    const q = searchInput.value.toLowerCase().trim();
    if (!q) {
      allItems.forEach(i => i.style.display = '');
      return;
    }
    allItems.forEach(i => {
      const text = i.textContent.toLowerCase();
      i.style.display = text.includes(q) ? '' : 'none';
    });
  });

  // Submit search on Enter
  searchInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const q = searchInput.value.trim();
      if (q) window.location.href = `/search/?keywords=${encodeURIComponent(q)}`;
    }
  });
}
