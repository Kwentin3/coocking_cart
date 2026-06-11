# Product Scope Alignment Audit: MVP / Target Product / Landing

Статус: refined product-scope alignment audit.
Дата: 2026-06-11.
Область: связь Demo MVP, Target Product / Product Vision and публичного лендинга «ТехКухня».

Связанные документы:

* [Product Vision](../product/PRODUCT_VISION_v0.1.md)
* [Capability Roadmap](../product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md)
* [PRD лендинга](LANDING_PRD_v0.1.md)
* [MVP / Target Product / Landing Traceability Matrix](mvp-landing-traceability-matrix.md)
* [Canonical Product Positioning Summary](product-positioning-canonical-summary.md)
* [Open Questions](product-consistency-open-questions.md)

## 1. Executive Summary

После уточнения владельца продукта аудит переосмыслен: MVP не является потолком продукта. MVP - первый проверочный срез, который валидирует главный сценарий: идея блюда -> управляемый диалог -> проект ТК/ТТК -> warnings/statuses -> structured JSON.

Лендинг может и должен описывать целевую систему «ТехКухня»: технологические карты, ТТК, рецептуры, расчеты, документы, себестоимость как target/roadmap capability, стандартизацию процессов общепита and future document layer. Это не ошибка, если broader claims закреплены в [Product Vision](../product/PRODUCT_VISION_v0.1.md), [Capability Roadmap](../product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md) или отдельном решении владельца продукта.

Настоящий drift возникает только когда claim:

* отсутствует в MVP, Target Product, Roadmap and owner decisions;
* противоречит решениям владельца продукта;
* обещает юридическую гарантию или автоматическое соответствие;
* звучит как current availability, хотя является roadmap/vision;
* не имеет maturity status.

## 2. Important Interpretation

MVP is not the ceiling of the product. MVP is the first validation slice. Landing may describe the target product, provided that broader claims are backed by Target Product PRD / Product Vision, Capability Roadmap, or owner decision.

Новая модель:

```text
Target Product / Product Vision
  -> Capability Roadmap / Maturity Matrix
  -> MVP / Prototype Scope
  -> Current Implementation
  -> Landing / Public Product Story
```

Лендинг не обязан сжиматься до MVP. Но лендинг обязан не путать maturity:

* current feature;
* MVP scope capability;
* MVP hypothesis;
* roadmap/target product perspective;
* vision;
* unsupported claim;
* forbidden claim.

## Storefront Principle / Target Product Showcase

Лендинг трактуется как витрина целевого продукта. Over-MVP claim не является дефектом сам по себе: он может быть нормальным `target_product_claim`, `roadmap_claim` или `vision_claim`, если закреплен в Product Vision, Capability Roadmap или owner decision.

Дефект возникает в трех случаях:

1. claim не закреплен ни в MVP, ни в Product Vision, ни в Capability Roadmap, ни в owner decision - это `unsupported_claim`;
2. roadmap/target/vision claim сформулирован как доступная current feature без подтверждения;
3. claim относится к forbidden-zone: юридическая гарантия, автоматическое соответствие, «без ошибок», AI autonomous approval.

Аудит классифицирует не «можно/нельзя относительно MVP», а слой продукта, к которому относится claim.

## 3. Scope

Проверены документы и контракты. Код, UI, content modules, схемы, registry-файлы and production-copy не изменялись.

В фокусе:

* Target Product / Product Vision;
* Capability Roadmap;
* MVP/PRD/product workflow;
* PRD and contracts публичного лендинга;
* Landing Control Plane;
* AI Asset Generation Pipeline;
* research, glossary, decision log.

## 4. Documents Reviewed

| Категория | Документы |
| --- | --- |
| Target product | `docs/product/PRODUCT_VISION_v0.1.md`, `docs/product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md` |
| MVP / prototype | `docs/prd/PRD_AI_TECH_CARDS_MVP_v0.2.md`, `docs/product/PRODUCT_WORKFLOW_v0.2.md`, `docs/mvp/README.md`, `docs/mvp/MVP_SCOPE_v0.1.md`, `docs/mvp/MVP_DEMO_LIMITATIONS_v0.1.md`, `docs/mvp/MVP_DEMO_SCENARIOS_v0.1.md`, `docs/mvp/MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md`, `docs/mvp/context/*.md` |
| Research / decisions | `docs/research/*`, `docs/glossary/GLOSSARY.md`, `docs/decisions/DECISION_LOG.md` |
| Landing | `docs/лэндинг/LANDING_PRD_v0.1.md`, `docs/лэндинг/LANDING_VISUAL_TECH_CONTRACT_v0.1.md`, `docs/лэндинг/LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md`, `docs/лэндинг/README.md` |
| Control plane | `docs/landing-control-plane-blueprint.md`, `docs/ai-asset-generation-pipeline.md`, asset generation ADR/research/rights docs |

## 5. Methodology

1. Найдены product, MVP, landing, control-plane and research docs через `rg`.
2. Сформирован верхний слой Product Vision.
3. Capabilities классифицированы по maturity: `implemented_now`, `mvp_scope`, `mvp_hypothesis`, `alpha_next`, `roadmap_claim`, `target_product_claim`, `vision_claim`, `decision_needed`, `forbidden_claim`, `unsupported_claim`.
4. Старые выводы вида «лендинг обещает больше, чем MVP» заменены на `scope_layer_mismatch`: claim шире MVP и требует проверки по Product Vision / Roadmap.
5. Legal/compliance claims проверены отдельно: опасные абсолютные формулировки остаются forbidden независимо от маркетинговой привлекательности.

## 6. MVP As Validation Slice

MVP проверяет:

* сможет ли пользователь через чат перейти от идеи блюда к проекту ТК/ТТК;
* достаточно ли полезны warnings and data statuses;
* работает ли разделение гипотезы, подтвержденных данных and проекта документа;
* понятен ли structured JSON как future integration bridge;
* доверяет ли пользователь проекту, если видит границы проверки.

MVP намеренно исключает:

* полноценную себестоимость;
* склад;
* закупочные цены;
* поставщиков;
* прямые интеграции;
* DOCX/PDF/Excel export;
* production approval;
* production audit;
* юридическое утверждение.

Это не отказ от target product. Это контроль сложности первого среза.

## 7. Target Product As Landing Source

Лендинг может опираться на Product Vision и показывать более зрелый образ «ТехКухни»:

* технологические карты and ТТК;
* рецептуры;
* расчетная основа;
* документы общепита;
* себестоимость как target/roadmap capability;
* калькуляционные карты как roadmap capability;
* export DOCX/PDF as roadmap/target capability;
* стандартизация кухни;
* управляемая база документов;
* AI-помощник как интерфейс and helper.

Условие: broader claims не должны звучать как «уже доступно сейчас», если maturity не `implemented_now` or `mvp_scope`.

## 8. What Remains True Drift

Настоящий drift:

1. Claim есть на лендинге, но отсутствует в MVP, Product Vision and Capability Roadmap; такой claim получает `unsupported_claim`.
2. Claim имеет `decision_needed`, но используется как подтвержденный public copy.
3. Claim является `vision_claim`, но подан как current feature.
4. Claim обещает legal/compliance guarantee.
5. Claim говорит «ready integration/import», когда есть только future integration direction.
6. Claim не имеет maturity status.
7. Claim противоречит human review boundary.

## 9. What Is Intentional Roadmap / Vision

Не считать drift:

| Claim | Refined interpretation |
| --- | --- |
| Себестоимость | `target_product_claim`; требует отдельного cost/prices/storage layer before current availability. |
| Калькуляционные карты | `roadmap_claim`; логичны после cost model. |
| DOCX/PDF export | `roadmap_claim`; можно упоминать как future/export layer, не как доступный download. |
| Производства и цеха | `target_product_claim` для фабрик-кухонь/цехов общепита; крупное пищевое производство остается `decision_needed`. |
| Тарифы/onboarding | `decision_needed`; go-to-market слой не описан. |
| База знаний | `decision_needed` или roadmap content layer. |
| План-меню/этикетки/накопительные ведомости | `vision_claim` / `decision_needed` до решения владельца. |

## 10. Claims Requiring Owner Decision

| Claim | Почему нужно решение |
| --- | --- |
| «Начать бесплатно» | Нет зафиксированного self-service onboarding/free plan. |
| «Посмотреть тарифы» | Нет pricing model. |
| «База знаний» | Нет content strategy and KB scope. |
| План-меню | Не зафиксировано как roadmap или vision. |
| Этикетки | Требует отдельной маркировочной/нормативной рамки. |
| Накопительные ведомости | Связано с учетными и производственными процессами. |
| Крупные пищевые производства | Сильно шире текущего общепита/MVP. |
| 1С/iiko/r_keeper/StoreHouse visibility on landing | Интеграции roadmap, но public wording требует аккуратности. |

## 11. Claims That Should Remain Forbidden

Forbidden независимо от Product Vision:

* «юридически утверждает карту»;
* «автоматически соблюдает СанПиН/ХАССП/ГОСТ/ТР ТС»;
* «полное соответствие требованиям без проверки»;
* «без ошибок»;
* «AI сам утверждает документ»;
* «лабораторно подтверждает показатели»;
* «сроки хранения и температуры подтверждаются автоматически»;
* «готовый импорт в 1С/iiko/r_keeper/StoreHouse» без реализованного adapter layer;
* fake testimonials as real.

## 12. Reclassified Key Findings

| Тема | Было в старой логике | Refined maturity | Новый вывод |
| --- | --- | --- | --- |
| Себестоимость | `scope_layer_mismatch` | `target_product_claim` | Не ошибка лендинга, если не обещать current full cost engine. |
| Калькуляционные карты | `scope_layer_mismatch` | `roadmap_claim` | Допустимы как future/roadmap, не current output. |
| DOCX/PDF export | `scope_layer_mismatch` | `roadmap_claim` | Не показывать как доступную кнопку download без реализации. |
| План-меню | `scope_layer_mismatch` | `vision_claim` / `decision_needed` | Нужна owner позиция перед public core copy. |
| Этикетки | `scope_layer_mismatch` | `vision_claim` / `decision_needed` | Не в MVP; можно только как дальнюю перспективу после решения. |
| Соответствие требованиям | risk | `forbidden_claim` for absolute wording | Оставить только «с учетом требований» and human review boundary. |
| AI approval | forbidden | `forbidden_claim` | Запрещено. |
| Производства/цеха | drift/decision | `target_product_claim` for общепит цеха; `decision_needed` for крупное производство | Уточнить сегмент в copy. |

## 13. Audience Alignment

| Аудитория | MVP | Target Product | Landing | Maturity |
| --- | --- | --- | --- | --- |
| Небольшие кафе/рестораны | Да | Да | Да | `mvp_scope` |
| Шеф-повара | Да | Да | Да | `mvp_scope` |
| Технологи | Да, базово | Да, расширенно | Да | `target_product_claim` for full technologist mode |
| Управляющие | Да | Да | Да | `mvp_scope` |
| Владельцы бизнеса | Да | Да | Косвенно | `mvp_scope` |
| Dark kitchen / доставка | Да | Да | Слабо | `landing_gap`, not drift |
| Небольшие сети | Да | Да | Слабо | `landing_gap`, not drift |
| Производства и цеха общепита | Частично | Да | Да | `target_product_claim` |
| Крупные пищевые производства | Нет | Не решено | Может считываться | `decision_needed` |

## 14. Feature Alignment

| Feature | Maturity | Landing guidance |
| --- | --- | --- |
| Проект ТК/ТТК | `implemented_now` / `mvp_scope` | Можно как current capability. |
| Warnings/data statuses | `implemented_now` / `mvp_scope` | Желательно усилить в лендинге. |
| Structured JSON | `mvp_scope` | Можно как future-integration bridge. |
| Себестоимость | `target_product_claim` | Можно как целевой контур; не как текущий full cost engine. |
| Калькуляционные карты | `roadmap_claim` | Только future/roadmap or document ecosystem. |
| DOCX/PDF export | `roadmap_claim` | Не как current download. |
| План-меню/этикетки | `vision_claim` / `decision_needed` | Обычно не core landing. |
| Integrations | `roadmap_claim` | Только future, no ready import. |
| Legal compliance guarantee | `forbidden_claim` | Блокировать. |

## 15. Recommended Documentation Updates

Сделано в refine:

* создан Product Vision;
* создан Capability Roadmap;
* audit переосмыслен как Product Scope Alignment;
* traceability matrix получила Claim maturity;
* positioning summary разделен на MVP-safe and Target Product;
* PRD лендинга связан с Product Vision / Roadmap;
* README лендинга обновлен под новый порядок чтения;
* Control Plane получил Claim Maturity Model;
* AI Asset Pipeline обновлен: visual prompts могут опираться на Target Product positioning, но forbidden claims сохраняются.

## 16. Recommended Landing Copy Handling

Не менять весь PRD/production-copy механически. Для каждого сильного утверждения:

1. определить claim maturity;
2. проверить Product Vision / Roadmap;
3. если maturity current/MVP - можно говорить как о функции;
4. если roadmap/target - использовать framing без current availability;
5. если decision_needed - вынести владельцу;
6. если unsupported - не публиковать до фиксации основания;
7. если forbidden - не использовать.

## 17. Decisions Required From Product Owner

1. Какие target-product capabilities являются обязательной частью витрины лендинга?
2. Себестоимость - target product claim или roadmap claim?
3. DOCX/PDF export - alpha-next или roadmap?
4. Калькуляционные карты - обязательная часть target product?
5. План-меню, этикетки and накопительные ведомости - vision или roadmap?
6. Как говорить о производствах/цехах: только общепит or wider food production?
7. Можно ли показывать roadmap capabilities на первом публичном лендинге?

## 18. Appendix: Source Document Map

| Категория | Источники |
| --- | --- |
| Product vision | `docs/product/PRODUCT_VISION_v0.1.md`, `docs/product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md` |
| Product truth / MVP | `docs/prd/PRD_AI_TECH_CARDS_MVP_v0.2.md`, `docs/product/PRODUCT_WORKFLOW_v0.2.md`, `docs/decisions/DECISION_LOG.md` |
| MVP boundary | `docs/mvp/README.md`, `docs/mvp/MVP_SCOPE_v0.1.md`, `docs/mvp/MVP_DEMO_LIMITATIONS_v0.1.md` |
| Runtime behavior | `docs/mvp/MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md`, `docs/mvp/context/*.md` |
| Normative caution | `docs/research/RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_v0.1.md`, `docs/research/RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_ADDENDUM_v0.2.md` |
| Exports/integrations | `docs/research/RESEARCH_REFERENCE_DATA_AND_EXPORTS_v0.1.md` |
| Landing | `docs/лэндинг/LANDING_PRD_v0.1.md`, `docs/лэндинг/*` |
| Managed landing future | `docs/landing-control-plane-blueprint.md`, `docs/ai-asset-generation-pipeline.md` |
