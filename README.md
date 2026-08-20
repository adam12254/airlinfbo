# Airlin FBO — website

Static site for Airlin FBO, Fujairah International Airport.
Seven pages, no CMS, no database, no build dependencies beyond Python 3.

Live preview: https://adam12254.github.io/airlinfbo

---

## Structure

```
├── build.py              generator — run after editing content
├── index.html            \
├── facilities.html        |
├── collaborations.html    |
├── why-airlin-fbo.html    > generated; edit build.py, not these
├── about.html             |
├── careers.html           |
├── contact.html          /
└── assets/
    ├── css/site.css      design system, single stylesheet
    ├── js/site.js        header, menu, slider, counters, form
    └── img/              photography and icons
```

## Building

```bash
python3 build.py
```

The header, footer, floating buttons and CTA band are defined once in
`build.py`, so a change to any of them lands on all seven pages. The build
fails if a page emits a modifier class with no matching CSS rule.

Do not hand-edit the `.html` files — they are regenerated and your changes
will be overwritten. Content lives in `build.py`; styling lives in
`assets/css/site.css`.

## Previewing locally

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

---

## Conventions worth knowing

**Colour.** `--gold` (`#C9A861`) is a fill colour only — it measures 2.27:1 on
white and fails WCAG AA as text. Gold *text* on light backgrounds uses
`--gold-text` (`#8A6D2F`); on dark backgrounds use `--gold-bright`.

**Asset URLs carry a `?v=` stamp** keyed to file modification time, applied at
build time. Filenames are stable while contents are not, and static hosts send
no `Cache-Control`, so without this an updated stylesheet or image can keep
serving stale bytes after deploy.

**Progressive enhancement.** Every interaction degrades: the nav is a plain
`<nav>`, the testimonial slider is a scroll-snap strip that already swipes, and
the scroll-reveal hidden state is gated behind a class only `site.js` adds — so
a blocked script can never leave the page blank.

**Accessibility.** WCAG AA contrast throughout, 44 × 44 px minimum tap targets,
visible focus rings, and `prefers-reduced-motion` honoured. Verified across
seven pages and four viewports. Please keep it that way.

## Deploying

Any static host will serve this — it is plain HTML, CSS, JS and images.

- **GitHub Pages:** Settings → Pages → Deploy from branch → `main` / root.
- **Custom domain:** add a `CNAME` file at the repo root containing the domain,
  then point the DNS at GitHub Pages.
- **Traditional hosting:** upload the repository contents to the web root.

## Licence and content

Copy and imagery are the property of Airlin FBO FZ LLC and are not licensed for
reuse. Some photography is placeholder material pending a commissioned shoot —
check with the owner before treating any image as final.
