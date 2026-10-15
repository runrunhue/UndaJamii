(function () {
    const html = document.documentElement;
    const toggle = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    const label = document.getElementById('theme-label');

    const saved = localStorage.getItem('undajamii-theme') || 'light';
    applyTheme(saved);

    if (toggle) {
        toggle.addEventListener('click', () => {
            const next = html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            applyTheme(next);
            localStorage.setItem('undajamii-theme', next);
        });
    }

    function applyTheme(theme) {
        html.setAttribute('data-bs-theme', theme);
        if (icon)  icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
        if (label) label.textContent = theme === 'dark' ? 'Light' : 'Theme';
    }

    // Auto-dismiss toasts
    document.querySelectorAll('.toast-msg').forEach(el => {
        setTimeout(() => {
            el.style.transition = 'opacity .4s ease, transform .4s ease';
            el.style.opacity = '0';
            el.style.transform = 'translateY(-8px)';
            setTimeout(() => el.remove(), 400);
        }, 3500);
    });
})();