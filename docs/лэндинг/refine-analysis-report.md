# Refine Analysis Report: Landing / MVP / Target Product

Статус: аналитический аудит результата refine.
Дата: 2026-06-11.
Область: документация публичного лендинга «ТехКухня», MVP, Product Vision, Capability Roadmap, Claim Maturity Governance, Landing Control Plane and AI Asset Generation Pipeline.

## 1. Executive Summary

Вердикт: refine принят с замечаниями.

Главная исходная проблема решена: документация больше не трактует MVP как потолок лендинга. Лендинг явно зафиксирован как витрина Target Product, а MVP - как проверочный срез движения к целевому продукту.

Blockers: нет.

Можно двигаться к верстке лендинга как к configurable/data-driven реализации публичной витрины. Нельзя фиксировать production-copy, CTA and визуальные mockups без учета Claim Maturity и оставшихся owner decisions.

Readiness verdict: `ready_after_minor_doc_cleanup`.

Причина: модель Target Product / Roadmap / MVP / Landing согласована, но перед copy-freeze/design-freeze нужно закрыть несколько решений по CTA, exports, себестоимости, vision document types and legal wording.

## 2. What Was Reviewed

Проверены документы:

* `docs/README.md`
* `docs/product/PRODUCT_VISION_v0.1.md`
* `docs/product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md`
* `docs/product/PRODUCT_WORKFLOW_v0.2.md`
* `docs/mvp/README.md`
* `docs/лэндинг/README.md`
* `docs/лэндинг/LANDING_PRD_v0.1.md`
* `docs/лэндинг/LANDING_VISUAL_TECH_CONTRACT_v0.1.md`
* `docs/лэндинг/LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md`
* `docs/лэндинг/product-consistency-audit.md`
* `docs/лэндинг/mvp-landing-traceability-matrix.md`
* `docs/лэндинг/product-positioning-canonical-summary.md`
* `docs/лэндинг/product-consistency-open-questions.md`
* `docs/landing-control-plane-blueprint.md`
* `docs/ai-asset-generation-pipeline.md`
* `docs/asset-generation-provider-research.md`
* `docs/asset-generation-adr.md`
* `docs/asset-provenance-and-rights.md`

Дополнительно проверены:

* локальные markdown-ссылки в 12 ключевых документах;
* наличие `docs/asset-generation-provider-research.md`, `docs/asset-generation-adr.md`, `docs/asset-provenance-and-rights.md`;
* фактическое имя папки `docs/лэндинг`;
* вхождения старых терминов `major_drift`, `mvp_gap`, `mvp_confirmed`, `claimStatus`, `unconfirmed`, `true_drift`.

## 3. Main Finding

Модель «лендинг = витрина Target Product, MVP = проверочный срез» закреплена достаточно явно и повторяется в верхних источниках.

Ключевые evidence:

* `docs/лэндинг/LANDING_PRD_v0.1.md`, раздел `Роль лендинга относительно MVP и целевого продукта`: лендинг назван рыночной витриной Target Product, MVP - экспериментальным проверочным срезом.
* `docs/product/PRODUCT_VISION_v0.1.md`, разделы `Executive Summary`, `Как Лендинг Связан С Target Product`, `Как MVP Связан С Target Product`: MVP не является потолком продукта, broader claims допустимы при закреплении в Product Vision / Roadmap.
* `docs/лэндинг/product-consistency-audit.md`, раздел `Storefront Principle / Target Product Showcase`: over-MVP claim не является дефектом сам по себе.
* `docs/landing-control-plane-blueprint.md`, раздел `Claim Maturity Model`: future validation сначала проверяет Product Vision / Capability Roadmap, а не блокирует claim только потому, что его нет в MVP.

Старая логика «лендинг шире MVP -> ошибка -> ужимать» в активных документах не найдена. Остаточное слово `scope_layer_mismatch` используется как новая диагностическая категория: claim шире MVP и требует проверки по Product Vision / Roadmap.

## 4. Acceptance Criteria Check

| Criteria | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Product Vision / Target Product создан и понятен | pass | `docs/product/PRODUCT_VISION_v0.1.md`, строка роли документа and разделы 1, 14, 15 | Документ явно выполняет роль Target Product / Product Vision. |
| Capability Roadmap / Maturity Matrix создан и понятен | pass | `docs/product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md`, строка роли документа and раздел 2 | Документ явно выполняет роль Capability Maturity Matrix / Roadmap. |
| PRD лендинга фиксирует лендинг как витрину Target Product | pass | `docs/лэндинг/LANDING_PRD_v0.1.md`, `Роль лендинга относительно MVP и целевого продукта` | Не требуется maturity-разметка в каждой секции PRD. |
| MVP не используется как потолок лендинга | pass | `docs/product/PRODUCT_VISION_v0.1.md`, `docs/лэндинг/product-consistency-audit.md`, `docs/лэндинг/README.md` | Формулировки устойчиво говорят, что MVP - проверочный срез. |
| Over-MVP claims проверяются через Product Vision / Roadmap | pass | `docs/лэндинг/product-consistency-audit.md`, `Storefront Principle / Target Product Showcase`; `docs/landing-control-plane-blueprint.md`, `Claim Maturity Model` | Это главный успешный результат refine. |
| Forbidden claims блокируются независимо от Product Vision | pass | `docs/лэндинг/LANDING_PRD_v0.1.md`, `docs/product/PRODUCT_VISION_v0.1.md`, `docs/лэндинг/mvp-landing-traceability-matrix.md` | Legal/compliance and AI approval boundary зафиксированы. |
| Traceability Matrix связывает claims с несколькими слоями | pass | `docs/лэндинг/mvp-landing-traceability-matrix.md`, разделы 2-8 | Есть current, MVP, Target Product, Roadmap/Vision, landing and recommendations. |
| Open Questions не спрашивает «MVP или future SaaS?» | pass | `docs/лэндинг/product-consistency-open-questions.md`, разделы 1, 11 | Вопрос заменен на maturity/hero/owner decisions. |
| Landing Control Plane validates через Product Vision / Roadmap | pass | `docs/landing-control-plane-blueprint.md`, `Claim Maturity Model` | Старая логика «нет в MVP - блокировать» не найдена. |
| AI Asset Pipeline допускает Target Product visuals | pass | `docs/ai-asset-generation-pipeline.md`, `PromptTemplateRegistry` | Также запрещены unsupported/forbidden visual claims. |
| README ведет к правильным ролям документов | pass | `docs/README.md`, `docs/лэндинг/README.md` | Роли Product Vision and Capability Roadmap явно указаны. |
| Можно безопасно начинать верстку | partial | `docs/лэндинг/LANDING_PRD_v0.1.md`, `docs/лэндинг/mvp-landing-traceability-matrix.md` | Можно начинать scaffold/layout. Production-copy and final CTA требуют owner decisions. |

## 5. Claim Maturity Consistency

Принятый enum:

```text
implemented_now
mvp_scope
mvp_hypothesis
alpha_next
roadmap_claim
target_product_claim
vision_claim
decision_needed
forbidden_claim
unsupported_claim
```

Где он закреплен:

* `docs/product/PRODUCT_VISION_v0.1.md`, раздел `Capability Maturity Levels`
* `docs/product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md`, раздел `Claim Maturity Legend`
* `docs/лэндинг/mvp-landing-traceability-matrix.md`, раздел `Legend`
* `docs/landing-control-plane-blueprint.md`, раздел `Claim Maturity Model`
* `docs/лэндинг/LANDING_PRD_v0.1.md`, правила интерпретации claims
* `docs/лэндинг/product-consistency-open-questions.md`, вопрос о будущем поле `claimMaturity`

Проверка старых терминов:

| Term | Result | Notes |
| --- | --- | --- |
| `mvp_confirmed` | not_found | Заменен на `mvp_scope`. |
| `claimStatus` | not_found | Future field теперь называется `claimMaturity`. |
| `unconfirmed` | not_found | Старый статус не используется. |
| `major_drift` | not_found | Заменен на `scope_layer_mismatch` в audit. |
| `mvp_gap` | not_found | Не найден в активном refine-пакете. |
| `true_drift` | not_found | Заменен на `unsupported_claim` / `scope_layer_mismatch`. |

Не конфликтующие дополнительные статусы:

* `landing_gap`, `needs_labeling`, `blocked` в `docs/лэндинг/mvp-landing-traceability-matrix.md` являются compatibility statuses, а не Claim Maturity enum.
* `scope_layer_mismatch` в `docs/лэндинг/product-consistency-audit.md` является audit diagnostic, а не maturity value.

Вывод: enum унифицирован достаточно хорошо. Дополнительные diagnostic/status terms не конфликтуют, потому что их роль понятна из контекста.

## 6. Remaining Risks

| Risk | Severity | Where | Why it matters | Recommended action |
| --- | --- | --- | --- | --- |
| PRD содержит target-product claims, которые могут быть ошибочно реализованы как current availability | medium | `docs/лэндинг/LANDING_PRD_v0.1.md`, разделы 2, 5, 6.6, 8 | В PRD есть «считает себестоимость», «Скачать DOCX», тарифы/onboarding. Верхнее правило это ограничивает, но верстальщик может читать секции изолированно. | В следующей задаче на верстку явно указать: брать maturity guidance из Traceability Matrix and Capability Roadmap; спорные CTA делать configurable/disabled. |
| Owner decisions по CTA не закрыты | medium | `docs/лэндинг/product-consistency-open-questions.md`, разделы 8, 10, 11; `docs/лэндинг/mvp-landing-traceability-matrix.md`, CTA Matrix | «Начать бесплатно», тарифы, база знаний, DOCX download могут быть недоступны. | До production-copy freeze выбрать primary CTA: demo request, sample project, signup, pricing. |
| Vision document types требуют решения | medium | `docs/product/PRODUCT_VISION_v0.1.md`, разделы 12, 17; `docs/лэндинг/product-consistency-audit.md`, sections 9-10 | План-меню, этикетки, накопительные ведомости присутствуют как vision/decision. | Owner должен решить, остаются ли они в core landing, в roadmap/vision copy или скрываются из первой версии. |
| Legal/normative wording требует ручной проверки | high | `docs/лэндинг/LANDING_PRD_v0.1.md`, sections 6.7, 7; `docs/лэндинг/product-consistency-audit.md`, `Claims That Should Remain Forbidden` | Лендинг содержит standards block and SEO topics. Ошибка здесь может создать юридический риск. | Перед copy-freeze провести отдельный legal copy review. |
| Visual mocks могут создать ложную current availability | medium | `docs/ai-asset-generation-pipeline.md`, `PromptTemplateRegistry`; `docs/лэндинг/mvp-landing-traceability-matrix.md`, Risk Matrix | Hero/product UI may show roadmap features as live product. | В implementation brief запретить визуальные UI-states без Capability Roadmap source and visual marker. |
| Product Vision покрывает roles на уровне vision, но не задает операционную role model | low | `docs/product/PRODUCT_VISION_v0.1.md`, long-term `multi-organization roles and permissions`; `docs/product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md` | Для лендинга это допустимо, но для будущей production/product spec будет мало. | Не блокирует верстку; добавить отдельный role model позже, если появится production scope. |
| Смешанный RU/EN стиль может снижать читаемость для внешней команды | low | Несколько docs используют `and`, `future`, `current availability`, `roadmap` | Это не логический дефект, но может мешать копирайтеру. | Сделать отдельный style cleanup перед передачей внешнему исполнителю, если важно. |

## 7. Broken Links / Missing Docs

Результат link-check:

* Проверены 12 ключевых markdown-файлов.
* Битых локальных markdown-ссылок не найдено.

Проверка asset-generation docs:

| Document | Status |
| --- | --- |
| `docs/asset-generation-provider-research.md` | present |
| `docs/asset-generation-adr.md` | present |
| `docs/asset-provenance-and-rights.md` | present |

Проверка папки лендинга:

* Фактическая папка: `docs/лэндинг`.
* Папка вида `#U043b#U044d#U043d#U0434#U0438#U043d#U0433` в `docs/` не найдена.
* Если такой путь появляется в архиве или внешнем выводе, это artifact escaping, а не реальное имя папки репозитория.

## 8. Owner Decisions Still Needed

1. Какой CTA является primary для первой публичной версии: `Записаться на демо`, `Посмотреть пример проекта`, `Начать бесплатно` или другой.
2. Есть ли реальный self-service onboarding/free plan для claims «Начать бесплатно».
3. Можно ли показывать DOCX/PDF/Excel export как roadmap-only, alpha-next или hidden до реализации.
4. Себестоимость остается core target-product claim, SEO-only topic или roadmap-only capability.
5. Какие document types входят в первую витрину: ТК/ТТК only, калькуляционные карты, план-меню, этикетки, накопительные ведомости.
6. Как формулировать standards/legal block: допустимые слова про СанПиН/ХАССП/ГОСТ/ТР ТС and mandatory disclaimer.
7. Какие target-product capabilities можно показывать в product UI mockups без риска current-availability overclaim.

## 9. Readiness Verdict

Status: `ready_after_minor_doc_cleanup`.

Обоснование:

* Нет blockers по структуре документации.
* Центральная логика Target Product storefront закреплена.
* Claim Maturity enum унифицирован.
* Ссылки and missing-docs issues не найдены.
* Сохраняются owner decisions, которые не блокируют engineering scaffold, но блокируют production-copy freeze and final public launch.

Можно ставить задачу на верстку, если в задаче явно указать:

1. не переписывать PRD в MVP-only;
2. не считать roadmap/target claims current features;
3. content and CTA должны быть data-driven/configurable;
4. спорные CTA/exports/vision outputs не публиковать как available-now без owner approval.

## 10. Recommended Next Task

Рекомендуемая следующая задача:

```text
Подготовить implementation handoff для верстки лендинга:
- взять PRD лендинга как Target Product storefront;
- взять Capability Roadmap and Traceability Matrix как claim maturity guardrails;
- зафиксировать allowed/blocked/current/roadmap CTA для первой версии;
- определить, какие section content fields будут configurable;
- не начинать production-copy freeze до owner decisions по CTA, export, себестоимости and legal wording.
```

Альтернативная маленькая задача перед версткой:

```text
Сделать minor doc cleanup для внешнего исполнителя: убрать смешанный RU/EN стиль в ключевых русских документах и добавить короткую "Implementation Guardrails" note в README лендинга.
```
