/* Nima Premium Motion
   Subtle progressive enhancement only; core experience remains fully functional without JS. */
(function () {
  'use strict';

  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  document.documentElement.classList.add('nima-motion');

  function markRevealTargets() {
    var selectors = [
      '.template-index .hero-copy',
      '.template-index .hero-art',
      '.template-index .shop-window__head',
      '.template-index .shop-window__item',
      '.template-index .magazine-teaser',
      '.template-collection .collection-head',
      '.template-collection .collection-visual',
      '.template-collection .product-grid > *',
      '.template-product .gallery',
      '.template-product .buy',
      '.template-search .search-page__intro',
      '.template-search .search-form',
      '.template-search .product-grid > *',
      '.template-cart .cart-item',
      '.template-cart .cart-summary',
      '.mag-hero__content',
      '.mag-grid .feature',
      '.mag-grid .side-story'
    ];

    selectors.forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (node, index) {
        if (node.hasAttribute('data-nima-reveal')) return;
        var media = node.matches('.hero-art,.collection-visual,.gallery,.mag-grid .feature');
        node.setAttribute('data-nima-reveal', media ? 'media' : 'content');
        node.style.transitionDelay = Math.min(index * 45, 180) + 'ms';
      });
    });
  }

  function revealAllPending() {
    document.querySelectorAll('[data-nima-reveal]:not(.is-visible)').forEach(function (target) {
      target.classList.add('is-visible');
    });
  }

  function reveal() {
    markRevealTargets();
    var targets = document.querySelectorAll('[data-nima-reveal]');
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -4% 0px' });

    targets.forEach(function (target) { observer.observe(target); });

    /* Motion is enhancement, never a visibility dependency. If an observer is
       throttled, a layout shift occurs, or a browser misses an intersection,
       make every remaining target visible after the entrance window. */
    window.setTimeout(function () {
      revealAllPending();
      observer.disconnect();
    }, 1800);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', reveal, { once: true });
  } else {
    reveal();
  }
})();
