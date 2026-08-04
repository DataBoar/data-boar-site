/**
 * combobox.js — transforma um <input list> + <datalist> num campo de busca
 * estilo HubSpot (caixa de texto + dropdown filtrável), sem dependências.
 * Se este script não rodar, o <datalist> nativo continua funcionando (fallback).
 */
(function () {
  'use strict';

  var MAX_RENDER = 80;

  function enhance(input) {
    var listId = input.getAttribute('list');
    var datalist = listId && document.getElementById(listId);
    if (!datalist) return;

    var options = Array.prototype.map.call(
      datalist.querySelectorAll('option'),
      function (o) {
        return o.value;
      }
    );
    if (!options.length) return;

    // Desativa o datalist nativo (evita UI dupla) — só quando o JS roda.
    input.removeAttribute('list');
    input.setAttribute('autocomplete', 'off');
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');

    var wrap = document.createElement('div');
    wrap.className = 'cbx-wrap';
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);

    var menu = document.createElement('ul');
    menu.className = 'cbx-menu';
    menu.setAttribute('role', 'listbox');
    menu.hidden = true;
    wrap.appendChild(menu);

    var active = -1;

    function open(show) {
      menu.hidden = !show;
      input.setAttribute('aria-expanded', show ? 'true' : 'false');
      if (!show) active = -1;
    }

    function choose(value) {
      input.value = value;
      open(false);
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }

    function render(query) {
      var q = (query || '').trim().toLowerCase();
      var filtered = q
        ? options.filter(function (o) {
            return o.toLowerCase().indexOf(q) > -1;
          })
        : options.slice();

      menu.textContent = '';
      filtered.slice(0, MAX_RENDER).forEach(function (value) {
        var li = document.createElement('li');
        li.className = 'cbx-opt';
        li.setAttribute('role', 'option');
        li.textContent = value;
        li.addEventListener('mousedown', function (e) {
          e.preventDefault();
          choose(value);
        });
        menu.appendChild(li);
      });
      active = -1;
      open(filtered.length > 0);
    }

    function move(delta) {
      var items = menu.querySelectorAll('.cbx-opt');
      if (!items.length) return;
      active = (active + delta + items.length) % items.length;
      Array.prototype.forEach.call(items, function (el, i) {
        el.classList.toggle('is-active', i === active);
      });
      items[active].scrollIntoView({ block: 'nearest' });
    }

    input.addEventListener('focus', function () {
      render(input.value);
    });
    input.addEventListener('input', function () {
      render(input.value);
    });
    input.addEventListener('keydown', function (e) {
      if (menu.hidden && e.key === 'ArrowDown') {
        render(input.value);
        return;
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        move(1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        move(-1);
      } else if (e.key === 'Enter') {
        var items = menu.querySelectorAll('.cbx-opt');
        if (!menu.hidden && active > -1 && items[active]) {
          e.preventDefault();
          choose(items[active].textContent);
        }
      } else if (e.key === 'Escape') {
        open(false);
      }
    });

    document.addEventListener('click', function (e) {
      if (!wrap.contains(e.target)) open(false);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var el = document.getElementById('demo-industria');
    if (el && el.getAttribute('list')) enhance(el);
  });
})();
