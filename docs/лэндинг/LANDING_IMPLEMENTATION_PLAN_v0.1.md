# Landing Implementation Plan v0.1

Статус: Phase 0 repo audit и техническое решение для управляемого лендинга «ТехКухня».
Дата: 2026-06-11.

## 1. Executive Summary

Выбран основной путь: отдельный Next.js + React + TypeScript frontend в `frontend/`.

Причина: в репозитории не найден существующий `package.json`, Vite, Next, React, `vite.config.*`, `next.config.*` или `tsconfig.json`. Текущий MVP UI остается Python/static runtime на `app/templates/index.html`, `app/static/app.js`, `app/static/styles.css` и обслуживается через `app/main.py` / `ThreadingHTTPServer`.

Next.js добавляется как отдельный контур лендинга, без миграции текущего Demo MVP chat workspace и без изменения backend/runtime.

## 2. Repo Audit

Факты на момент старта:

| Проверка | Результат |
| --- | --- |
| Root `package.json` | Не найден |
| Next.js | Не найден |
| Vite | Не найден |
| React | Не найден |
| TypeScript config | Не найден |
| Текущий frontend | `app/templates/index.html`, `app/static/app.js`, `app/static/styles.css` |
| Текущий HTTP entrypoint | `app/main.py` |
| Текущий static serving | `/static/*` из `app/static` |
| Node | `v22.19.0` |
| npm | `11.6.2` |

## 3. Technical Decision

Размещать лендинг в:

```text
frontend/
  app/
  landing/
  public/
```

`frontend/` является самостоятельным npm-пакетом. Все runtime imports должны быть объявлены в `frontend/package.json`.

## 4. Target Structure

```text
frontend/
  app/
    page.tsx
    layout.tsx
    globals.css
  landing/
    content/ru/*.json
    schemas/*.ts
    registries/*.ts
    theme/*.ts
    sections/*
    components/*
    manifests/*.json
    lib/*.ts
  public/
    landing/assets/*
```

## 5. Domain Boundaries

| Domain | Owns | Must not own |
| --- | --- | --- |
| Content | Russian copy, stable ids, claim refs, action refs, asset/icon keys | JSX, CSS selectors, physical image paths |
| Schemas | Runtime validation and max length rules | Product decisions |
| Registries | Section order, assets, icons, CTA, analytics | Section-local business copy |
| Theme/layout | Semantic tokens, layout variants, responsive constraints | Business claims |
| Sections | Rendering validated DTOs | Claims policy, physical paths, hardcoded analytics |
| Primitives | UI semantics and state rendering | Product availability decisions |

## 6. Risks

1. Next.js introduces a second runtime beside the existing Python/static MVP. Mitigation: keep it isolated in `frontend/`.
2. Public CTA, pricing, export/download and legal claims need owner approval before production launch. Mitigation: represent them as disabled/hidden/configurable actions.
3. Product UI mockups may imply unavailable functionality. Mitigation: use claim maturity and cautious roadmap wording.
4. Generated or final marketing assets are not approved yet. Mitigation: use registry-backed local scaffold assets and keep public launch blocked by owner gates.

## 7. Validation Plan

Run from `frontend/`:

```text
npm run validate
npm run lint
npm run build
```

Additional static checks:

```text
rg -n "#[0-9a-fA-F]{3,8}|rgb\\(|hsl\\(" frontend/landing/sections frontend/landing/components
rg -n "/images/|\\.png|\\.webp|\\.svg" frontend/landing/sections
rg -n "style=|top:|left:|z-index:|width: [0-9]|height: [0-9]" frontend/landing/sections
```

## 8. Non-Goals

* не менять Python backend;
* не мигрировать текущий MVP UI на Next.js;
* не реализовывать CMS или `landingctl`;
* не реализовывать AI Asset Generation Pipeline;
* не объявлять production launch готовым без owner gates.

## 9. Phase 0 Acceptance

* решение по стеку зафиксировано;
* Vite-конфликт не найден;
* риски описаны;
* код секций не начинался до фиксации этого плана.
