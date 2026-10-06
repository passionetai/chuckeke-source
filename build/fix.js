document.addEventListener('DOMContentLoaded', function () {
  // Astro's ClientRouter normally dispatches this on load — polyfill it
  window.dispatchEvent(new Event('astro:page-load'));

  // Layout.js normally adds reveal-in on scroll; make everything visible immediately
  document.querySelectorAll('.reveal-init').forEach(function (el) {
    el.classList.add('reveal-in');
  });

  // Hero script expects is-ready on the hero element
  var hero = document.querySelector('.hero');
  if (hero) hero.classList.add('is-ready');
});
