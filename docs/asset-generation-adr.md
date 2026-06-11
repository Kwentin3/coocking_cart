# ADR: AI Asset Generation Pipeline Provider and Governance

Статус: proposed.
Дата: 2026-06-11.

Связанные документы:

* [AI Asset Generation Pipeline](ai-asset-generation-pipeline.md)
* [Provider Research](asset-generation-provider-research.md)
* [Asset Provenance and Rights](asset-provenance-and-rights.md)
* [Landing Control Plane Blueprint](landing-control-plane-blueprint.md)

## Context

Landing Control Plane должен управлять ассетами лендинга через asset registry. Следующий шаг — разрешить агенту создавать candidate assets через image-generation provider, но без прямой публикации на сайт.

Риск: если агент сможет «сгенерировать и сразу вставить» изображение, система потеряет governance: права, безопасность, бренд, качество, стоимость и rollback будут обходиться.

## Decision

Для v1 принять следующую архитектуру:

1. Использовать backend-only integration.
2. Основной provider path для v1: Gemini Developer API paid tier через auth key.
3. Использовать Google Gen AI SDK как compatibility layer для будущей миграции на Vertex AI / Gemini Enterprise Agent Platform.
4. Не использовать free tier для реальных брендовых или коммерческих ассетов.
5. Запретить auto-publish.
6. Ввести GeneratedAssetCandidate как отдельную сущность до публикации.
7. Требовать ручной approve перед регистрацией ассета в Asset Registry.
8. Публиковать ассет только через stable `assetKey`.
9. Хранить provenance metadata: provider, model, prompt hash, candidate id, approval user/time, rights flags, SynthID expected flag.
10. Vertex AI / Agent Platform оставить production upgrade path для IAM, service accounts, regional controls, audit and enterprise quotas.

## Alternatives Considered

### A. Full Vertex AI / Agent Platform from day one

Плюсы:

* IAM/service accounts;
* enterprise governance;
* Google Cloud audit/cost controls;
* better production posture.

Минусы:

* выше стартовая сложность;
* больше инфраструктурных решений до проверки продуктового workflow;
* Vertex image endpoint landscape требует проверки на момент реализации из-за deprecation/migration notes.

Решение: не v1 default, но проектировать provider adapter так, чтобы migration не ломал contracts.

### B. Gemini Developer API free tier

Плюсы:

* низкий порог старта.

Минусы:

* данные free tier могут использоваться для улучшения продуктов;
* не подходит для конфиденциальной брендовой стратегии и production asset workflow;
* слабее billing/governance discipline.

Решение: не использовать для реальных ассетов.

### C. Direct generation into Asset Registry

Плюсы:

* меньше шагов.

Минусы:

* нет approval gate;
* высокий риск публикации плохого/неправомерного изображения;
* сложнее rollback and audit.

Решение: запрещено.

## Consequences

Положительные:

* безопасный MVP без тяжелой CMS;
* понятный audit trail;
* provider can be swapped later;
* generated assets не смешиваются с approved/published assets.

Отрицательные:

* больше сущностей и workflow states;
* нужен storage для candidates;
* нужен approval UI или хотя бы preview command;
* prompt/provenance становятся чувствительными данными.

## Required Follow-Up

* Перед реализацией подтвердить provider and billing project.
* Выбрать object storage.
* Определить retention для rejected candidates.
* Определить, кто имеет право approve/publish.
* Проверить актуальные Gemini/Vertex model IDs и pricing на дату реализации.

