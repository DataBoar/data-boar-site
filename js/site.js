(function () {
  'use strict';

  var header = document.querySelector('header');
  var toggle = document.querySelector('.nav-toggle');
  var overlay = document.querySelector('.nav-overlay');
  var siteNav = document.getElementById('site-nav');

  // Language of the page: <html lang> says it (PT root pages, /en/ pages, and the
  // single-URL pages login/agende, whose panels applyLanguage() toggles).
  var currentLang = document.documentElement.lang === 'en' ? 'en' : 'pt-BR';
  var navLabels = {
    'pt-BR': { open: 'Abrir menu de navegação', close: 'Fechar menu de navegação' },
    en: { open: 'Open navigation menu', close: 'Close navigation menu' }
  };

  function navLabel(open) {
    return navLabels[currentLang][open ? 'close' : 'open'];
  }

  function setNavOpen(open) {
    if (!header || !toggle) return;
    header.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', navLabel(open));
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

  function rememberLang(lang) {
    try {
      localStorage.setItem('databoar-lang', lang);
    } catch (err) {
      /* ignore */
    }
  }

  // The language twin of this page, from <link rel="alternate" hreflang>. Pages that
  // have one (the PT root page and its /en/ page) switch language by navigating to it.
  // Pages without one (login, agende) keep toggling their panels in place.
  function twinHref(lang) {
    var link = document.querySelector('link[rel="alternate"][hreflang="' + lang + '"]');
    if (!link) return null;
    var href = link.getAttribute('href');
    try {
      var target = new URL(href, window.location.href);
      return window.location.origin !== 'null' ? window.location.origin + target.pathname : href;
    } catch (err) {
      return href;
    }
  }

  var hasTwin = !!(twinHref('en') && twinHref('pt-BR'));

  function applyLanguage(lang) {
    var resolved = lang === 'en' ? 'en' : 'pt-BR';
    currentLang = resolved;
    document.documentElement.lang = resolved === 'en' ? 'en' : 'pt-BR';
    rememberLang(resolved);
    if (toggle && header) {
      toggle.setAttribute('aria-label', navLabel(header.classList.contains('nav-open')));
    }
    document.querySelectorAll('[data-lang-panel]').forEach(function (panel) {
      var match = panel.getAttribute('data-lang-panel') === resolved;
      if (match) {
        panel.removeAttribute('hidden');
      } else {
        panel.setAttribute('hidden', '');
      }
    });
    // Swap placeholders/aria in form fields by language (single form, no duplication)
    document.querySelectorAll('[data-ph-en],[data-ph-pt-BR]').forEach(function (el) {
      var ph = el.getAttribute('data-ph-' + resolved);
      if (ph !== null) el.setAttribute('placeholder', ph);
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
      var lang = this.dataset.lang === 'en' ? 'en' : 'pt-BR';
      if (hasTwin) {
        document.querySelectorAll('.lang-menu').forEach(function (menu) {
          menu.classList.remove('open');
        });
        if (lang !== currentLang) {
          rememberLang(lang);
          window.location.href = twinHref(lang);
        }
        return;
      }
      applyLanguage(lang);
    });
  });

  // No language detection by browser and no redirect: the URL decides the language.
  // Single-URL pages only remember the last language chosen (or the last language page visited).
  function savedLang() {
    try {
      var saved = localStorage.getItem('databoar-lang');
      if (saved === 'en' || saved === 'pt-BR') return saved;
    } catch (e) {
      /* ignore */
    }
    return 'pt-BR';
  }

  if (hasTwin) {
    rememberLang(currentLang);
  } else if (document.querySelector('[data-lang-panel]')) {
    applyLanguage(savedLang());
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
