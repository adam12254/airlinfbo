/* Airlin FBO — progressive enhancement only.

   Every feature here degrades to something usable:
   - the nav panel is a plain <nav> the CSS hides at narrow widths
   - the slider is a scroll-snap strip that already swipes without JS
   - the reveal animation's hidden state is gated behind a class only this file adds
   - the contact form validates natively and falls back to a mailto: link
*/
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --------------------------------------------------------------- header */

  var header = document.querySelector('.site-header');
  if (header) {
    var ticking = false;
    var sync = function () {
      header.classList.toggle('is-stuck', window.scrollY > 8);
      ticking = false;
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(sync); ticking = true; }
    }, { passive: true });
    sync();
  }

  /* ------------------------------------------------------------ mobile nav */

  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('primary-nav');

  if (toggle && nav) {
    var setOpen = function (open) {
      nav.dataset.open = open ? 'true' : 'false';
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    setOpen(false);

    toggle.addEventListener('click', function () { setOpen(nav.dataset.open !== 'true'); });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.dataset.open === 'true') { setOpen(false); toggle.focus(); }
    });

    document.addEventListener('click', function (e) {
      if (nav.dataset.open !== 'true') return;
      if (nav.contains(e.target) || toggle.contains(e.target)) return;
      setOpen(false);
    });

    var mq = window.matchMedia('(min-width: 981px)');
    var onChange = function (e) { if (e.matches) setOpen(false); };
    if (mq.addEventListener) mq.addEventListener('change', onChange);
    else if (mq.addListener) mq.addListener(onChange);
  }

  /* --------------------------------------------------------- scroll reveal */

  var REVEAL_MS = 900;
  var revealTargets = document.querySelectorAll('.js-reveal');

  if (revealTargets.length && !reduced && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('js-reveal-ready');

    /* Items inside a grid arrive in sequence. The delay is capped so a long
       grid never leaves the last card lagging seconds behind the first. */
    document.querySelectorAll('.grid, .quotes, .slider__track').forEach(function (group) {
      Array.prototype.slice.call(group.children).forEach(function (el, i) {
        if (el.classList.contains('js-reveal')) {
          el.style.setProperty('--reveal-delay', Math.min(i, 5) * 80 + 'ms');
        }
      });
    });

    /* Retire the classes once the entrance has played, so the reveal rules stop
       outranking :hover. A timer rather than transitionend: transitionend never
       fires if the tab is hidden while the item is revealed, which would strand
       the card with its hover disabled. */
    var settle = function (el) {
      var delay = parseFloat(el.style.getPropertyValue('--reveal-delay')) || 0;
      window.setTimeout(function () {
        el.classList.remove('js-reveal', 'is-in');
        el.style.removeProperty('--reveal-delay');
      }, delay + REVEAL_MS + 120);
    };

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        settle(entry.target);
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.06 });

    revealTargets.forEach(function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight) {
        el.classList.add('is-in');
        settle(el);
      } else {
        io.observe(el);
      }
    });
  }

  /* ------------------------------------------------------------- counters */
  /* Animates the leading number of a stat ("35 PAX", "20+ Positions") while
     leaving the rest of the string alone. Zero padding is preserved so
     "01 Available" doesn't finish as "1 Available". */

  function initCounters() {
    var stats = document.querySelectorAll('.stat__value');
    if (!stats.length) return;

    var animate = function (el) {
      var raw = el.textContent;
      var match = raw.match(/^(\d+)/);
      if (!match) return;

      var target = parseInt(match[1], 10);
      var pad = match[1].length;
      var rest = raw.slice(match[1].length);
      if (target === 0) return;

      var finish = function () { el.textContent = String(target).padStart(pad, '0') + rest; };

      /* rAF is paused while the document is hidden, so a counter started in a
         background tab would freeze part-way and display "12 PAX" forever.
         Jump straight to the final value instead of animating to nowhere. */
      if (document.hidden) { finish(); return; }

      var start = null;
      var dur = 1100;
      var step = function (now) {
        if (document.hidden) { finish(); return; }
        if (start === null) start = now;
        var t = Math.min((now - start) / dur, 1);
        var eased = 1 - Math.pow(1 - t, 3);
        if (t >= 1) { finish(); return; }
        el.textContent = String(Math.round(target * eased)).padStart(pad, '0') + rest;
        window.requestAnimationFrame(step);
      };
      window.requestAnimationFrame(step);
    };

    if (reduced || !('IntersectionObserver' in window)) return; // leave final values in place

    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        animate(entry.target);
        cio.unobserve(entry.target);
      });
    }, { threshold: 0.5 });

    stats.forEach(function (el) { cio.observe(el); });
  }
  initCounters();

  /* --------------------------------------------------------------- slider */

  var ARROW = {
    prev: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.4 7.4 14 6l-6 6 6 6 1.4-1.4-4.6-4.6z"/></svg>',
    next: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.6 16.6 10 18l6-6-6-6-1.4 1.4 4.6 4.6z"/></svg>'
  };

  document.querySelectorAll('[data-slider]').forEach(function (slider) {
    var track = slider.querySelector('.slider__track');
    if (!track) return;
    var slides = Array.prototype.slice.call(track.children);
    if (slides.length < 2) return;

    var controls = document.createElement('div');
    controls.className = 'slider__controls';

    var dots = document.createElement('div');
    dots.className = 'slider__dots';
    dots.setAttribute('role', 'tablist');
    dots.setAttribute('aria-label', 'Choose testimonial');

    var arrows = document.createElement('div');
    arrows.className = 'slider__arrows';

    var mkArrow = function (dir, label) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'slider__arrow';
      b.setAttribute('aria-label', label);
      b.innerHTML = ARROW[dir];
      return b;
    };
    var prev = mkArrow('prev', 'Previous testimonials');
    var next = mkArrow('next', 'Next testimonials');
    arrows.appendChild(prev);
    arrows.appendChild(next);

    /* All positions are derived from real offsetLeft values rather than
       width+gap arithmetic. Deriving them arithmetically produced positions
       that scroll-snap then rejected, leaving the track stuck. */
    var offsetOf = function (i) { return slides[i].offsetLeft - slides[0].offsetLeft; };

    /* One dot per scroll position, not per slide — with three visible at a
       time, six slides is four stops, and a dot per slide would misreport. */
    var pageCount = function () {
      var last = offsetOf(slides.length - 1) + slides[slides.length - 1].offsetWidth;
      if (last <= track.clientWidth + 1) return 1;   // everything already fits
      var perView = Math.max(1, Math.round(track.clientWidth / (offsetOf(1) || slides[0].offsetWidth)));
      return Math.max(1, slides.length - perView + 1);
    };

    var buttons = [];
    var buildDots = function () {
      dots.innerHTML = '';
      buttons = [];
      var n = pageCount();
      for (var i = 0; i < n; i++) {
        (function (idx) {
          var d = document.createElement('button');
          d.type = 'button';
          d.className = 'slider__dot';
          d.setAttribute('role', 'tab');
          d.setAttribute('aria-label', 'Testimonial ' + (idx + 1));
          d.addEventListener('click', function () { goTo(idx); });
          dots.appendChild(d);
          buttons.push(d);
        })(i);
      }
    };

    var currentIndex = function () {
      var x = track.scrollLeft, best = 0, bestDist = Infinity;
      for (var i = 0; i < slides.length; i++) {
        var d = Math.abs(offsetOf(i) - x);
        if (d < bestDist) { bestDist = d; best = i; }
      }
      return Math.min(best, Math.max(0, buttons.length - 1));
    };

    var goTo = function (i) {
      i = Math.max(0, Math.min(slides.length - 1, i));
      track.scrollTo({ left: offsetOf(i), behavior: reduced ? 'auto' : 'smooth' });
    };

    var syncState = function () {
      var i = currentIndex();
      var n = buttons.length;
      buttons.forEach(function (b, idx) { b.setAttribute('aria-selected', idx === i ? 'true' : 'false'); });
      prev.disabled = i <= 0;
      next.disabled = i >= n - 1;
    };

    prev.addEventListener('click', function () { goTo(Math.max(0, currentIndex() - 1)); });
    next.addEventListener('click', function () { goTo(Math.min(buttons.length - 1, currentIndex() + 1)); });

    /* The track is a scroll container, so it must be keyboard reachable. */
    track.setAttribute('tabindex', '0');
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); goTo(Math.min(buttons.length - 1, currentIndex() + 1)); }
      if (e.key === 'ArrowLeft')  { e.preventDefault(); goTo(Math.max(0, currentIndex() - 1)); }
    });

    var scrollTick = false;
    track.addEventListener('scroll', function () {
      if (scrollTick) return;
      scrollTick = true;
      window.requestAnimationFrame(function () { syncState(); scrollTick = false; });
    }, { passive: true });

    /* If the tab is backgrounded mid-scroll the queued frame never runs, so
       scrollTick stays true and the dots stop tracking for good. Re-sync and
       clear the latch when the page comes back. */
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) return;
      scrollTick = false;
      syncState();
    });

    controls.appendChild(dots);
    controls.appendChild(arrows);
    slider.appendChild(controls);

    buildDots();
    syncState();

    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () { buildDots(); syncState(); }, 150);
    });
  });

  /* -------------------------------------------------------------- marquee */
  /* Drive the loop at a constant speed instead of a constant duration. The
     track holds the list twice and travels -50%, so the distance covered per
     cycle is half its width — which changes with the type size, the copy and
     the viewport. Pinning the duration instead would make the strip visibly
     faster every time any of those grew. */

  var MARQUEE_PX_PER_SEC = 46;

  document.querySelectorAll('.marquee').forEach(function (strip) {
    var track = strip.querySelector('.marquee__track');
    if (!track) return;

    var setPace = function () {
      var distance = track.scrollWidth / 2;
      if (!distance) return;
      track.style.setProperty('--marquee-duration',
        (distance / MARQUEE_PX_PER_SEC).toFixed(2) + 's');
    };

    setPace();
    /* Webfonts land after first paint and change the measurement. */
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(setPace);
    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt); rt = setTimeout(setPace, 200);
    });
  });

  /* ------------------------------------------------------ hero slideshow */
  /* Cross-fades the hero stack. The first slide already has .is-active from the
     markup, so with this script blocked the hero is simply a static photograph.
     Paused while the tab is hidden, since the fades would otherwise all stack
     up and fire at once on return. */

  var stage = document.querySelector('[data-hero-slideshow]');
  if (stage && !reduced) {
    var shots = Array.prototype.slice.call(stage.querySelectorAll('img'));
    if (shots.length > 1) {
      var at = 0, timer = null;
      var advance = function () {
        shots[at].classList.remove('is-active');
        at = (at + 1) % shots.length;
        shots[at].classList.add('is-active');
      };
      var play = function () { if (!timer) timer = setInterval(advance, 6000); };
      var halt = function () { clearInterval(timer); timer = null; };

      document.addEventListener('visibilitychange', function () {
        if (document.hidden) halt(); else play();
      });
      play();
    }
  }

  /* ------------------------------------------------------------- parallax */

  /* Every slide in the stack drifts together — moving only the first would
     leave the others static and the cross-fade would visibly jump. */
  var heroImgs = Array.prototype.slice.call(document.querySelectorAll('.hero__media img'));
  if (heroImgs.length && !reduced) {
    var pTick = false;
    var drift = function () {
      var y = window.scrollY;
      if (y < window.innerHeight) {
        var t = 'translate3d(0,' + (y * 0.18) + 'px,0) scale(1.06)';
        heroImgs.forEach(function (im) { im.style.transform = t; });
      }
      pTick = false;
    };
    heroImgs.forEach(function (im) {
      im.style.willChange = 'transform';
      im.style.transform = 'scale(1.06)';
    });
    window.addEventListener('scroll', function () {
      if (!pTick) { window.requestAnimationFrame(drift); pTick = true; }
    }, { passive: true });
  }

  /* ----------------------------------------------------------------- form */

  var form = document.querySelector('[data-enquiry]');
  if (form) {
    var status = form.querySelector('.form__status');

    var showError = function (field, msg) {
      field.dataset.invalid = 'true';
      var slot = field.querySelector('.field__error');
      if (slot) slot.textContent = msg;
      var input = field.querySelector('input, textarea, select');
      if (input) input.setAttribute('aria-invalid', 'true');
    };
    var clearError = function (field) {
      field.dataset.invalid = 'false';
      var slot = field.querySelector('.field__error');
      if (slot) slot.textContent = '';
      var input = field.querySelector('input, textarea, select');
      if (input) input.removeAttribute('aria-invalid');
    };

    form.querySelectorAll('.field input, .field textarea').forEach(function (input) {
      input.addEventListener('input', function () {
        if (input.closest('.field').dataset.invalid === 'true' && input.checkValidity()) {
          clearError(input.closest('.field'));
        }
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstBad = null;

      form.querySelectorAll('.field').forEach(function (field) {
        var input = field.querySelector('input, textarea, select');
        if (!input) return;
        if (!input.checkValidity()) {
          var msg = input.validity.valueMissing
            ? 'This field is required.'
            : (input.type === 'email' ? 'Enter a valid email address.' : 'Check this value.');
          showError(field, msg);
          if (!firstBad) firstBad = input;
        } else {
          clearError(field);
        }
      });

      if (firstBad) {
        if (status) { status.dataset.state = 'error'; status.textContent = 'Please correct the highlighted fields.'; }
        firstBad.focus();
        return;
      }

      /* No endpoint configured, so hand off to the visitor's mail client
         rather than silently dropping the enquiry. See README to wire this to
         a real form service. */
      var get = function (n) { var el = form.elements[n]; return el ? el.value.trim() : ''; };
      var body = [
        'Name: ' + get('name'),
        'Email: ' + get('email'),
        'Company: ' + (get('company') || '—'),
        'Aircraft / registration: ' + (get('aircraft') || '—'),
        'Date of movement: ' + (get('date') || '—'),
        '',
        get('message')
      ].join('\n');

      var href = 'mailto:' + form.dataset.enquiry +
                 '?subject=' + encodeURIComponent('Handling enquiry — ' + get('name')) +
                 '&body=' + encodeURIComponent(body);

      if (status) {
        status.dataset.state = 'ok';
        status.textContent = 'Opening your email client with the enquiry ready to send…';
      }
      window.location.href = href;
    });
  }
})();
