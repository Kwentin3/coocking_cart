# Публичный лендинг «ТехКухня»

Статус: рабочий пакет документов для верстки публичной маркетинговой страницы.

Этот каталог описывает ту часть продукта, где проект рассказывает о себе: позиционирование, структуру лендинга, визуальную систему, контентные контракты, ассеты и правила приемки.

## Документы пакета

1. [Product Vision](../product/PRODUCT_VISION_v0.1.md) — Target Product / Product Vision: целевая продуктовая система «ТехКухня», ее связь с MVP, roadmap и лендингом.
2. [Capability Roadmap](../product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md) — Capability Maturity Matrix / Roadmap для claims and capabilities: current, MVP, alpha, roadmap, target, vision, unsupported, forbidden.
3. [PRD лендинга](LANDING_PRD_v0.1.md) — продуктовая цель, аудитории, структура секций, CTA, SEO, метрики и Definition of Done.
4. [Product Scope Alignment Audit](product-consistency-audit.md) — аудит согласованности MVP, Target Product и текущей маркетинговой модели лендинга.
5. [MVP / Target Product / Landing Traceability Matrix](mvp-landing-traceability-matrix.md) — практическая матрица соответствия аудиторий, функций, outputs, claims и CTA.
6. [Canonical Product Positioning Summary](product-positioning-canonical-summary.md) — каноническая продуктовая сводка для MVP-safe и Target Product copy, SEO и content modules.
7. [Product Consistency Open Questions](product-consistency-open-questions.md) — вопросы владельцу продукта перед фиксацией claims и copy.
8. [Визуальный и технический контракт](LANDING_VISUAL_TECH_CONTRACT_v0.1.md) — архитектура секций, theme contract, content config, компоненты, адаптивность и запреты для реализации.
9. [Visual Asset Layering Contract](LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md) — layered hero scene, transparent cutouts, content images, final CTA brand band, z-slots and safe areas.
10. [Production Asset Brief](LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md) — рабочий brief для первого production-пакета hero/final CTA assets: backdrop, chef cutout, food cutout, CTA brand band, edge decor и content images.
11. [Asset & Icon Registry Contract](LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md) — детальный контракт изображений, декоративных объектов, продуктовых мокапов, аватаров и пиктограмм.
12. [Landing Showcase Mode Strategy](LANDING_SHOWCASE_MODE_STRATEGY_v0.1.md) — стратегический refine режима `showcase`, MVP entry и contract-managed CTA visibility.
13. [Landing Implementation Handoff](LANDING_IMPLEMENTATION_HANDOFF_v0.1.md) — инженерный handoff для будущей верстки: целевая архитектура, границы доменов, layout system, responsive strategy, токены, контракты секций/компонентов, CTA, analytics, validation и acceptance.
14. [Landing Implementation Plan](LANDING_IMPLEMENTATION_PLAN_v0.1.md) — Phase 0 repo audit, выбранный Next.js путь, структура реализации, риски и validation plan.
15. [Landing Implementation Progress](LANDING_IMPLEMENTATION_PROGRESS.md) — журнал фаз реализации, проверок, отклонений и следующего шага.
16. [Landing Owner Gates](LANDING_OWNER_GATES_v0.1.md) — решения владельца продукта, блокирующие showcase publish, beta и public launch.
17. [Landing Control Plane Blueprint](../landing-control-plane-blueprint.md) — архитектура agent-native управления лендингом через content modules, registries, validation, preview, diff и rollback.
18. [AI Asset Generation Pipeline](../ai-asset-generation-pipeline.md) — генерация candidate assets через image providers с ручным approval, provenance, registry publishing и rollback.
19. [Эскизы](эскизы/) — визуальные референсы. Используются для сверки композиции, но не заменяют контракты.

## Порядок чтения

1. Начинать с Product Vision / Target Product: он задает целевую систему, а не только MVP.
2. Затем читать Capability Roadmap: он задает maturity для capabilities and claims.
3. После этого читать PRD лендинга: он задает публичную упаковку целевой продуктовой ценности.
4. Перед правкой claims, аудиторий, функций, document types, CTA или SEO читать Product Scope Alignment Audit, Traceability Matrix и Canonical Product Positioning Summary.
5. Затем читать Landing Showcase Mode Strategy, если задача касается режима лендинга, MVP entry, CTA visibility или action resolver.
6. Затем читать визуально-технический контракт: он задает, как сверстать страницу управляемо, без локального хардкода.
7. Читать Visual Asset Layering Contract, если задача касается hero composition, прозрачного фона, cutout ассетов, CTA-фона, z-slots или safe areas.
8. Читать Production Asset Brief, если задача касается создания, генерации, ревью или замены hero/final CTA production assets.
9. После этого читать Asset & Icon Registry Contract: он является источником правды по визуальным объектам и пиктограммам.
10. Перед началом верстки читать Landing Implementation Handoff: он переводит продуктовые и визуальные контракты в инженерный план реализации.
11. Читать Landing Implementation Plan и Landing Implementation Progress при проверке фактической реализации.
12. Читать Landing Owner Gates перед showcase publish, beta или public launch.
13. Потом читать Landing Control Plane Blueprint, если задача касается агентного управления, CLI/API, validation, preview или rollback.
14. Читать AI Asset Generation Pipeline, если задача касается генерации, замены или публикации новых изображений.
15. Эскизы смотреть при визуальной сверке hero, карточек, плотности, кропов и общей атмосферы.

## Правила консистентности

* PRD главнее для продуктового смысла, состава секций, CTA, SEO и метрик.
* Визуально-технический контракт главнее для архитектуры реализации, темизации, компонентных границ и правил адаптива.
* Visual Asset Layering Contract главнее для прозрачного фона, cutout/content image/backdrop taxonomy, z-slots, overlap policy и safe areas.
* Production Asset Brief главнее для будущего production-пакета hero/final CTA ассетов, но текущий showcase может публиковаться с registry-backed `local-scaffold` placeholder assets.
* Asset & Icon Registry Contract главнее для ключей ассетов, иконок, alt-текстов, loading strategy и условий отображения.
* Если документы расходятся, править нужно не только один файл, а все связанные места: PRD, visual contract, registry contract и этот индекс.
* Лендинг является витриной Target Product и не обязан ограничиваться текущим MVP, но все claims за пределами MVP должны быть закреплены в Product Vision / Capability Roadmap или помечены как требующие решения владельца продукта.
* MVP — проверочный срез, а не финальная граница продукта.
* Future/commercial CTA не удаляются из модели; они управляются через Landing Mode, Action Visibility Policy, claim maturity и owner gates.
* Если лендинг использует более зрелую target-product формулировку, она должна иметь maturity status.
* `unsupported_claim` нельзя публиковать до фиксации основания в Product Vision, Capability Roadmap или owner decision.
* `forbidden_claim` нельзя использовать даже если формулировка маркетингово привлекательна.
* Любой визуальный объект на лендинге должен иметь ключ в `AssetRegistry` или `IconRegistry`.
* Placeholder/scaffold asset допустим в текущем showcase только если он зарегистрирован, промаркирован как `local-scaffold`, не имеет фиктивного approval и заменяется через registry без правки секций.
* Юридические и нормативные обещания на лендинге должны оставаться осторожными: продукт помогает готовить документы с учетом требований, но не обещает абсолютное соответствие без проверки.

## Минимальный gate перед версткой

Перед началом реализации должны быть подтверждены:

* список секций и порядок страницы;
* primary и secondary CTA;
* структура content config;
* `LandingThemeContract`;
* `LandingAssetKey` и `IconKey`;
* стратегия hero assets и LCP;
* поведение desktop/tablet/mobile;
* список аналитических событий.
* claim maturity для hero, benefits, documents, standards, CTA and SEO claims.
