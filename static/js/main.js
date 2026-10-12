// 19-Maktab — Professional Frontend Interactive Engine
document.addEventListener('DOMContentLoaded', () => {

    /* ----------------------------------------------------------------------
       1. DARK / LIGHT MODE ENGINE
       ---------------------------------------------------------------------- */
    const themeToggleBtn = document.getElementById('darkModeToggle');
    const themeIcon = document.getElementById('darkModeIcon');
    const rootHtml = document.documentElement;

    // Load saved theme (Default is ALWAYS LIGHT unless user explicitly chose dark)
    const savedTheme = localStorage.getItem('maktab19_theme') || 'light';

    function applyTheme(theme) {
        rootHtml.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('maktab19_theme', theme);
        if (themeIcon) {
            if (theme === 'dark') {
                themeIcon.className = 'fas fa-sun';
                themeIcon.style.color = '#FACC15';
            } else {
                themeIcon.className = 'fas fa-moon';
                themeIcon.style.color = '#475569';
            }
        }
    }

    applyTheme(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = rootHtml.getAttribute('data-theme') || 'light';
            const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme);
        });
    }

    /* ----------------------------------------------------------------------
       2. THREE-LANGUAGE SWITCHER (UZ, RU, EN)
       ---------------------------------------------------------------------- */
    const langSelect = document.getElementById('languageSwitcher');
    if (langSelect) {
        langSelect.addEventListener('change', (e) => {
            const selectedLang = e.target.value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

            const formData = new FormData();
            formData.append('language', selectedLang);
            formData.append('next', window.location.pathname);

            fetch('/api/set-language/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    window.location.href = `/api/set-language/?language=${selectedLang}&next=${encodeURIComponent(window.location.pathname)}`;
                }
            })
            .catch(() => {
                window.location.href = `/api/set-language/?language=${selectedLang}&next=${encodeURIComponent(window.location.pathname)}`;
            });
        });
    }

    /* ----------------------------------------------------------------------
       3. MOBILE NAVBAR AUTO-COLLAPSE ON LINK CLICK
       (Telefonda menyudagi link bosilganda hamburger menyu silliq yopiladi)
       ---------------------------------------------------------------------- */
    const navbarCollapse = document.getElementById('mainNavbar');
    if (navbarCollapse) {
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                    try {
                        const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse) || new bootstrap.Collapse(navbarCollapse);
                        bsCollapse.hide();
                    } catch (e) {
                        navbarCollapse.classList.remove('show');
                    }
                }
            });
        });
    }

    /* ----------------------------------------------------------------------
       4. AUTO-DISMISS ALERT NOTIFICATIONS
       ---------------------------------------------------------------------- */
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.display = 'none';
            }
        }, 5000);
    });

    /* ----------------------------------------------------------------------
       5. SMOOTH ACTIVE STATE FOR NAV LINKS ON SCROLL
       ---------------------------------------------------------------------- */
    const sections = document.querySelectorAll('section[id]');
    if (sections.length > 0) {
        window.addEventListener('scroll', () => {
            const scrollY = window.pageYOffset;
            sections.forEach(section => {
                const sectionHeight = section.offsetHeight;
                const sectionTop = section.offsetTop - 120;
                const sectionId = section.getAttribute('id');
                const targetLink = document.querySelector(`.navbar-nav a[href*="#${sectionId}"]`);

                if (targetLink && scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                    document.querySelectorAll('.navbar-nav .nav-link').forEach(l => l.classList.remove('active'));
                    targetLink.classList.add('active');
                }
            });
        }, { passive: true });
    }

    /* ----------------------------------------------------------------------
       6. STAT NUMBER ACCENT ANIMATION
       ---------------------------------------------------------------------- */
    const statCards = document.querySelectorAll('.stat-card');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-stat');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        statCards.forEach(c => observer.observe(c));
    }
});
