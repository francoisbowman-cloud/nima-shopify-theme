/* PetDrop theme — interacciones mínimas sin dependencias.
   - Toggle del menú móvil
   - Galería de producto (thumbnails)
   - Selección de variantes + add to cart vía AJAX Cart API
   - Actualización del contador del carrito */

(function () {
  'use strict';

  /* ---- Menú móvil ---- */
  document.addEventListener('click', function (e) {
    var toggle = e.target.closest('[data-nav-toggle]');
    if (!toggle) return;
    var nav = document.querySelector('[data-navlinks]');
    if (!nav) return;
    var open = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  /* ---- Galería de producto ---- */
  document.addEventListener('click', function (e) {
    var thumb = e.target.closest('[data-gallery-thumb]');
    if (!thumb) return;
    var main = document.querySelector('[data-gallery-main]');
    if (main) main.src = thumb.getAttribute('data-full');
  });

  /* ---- Contador del carrito ---- */
  function refreshCartCount() {
    fetch('/cart.js', { headers: { Accept: 'application/json' } })
      .then(function (r) { return r.json(); })
      .then(function (cart) {
        document.querySelectorAll('[data-cart-count]').forEach(function (el) {
          el.textContent = cart.item_count;
        });
      })
      .catch(function () {});
  }

  /* ---- Add to cart ---- */
  document.addEventListener('submit', function (e) {
    var form = e.target.closest('[data-product-form]');
    if (!form) return;
    e.preventDefault();

    var btn = form.querySelector('[data-add-btn]');
    var original = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = btn.getAttribute('data-adding') || 'Añadiendo…'; }

    fetch('/cart/add.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        id: form.querySelector('[name="id"]').value,
        quantity: 1
      })
    })
      .then(function (r) {
        if (!r.ok) throw new Error('add-failed');
        return r.json();
      })
      .then(function () {
        refreshCartCount();
        if (btn) { btn.textContent = btn.getAttribute('data-added') || 'Añadido ✓'; }
        setTimeout(function () {
          if (btn) { btn.disabled = false; btn.textContent = original; }
        }, 1600);
      })
      .catch(function () {
        if (btn) { btn.disabled = false; btn.textContent = original; }
        alert('No se pudo añadir al carrito. Intentá de nuevo.');
      });
  });

  /* ---- Selección de variante: actualiza el input hidden [name=id] ---- */
  document.addEventListener('change', function (e) {
    var input = e.target.closest('[data-variant-option]');
    if (!input) return;
    var form = input.closest('[data-product-form]');
    if (!form) return;
    var idInput = form.querySelector('[name="id"]');
    if (idInput && input.value) idInput.value = input.value;
  });

  document.addEventListener('DOMContentLoaded', refreshCartCount);

  /* ---- Catálogo: filtro por categoría (chips) ---- */
  document.addEventListener('click', function (e) {
    var chip = e.target.closest('[data-filter-chip]');
    if (!chip) return;
    var bar = chip.closest('[data-catalog-filter]');
    if (!bar) return;
    var grid = bar.parentElement.querySelector('[data-product-grid]');
    if (!grid) return;

    bar.querySelectorAll('[data-filter-chip]').forEach(function (c) {
      c.classList.remove('filterbar__chip--active');
    });
    chip.classList.add('filterbar__chip--active');

    var category = chip.getAttribute('data-category');
    var cards = grid.querySelectorAll('[data-category]');
    var visible = 0;
    cards.forEach(function (card) {
      var match = category === 'all' || card.getAttribute('data-category') === category;
      card.style.display = match ? '' : 'none';
      if (match) visible += 1;
    });

    var count = bar.querySelector('[data-filter-count]');
    if (count) count.textContent = visible + ' ' + (count.getAttribute('data-label') || 'productos');
  });
})();
