# SEO Design Spec

## Goal

Improve search engine discoverability (local search for "pickleball singles St. Louis" etc.) and social sharing previews across all public pages. The site is a React SPA served as static files on Render.

## Approach

react-helmet-async (v3+) for per-page meta tags + vite-prerender-plugin for static HTML generation + JSON-LD structured data for events + static robots.txt and sitemap.xml.

---

## 1. Per-Page Meta Tags (react-helmet-async@^3.0.0)

**Version note:** v3.0.0+ is required for React 19 compatibility. Earlier versions are broken with React 19.

Wrap the app in `<HelmetProvider>` in `main.jsx`. Each public page gets a `<Helmet>` block with unique title, description, OG tags (including `og:image`), Twitter Card tags, and canonical URL.

### Page meta mapping

| Route | Title | Description |
|---|---|---|
| `/` | Pickleball Singles Social - Meet Singles Through Pickleball in St. Louis | Social pickleball events for singles in St. Louis. Play mixed doubles, meet new people, and connect through the fastest-growing sport in America. |
| `/about` | About - Pickleball Singles Social | Learn about Pickleball Singles Social, volunteer-run singles pickleball events in St. Louis by Gateway Smash. |
| `/faq` | FAQ - Pickleball Singles Social | Common questions about our singles pickleball events: skill level, matching, pricing, what to bring, and more. |
| `/code-of-conduct` | Code of Conduct - Pickleball Singles Social | Our community guidelines for a safe, respectful, and fun experience at every event. |
| `/events` | Upcoming Events - Pickleball Singles Social | Browse and register for upcoming singles pickleball events in St. Louis. |
| `/events/:id/register` | Register - Pickleball Singles Social | (generic fallback, dynamic page; includes `<meta name="robots" content="noindex">`) |

Each page's `<Helmet>` block includes:
- `<title>`
- `<meta name="description">`
- `<meta property="og:title">`, `<meta property="og:description">`, `<meta property="og:url">`
- `<meta property="og:image">` (uses logo: `https://pickleballsinglessocial.com/pickleballsinglessociallogo.png`)
- `<meta name="twitter:card" content="summary_large_image">`, `<meta name="twitter:title">`, `<meta name="twitter:description">`, `<meta name="twitter:image">`
- `<link rel="canonical">`

Existing OG tags in `index.html` serve as the global fallback. Helmet overrides them per-page.

### Noindex for transactional pages

The following pages get `<meta name="robots" content="noindex">` via Helmet since they have no SEO value:
- `/events/:id/register`
- `/events/:id/pay`
- `/register/success`
- `/match/:token`

---

## 2. Pre-Rendering (vite-prerender-plugin)

**Plugin:** `vite-prerender-plugin` (from the Preact team, actively maintained). Peer dependencies list `"vite": "5.x || 6.x || 7.x || 8.x"` and the source contains Vite 8-specific code comments. This is NOT the same as the abandoned `vite-plugin-prerender`.

**Vite 8 compatibility note:** While peer dependencies and source code indicate Vite 8 support, this should be verified with a PoC build early in implementation. If the plugin fails with Vite 8, fallback plan: write a simple custom post-build script (~50 lines) that uses `renderToString` directly for the 5 static routes.

**How it works:** Unlike Puppeteer-based solutions, this plugin calls your app's exported `prerender()` function in Node.js using `react-dom/server`'s `renderToString`. No headless browser needed.

### Architecture changes for pre-rendering

The plugin requires a slightly different entry point structure:

1. **`main.jsx` (client entry):** Uses `hydrateRoot` instead of `createRoot` when pre-rendered HTML is present, falls back to `createRoot` for non-prerendered routes. Wraps router in `<BrowserRouter>` (imported from `react-router`). Wraps in `<HelmetProvider>`, `<ThemeProvider>`, and `<CssBaseline>` (preserving existing MUI setup).

2. **`main-prerender.jsx` (prerender entry, new file):** Exports a `prerender({ url })` function that:
   - Wraps `<App />` in `<StaticRouter location={url}>` (imported from `react-router`), `<HelmetProvider>`, `<ThemeProvider>`, and `<CssBaseline>`
   - Calls `renderToString` to produce body HTML
   - Returns `{ html, head, links }`:
     - `html`: the rendered body content
     - `head`: hardcoded meta tags from a route-to-meta lookup table (see below)
     - `links`: list of internal links found in the rendered output for the plugin to crawl

3. **`index.html`:** Add `prerender` attribute to the script tag so the plugin knows which module to use for pre-rendering.

4. **`App.jsx`:** No changes. The router wrapper (`BrowserRouter` vs `StaticRouter`) is handled in the entry files, not in App.

### Head meta strategy for pre-rendering

**Problem:** react-helmet-async v3 on React 19 does NOT populate the `helmetContext` object. React 19 natively hoists `<title>`, `<meta>`, and `<link>` tags, but the Helmet context used for SSR head extraction is empty.

**Solution:** The `prerender()` function uses a hardcoded route-to-meta lookup table for the 5 static routes. This is reliable and simple since all pre-rendered page meta is known at build time (it comes from the table in Section 1). The client-side `<Helmet>` blocks still work normally for client-side navigation and for non-prerendered pages.

```javascript
const META = {
  '/': {
    title: 'Pickleball Singles Social - Meet Singles Through Pickleball in St. Louis',
    description: 'Social pickleball events for singles in St. Louis...',
  },
  '/about': { ... },
  // etc.
};

export async function prerender({ url }) {
  const meta = META[url] || META['/'];
  const html = renderToString(/* app wrapped in StaticRouter */);
  return {
    html,
    head: {
      title: meta.title,
      elements: new Set([
        { type: 'meta', props: { name: 'description', content: meta.description } },
        { type: 'meta', props: { property: 'og:title', content: meta.title } },
        // ... other meta tags
      ]),
    },
    links: extractLinks(html),
  };
}
```

### Routes to pre-render

- `/`
- `/about`
- `/faq`
- `/code-of-conduct`
- `/events`

### Not pre-rendered (dynamic/authenticated)

- `/events/:id/register`
- `/events/:id/pay`
- `/register/success`
- `/match/:token`
- `/admin/*`

### Build integration

Add the plugin to `vite.config.js` with the `prerenderScript` option pointing to `main-prerender.jsx`. The existing Render build command (`npm run build`) already runs Vite, so no deployment changes needed. The plugin writes HTML files using directory structure (e.g., `dist/about/index.html`).

### Render static site compatibility

Render does NOT apply rewrite rules when a file already exists at the requested path. Since the plugin outputs `dist/about/index.html`, a request to `/about` will be served the prerendered file directly. The catch-all rewrite (`/* -> /index.html`) only applies to non-prerendered routes. This is the correct behavior.

**Verification step:** After the first build, confirm the `dist/` directory contains the expected structure (e.g., `dist/about/index.html`, `dist/faq/index.html`).

### API data at build time

The `/events` page fetches event data from the API. At build time the API may not be reachable, so the pre-rendered HTML shows the page shell without event data. This is acceptable: the page structure and meta tags carry the SEO weight for crawlers. The `fetchEvents` call in `useEffect` should handle fetch failures gracefully (it already does via `.catch(() => {})`).

---

## 3. JSON-LD Structured Data

A reusable `<EventJsonLd>` component that injects `<script type="application/ld+json">` via Helmet. Uses Schema.org Event type. Rendered on the `/events` page, one block per event.

### Schema field mapping

| Schema.org field | Source |
|---|---|
| `@type` | `"Event"` |
| `name` | Event title (e.g., "Pickleball Singles Social (25-45) - 4/12/2026") |
| `startDate` | `event_date` in ISO 8601 |
| `endDate` | `event_date` + 2.5 hours |
| `location.name` | "Arch Pickleball" |
| `location.address` | Bridgeton, MO address |
| `eventStatus` | `EventScheduled` |
| `eventAttendanceMode` | `OfflineEventAttendanceMode` |
| `offers.price` | "15" |
| `offers.priceCurrency` | "USD" |
| `offers.availability` | `InStock` or `SoldOut` based on capacity |
| `offers.url` | Registration link |
| `organizer.name` | "Pickleball Singles Social" |
| `organizer.url` | `https://pickleballsinglessocial.com` |
| `description` | Short event description |
| `image` | Logo URL |

### Limitation

JSON-LD renders client-side only (after hydration). Googlebot executes JavaScript and will see it. However, Bing's crawler has limited JS execution, and social media crawlers (Facebook, Twitter/X) do not execute JS at all, so they will not see structured event data. This is an acceptable tradeoff given that event data is not available at build time. If events become available at build time in the future (e.g., via a build-time API call or JSON fixture), injecting JSON-LD into the pre-rendered output would improve coverage.

---

## 4. robots.txt, sitemap.xml, and index.html

### robots.txt (public/robots.txt)

```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /match/
Disallow: /register/

Sitemap: https://pickleballsinglessocial.com/sitemap.xml
```

### sitemap.xml (public/sitemap.xml)

Static sitemap with five public routes. Note: `priority` and `changefreq` are included for non-Google crawlers but Google ignores both fields.

| URL | Priority | Change frequency |
|---|---|---|
| `/` | 1.0 | weekly |
| `/events` | 0.9 | weekly |
| `/about` | 0.5 | monthly |
| `/faq` | 0.5 | monthly |
| `/code-of-conduct` | 0.3 | yearly |

No dynamic event URLs (individual event pages are registration forms, not content pages).

### index.html additions

- `<meta name="description" content="Social pickleball events for singles in St. Louis. Play mixed doubles, meet new people, and connect through the fastest-growing sport in America.">` as global fallback
- `<meta property="og:image" content="https://pickleballsinglessocial.com/pickleballsinglessociallogo.png" />`
- `<meta name="twitter:card" content="summary_large_image" />`
- `<meta name="twitter:title" content="Pickleball Singles Social" />`
- `<meta name="twitter:description" content="Meet fellow pickleball singles players at our social events. Register, play, and connect with people you enjoy playing with." />`
- `<meta name="twitter:image" content="https://pickleballsinglessocial.com/pickleballsinglessociallogo.png" />`
- `<link rel="canonical" href="https://pickleballsinglessocial.com" />` as fallback
- Note: `<html lang="en">` is already present, no change needed.

---

## Files Modified/Created

| File | Action | What |
|---|---|---|
| `frontend/package.json` | Modify | Add `react-helmet-async@^3.0.0`, `vite-prerender-plugin` |
| `frontend/vite.config.js` | Modify | Configure prerender plugin |
| `frontend/index.html` | Modify | Add fallback meta description, og:image, twitter card tags, canonical; add `prerender` attribute to script tag |
| `frontend/public/robots.txt` | New | Crawler directives + sitemap pointer |
| `frontend/public/sitemap.xml` | New | Static sitemap of public routes |
| `frontend/src/main.jsx` | Modify | Wrap in HelmetProvider, use hydrateRoot when prerendered HTML exists |
| `frontend/src/main-prerender.jsx` | New | Prerender entry: exports prerender() using renderToString + StaticRouter |
| `frontend/src/components/EventJsonLd.jsx` | New | Reusable JSON-LD structured data component |
| `frontend/src/pages/HomePage.jsx` | Modify | Add Helmet with page-specific meta |
| `frontend/src/pages/AboutPage.jsx` | Modify | Add Helmet with page-specific meta |
| `frontend/src/pages/FAQPage.jsx` | Modify | Add Helmet with page-specific meta |
| `frontend/src/pages/CodeOfConductPage.jsx` | Modify | Add Helmet with page-specific meta |
| `frontend/src/pages/EventListPage.jsx` | Modify | Add Helmet with page-specific meta + EventJsonLd per event |
| `frontend/src/pages/RegisterPage.jsx` | Modify | Add Helmet with noindex |
| `frontend/src/pages/PayPage.jsx` | Modify | Add Helmet with noindex |
| `frontend/src/pages/SuccessPage.jsx` | Modify | Add Helmet with noindex |
| `frontend/src/pages/MatchFormPage.jsx` | Modify | Add Helmet with noindex |

No backend changes. No deployment config changes.
