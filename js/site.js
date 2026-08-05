(function () {
  'use strict';

  var header = document.querySelector('header');
  var toggle = document.querySelector('.nav-toggle');
  var overlay = document.querySelector('.nav-overlay');
  var siteNav = document.getElementById('site-nav');

  function setNavOpen(open) {
    if (!header || !toggle) return;
    header.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute(
      'aria-label',
      open ? 'Fechar menu de navegação' : 'Abrir menu de navegação'
    );
    if (overlay) {
      overlay.setAttribute('aria-hidden', open ? 'false' : 'true');
    }
    document.body.classList.toggle('nav-menu-open', open);
  }

  if (toggle && siteNav) {
    toggle.addEventListener('click', function () {
      setNavOpen(!header.classList.contains('nav-open'));
    });

    if (overlay) {
      overlay.addEventListener('click', function () {
        setNavOpen(false);
      });
    }

    siteNav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        setNavOpen(false);
      });
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        setNavOpen(false);
      }
    });
  }

  document.querySelectorAll('.lang-btn').forEach(function (btn) {
    btn.addEventListener('click', function (event) {
      event.stopPropagation();
      var menu = this.nextElementSibling;
      if (!menu) return;
      var open = menu.classList.toggle('open');
      this.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  function applyLanguage(lang) {
    var resolved = lang === 'en' ? 'en' : 'pt-BR';
    document.documentElement.lang = resolved === 'en' ? 'en' : 'pt-BR';
    try {
      localStorage.setItem('databoar-lang', resolved);
    } catch (err) {
      /* ignore */
    }
    document.querySelectorAll('[data-lang-panel]').forEach(function (panel) {
      var match = panel.getAttribute('data-lang-panel') === resolved;
      if (match) {
        panel.removeAttribute('hidden');
      } else {
        panel.setAttribute('hidden', '');
      }
    });
    document.querySelectorAll('.lang-option').forEach(function (o) {
      o.classList.toggle('selected', o.dataset.lang === resolved);
    });
    var langBtn = document.querySelector('.lang-btn');
    if (langBtn) {
      var code = langBtn.querySelector('.lang-code');
      var flag = langBtn.querySelector('.lang-flag');
      var selected = document.querySelector('.lang-option.selected');
      if (code) {
        code.textContent = resolved === 'en' ? 'EN' : 'PT-BR';
      }
      if (flag && selected) {
        flag.textContent = selected.dataset.flag;
      }
      langBtn.setAttribute('aria-expanded', 'false');
    }
    document.querySelectorAll('.lang-menu').forEach(function (menu) {
      menu.classList.remove('open');
    });
  }

  document.querySelectorAll('.lang-option').forEach(function (opt) {
    opt.addEventListener('click', function (event) {
      event.preventDefault();
      applyLanguage(this.dataset.lang);
    });
  });

  function detectLang() {
    try {
      var saved = localStorage.getItem('databoar-lang');
      if (saved === 'en' || saved === 'pt-BR') return saved;
    } catch (e) {
      /* ignore */
    }
    // 1a visita: detecta pelo navegador. pt* -> PT-BR; qualquer outro -> EN.
    var nav = (navigator.language || navigator.userLanguage || 'pt-BR').toLowerCase();
    return nav.indexOf('pt') === 0 ? 'pt-BR' : 'en';
  }

  if (document.querySelector('[data-lang-panel]')) {
    applyLanguage(detectLang());
  }

  document.addEventListener('click', function (event) {
    if (!event.target.closest('.lang-switch')) {
      document.querySelectorAll('.lang-menu').forEach(function (menu) {
        menu.classList.remove('open');
      });
      document.querySelectorAll('.lang-btn').forEach(function (btn) {
        btn.setAttribute('aria-expanded', 'false');
      });
    }
  });
})();
