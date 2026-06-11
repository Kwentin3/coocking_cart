# MVP same-domain base path refactor report

- Date: 2026-06-11
- Scope: prepare and deploy Demo MVP and Landing Showcase on one public domain.
- Target public topology: `/` serves Landing Showcase, `/mvp` serves Demo MVP.
- Deploy topology: `docker-compose.demo.yml` defines a `landing` service for `/` and an `app` service for `/mvp`.

## Why this was needed

The existing production domain was serving the Demo MVP at `/`. The desired product flow is different:

- visitor opens the domain root and sees the Landing Showcase;
- the landing header exposes a small icon-only MVP entry;
- clicking it opens the existing MVP on the same domain under `/mvp`.

This requires the MVP to stop assuming that `/api`, `/static`, and the session cookie live at the domain root.

## Implementation summary

- Added `APP_BASE_PATH` runtime config to the Python MVP.
- Kept default root mode by using an empty `APP_BASE_PATH`.
- Added strict base path normalization: valid examples are empty string and `/mvp`; invalid examples include `mvp`, `//mvp`, paths with `?`, `#`, or backslashes.
- Made `DemoMvpHandler` prefix-aware:
  - external `/mvp` maps to internal `/`;
  - external `/mvp/static/...` maps to internal `/static/...`;
  - external `/mvp/api/...` maps to internal `/api/...`;
  - external root `/api/...` is not served by the MVP when `APP_BASE_PATH=/mvp`.
- Kept `app/routes/contracts.py` on internal `/api/...` contracts and documented that the handler strips `APP_BASE_PATH` first.
- Rendered `app/templates/index.html` with base-path-aware static asset URLs.
- Added `window.__MVP_BASE_PATH__` for browser JavaScript.
- Added `appPath()` in `app/static/app.js` so all fetch calls continue to use internal `/api/...` paths while the mount prefix is added centrally.
- Scoped auth cookies to the mounted path:
  - root mode: `Path=/`;
  - prefixed mode: `Path=/mvp`.
- In prefixed mode login/logout also clear the legacy root-scoped `cc_session` cookie with `Path=/` to avoid conflicts after migration from the old root MVP deployment.
- Made server-proxy Live Voice return browser WebSocket URLs under `/mvp/api/live-voice/ws/...` when prefixed.
- Updated Landing Showcase config so `NEXT_PUBLIC_MVP_ENTRY_URL=/mvp` is valid, while absolute `http(s)` URLs still work for separate contours.
- Added `frontend/Dockerfile` for the Landing Showcase Next.js runtime.
- Updated `docker-compose.demo.yml`:
  - `coocking-cart-landing` serves the root landing router;
  - `coocking-cart-app` serves only `PathPrefix(/mvp)`;
  - no strip-prefix middleware is used for the MVP.
- Updated env examples:
  - backend `.env.example` documents `APP_BASE_PATH`;
  - frontend `.env.example` uses `NEXT_PUBLIC_MVP_ENTRY_URL=/mvp`.
- Updated the production runbook with legacy root-mode and same-domain prefixed-mode smoke checks.

## Runtime contract

For same-domain deployment:

```env
APP_BASE_PATH=/mvp
NEXT_PUBLIC_MVP_ENTRY_URL=/mvp
```

Edge routing should forward `/mvp` and `/mvp/...` to the MVP without stripping `/mvp`, because the application now handles the prefix itself.

The root `/` should be owned by the Landing Showcase service.

## Key verification targets

Local code checks:

```powershell
python -m unittest discover -s tests
python -m compileall app tests scripts
node --check app/static/app.js
cd frontend
$env:NEXT_PUBLIC_MVP_ENTRY_URL='/mvp'; npm run validate
$env:NEXT_PUBLIC_MVP_ENTRY_URL='/mvp'; npm run lint
$env:NEXT_PUBLIC_MVP_ENTRY_URL='/mvp'; npm run build
```

Production smoke after deploy:

- `HEAD https://coocking-cart.speechbattle.com/` returns the landing.
- `HEAD https://coocking-cart.speechbattle.com/mvp` returns the MVP shell.
- `GET https://coocking-cart.speechbattle.com/mvp/api/config` returns `ok=true`.
- `POST /mvp/api/demo-login` followed by `GET /mvp/api/sessions` works with one cookie jar.
- The returned auth cookie contains `Path=/mvp`.
- Login/logout responses in prefixed mode also include a root-cookie cleanup header with `Path=/; Max-Age=0`.
- In prefixed mode, `GET https://coocking-cart.speechbattle.com/api/config` is not served by the MVP app.

## Non-goals

- No DNS, firewall, Traefik, Docker network, or unrelated container change was performed.
- No MVP UI redesign was performed.
- No API route contract was renamed inside the route modules.
