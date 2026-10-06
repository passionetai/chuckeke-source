// Stand-in for the original Astro bundles (ClientRouter, Layout, ConstellationMap),
// which are not in this repo.
(function () {
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Fade sections in as they enter the viewport. They reset once fully off screen,
  // so they fade in again on the next pass.
  function initReveal() {
    var els = document.querySelectorAll('[data-reveal]');
    if (!('IntersectionObserver' in window) || reducedMotion) {
      els.forEach(function (el) { el.classList.add('reveal-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var el = entry.target;
        if (entry.isIntersecting) {
          el.style.transitionDelay = (parseInt(el.getAttribute('data-reveal-delay'), 10) || 0) + 'ms';
          el.classList.add('reveal-in');
        } else if (entry.intersectionRatio === 0) {
          el.style.transitionDelay = '0ms';
          el.classList.remove('reveal-in');
        }
      });
    }, { threshold: [0, 0.12], rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  }

  // Switch the nav to its light-on-dark style while it sits over a navy section.
  function initNavTheme() {
    var nav = document.getElementById('site-nav');
    if (!nav) return;
    var dark = Array.prototype.filter.call(document.querySelectorAll('.bg-navy'), function (el) {
      return !nav.contains(el);
    });
    var queued = false;
    function update() {
      queued = false;
      var y = nav.offsetHeight / 2;
      var overDark = dark.some(function (el) {
        var r = el.getBoundingClientRect();
        return r.top <= y && r.bottom >= y && r.width > window.innerWidth / 2;
      });
      nav.classList.toggle('is-dark', overDark);
    }
    function schedule() {
      if (!queued) { queued = true; requestAnimationFrame(update); }
    }
    update();
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
  }

  // About page: draw the spokes, highlight a spoke on hover/focus, show its caption,
  // and open the matching link (taken from the mobile list, which is in the same order).
  function initConstellation() {
    var root = document.querySelector('.constellation');
    if (!root) return;
    var lines = root.querySelectorAll('.c-line');
    var nodes = root.querySelectorAll('.c-node');
    var items = root.querySelectorAll('ul > li');
    var caption = root.querySelector('.c-caption');
    var defaultCaption = caption ? caption.innerHTML : '';

    function draw() {
      lines.forEach(function (line, i) {
        setTimeout(function () { line.classList.add('is-drawn'); }, reducedMotion ? 0 : i * 90);
      });
    }
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries.some(function (e) { return e.isIntersecting; })) { draw(); io.disconnect(); }
      }, { threshold: 0.25 });
      io.observe(root);
    } else {
      draw();
    }

    nodes.forEach(function (node, i) {
      var item = items[i];
      var link = item ? item.querySelector('a') : null;
      function on() {
        node.classList.add('is-active');
        if (lines[i]) lines[i].classList.add('is-active');
        if (caption && item) caption.innerHTML = (link || item).innerHTML;
      }
      function off() {
        node.classList.remove('is-active');
        if (lines[i]) lines[i].classList.remove('is-active');
        if (caption) caption.innerHTML = defaultCaption;
      }
      function go() {
        if (!link) return;
        if (link.target === '_blank') window.open(link.href, '_blank', 'noopener');
        else window.location.href = link.href;
      }
      node.addEventListener('mouseenter', on);
      node.addEventListener('mouseleave', off);
      node.addEventListener('focus', on);
      node.addEventListener('blur', off);
      node.addEventListener('click', go);
      node.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    // The page's own scripts (nav, mobile menu, hero video, counters, slideshow,
    // copy buttons, contact form) listen for this on document; ClientRouter used to send it.
    document.dispatchEvent(new Event('astro:page-load'));

    var hero = document.querySelector('.hero');
    if (hero) hero.classList.add('is-ready');

    initReveal();
    initNavTheme();
    initConstellation();
  });
})();
