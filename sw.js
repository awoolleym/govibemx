// GoVibeMX offline cache for the rear screen (infotainment.html) and the phone remote (driver.html).
// Goal: when the connection drops (Starlink, tunnels) and the page reloads, it still opens instead of
// showing the browser's "no internet" page. Everything else connects again when the signal is back.
//
// - The two pages: network first (so updates arrive right away), the saved copy when offline.
// - Libraries, fonts, logo, QR codes, game thumbnails: saved copy first, refreshed in the background.
// - Map tiles: the ones already seen are kept (up to MAX_TILES), so the map still shows offline.
// - Anything else (Firebase live data, videos, games, the booking widget) is not touched.

const VERSION = 'govibe-v1';
const PAGES = VERSION + '-pages';
const STATIC = VERSION + '-static';
const TILES = VERSION + '-tiles';
const MAX_TILES = 1500;

const PAGE_FILES = ['infotainment.html', 'driver.html', 'remote.webmanifest', 'remote-icon-192.png', 'remote-icon-512.png'];
const STATIC_HOSTS = ['cdnjs.cloudflare.com', 'www.gstatic.com', 'fonts.googleapis.com', 'fonts.gstatic.com',
  'img1.wsimg.com', 'api.qrserver.com', 'img.cdn.famobi.com', 'i.ytimg.com'];
const TILE_HOST = 'server.arcgisonline.com';

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(PAGES).then((c) => Promise.all(PAGE_FILES.map((f) => c.add(f).catch(() => {})))).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => !k.startsWith(VERSION)).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function isPage(url) {
  if (url.origin !== self.location.origin) return false;
  const file = url.pathname.split('/').pop();
  return PAGE_FILES.indexOf(file) >= 0;
}

// Network first, with a time limit so a "half connected" network doesn't leave the screen blank
function networkFirst(req) {
  return caches.open(PAGES).then((cache) => {
    const fromNet = fetch(req).then((res) => {
      if (res && res.ok) cache.put(req, res.clone());
      return res;
    });
    const timeout = new Promise((resolve) => setTimeout(resolve, 6000));
    return Promise.race([fromNet.catch(() => null), timeout]).then((res) =>
      res || cache.match(req, { ignoreSearch: true }).then((hit) => hit || fromNet));
  });
}

// Saved copy first; refresh it in the background
function staleWhileRevalidate(req, cacheName) {
  return caches.open(cacheName).then((cache) => cache.match(req).then((hit) => {
    const fromNet = fetch(req).then((res) => {
      if (res && (res.ok || res.type === 'opaque')) cache.put(req, res.clone());
      return res;
    });
    if (hit) { fromNet.catch(() => {}); return hit; }
    return fromNet;
  }));
}

let tilePuts = 0;
function trimTiles() {
  return caches.open(TILES).then((cache) => cache.keys().then((keys) => {
    const extra = keys.length - MAX_TILES;
    return extra > 0 ? Promise.all(keys.slice(0, extra).map((k) => cache.delete(k))) : null;
  }));
}
function tileCacheFirst(req) {
  return caches.open(TILES).then((cache) => cache.match(req).then((hit) => hit || fetch(req).then((res) => {
    if (res && res.ok) {
      cache.put(req, res.clone());
      if (++tilePuts % 100 === 0) trimTiles();
    }
    return res;
  })));
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  let url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (isPage(url)) { e.respondWith(networkFirst(req)); return; }
  if (url.hostname === TILE_HOST) { e.respondWith(tileCacheFirst(req)); return; }
  if (STATIC_HOSTS.indexOf(url.hostname) >= 0) { e.respondWith(staleWhileRevalidate(req, STATIC)); return; }
  // Everything else goes to the network as usual
});
