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

  document.querySelectorAll('.lang-option').forEach(function (opt) {
    opt.addEventListener('click', function (event) {
      event.preventDefault();
      document.querySelectorAll('.lang-option').forEach(function (o) {
        o.classList.remove('selected');
      });
      this.classList.add('selected');
      var langBtn = document.querySelector('.lang-btn');
      if (langBtn) {
        var code = langBtn.querySelector('.lang-code');
        var flag = langBtn.querySelector('.lang-flag');
        if (code) {
          code.textContent = this.dataset.lang === 'en' ? 'EN' : 'PT-BR';
        }
        if (flag) {
          flag.textContent = this.dataset.flag;
        }
      }
      var menu = this.closest('.lang-menu');
      if (menu) {
        menu.classList.remove('open');
      }
      var activeBtn = document.querySelector('.lang-btn');
      if (activeBtn) {
        activeBtn.setAttribute('aria-expanded', 'false');
      }
    });
  });

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
