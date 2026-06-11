# Product Capability Roadmap v0.1

Статус: capability maturity matrix.
Дата: 2026-06-11.
Область: «ТехКухня» Target Product, MVP, alpha-next, roadmap, vision and landing claims.
Роль документа: `PRODUCT_CAPABILITY_ROADMAP_v0.1.md` выполняет роль Capability Maturity Matrix / Roadmap.

Связанные документы:

* [Product Vision](PRODUCT_VISION_v0.1.md)
* [PRD MVP v0.2](../prd/PRD_AI_TECH_CARDS_MVP_v0.2.md)
* [Product workflow v0.2](PRODUCT_WORKFLOW_v0.2.md)
* [Landing PRD](../лэндинг/LANDING_PRD_v0.1.md)
* [Traceability Matrix](../лэндинг/mvp-landing-traceability-matrix.md)

## 1. Purpose

Этот документ отделяет текущую реализацию, MVP, alpha-next, roadmap, target product and long-term vision. Он нужен, чтобы лендинг мог говорить о целевом продукте, но не создавал ложное ощущение, что roadmap/vision capabilities уже доступны.

## 2. Claim Maturity Legend

| Claim maturity | Значение | Landing usage |
| --- | --- | --- |
| `implemented_now` | Уже реализовано сейчас | Можно как current feature. |
| `mvp_scope` | Входит в утвержденный MVP scope | Можно как MVP/current capability. |
| `mvp_hypothesis` | Проверяется MVP, но еще требует подтверждения demo/discovery | Можно осторожно, без обещания подтвержденного результата. |
| `alpha_next` | Ближайший следующий слой | Осторожно; лучше не в hero без решения. |
| `roadmap_claim` | Запланированный слой | Можно как roadmap/future. |
| `target_product_claim` | Часть целевого продукта | Можно как перспектива, без current availability. |
| `vision_claim` | Дальняя перспектива | Обычно не в core landing. |
| `decision_needed` | Нужно решение владельца | Не фиксировать публично без approval. |
| `forbidden_claim` | Нельзя обещать | Запрещено. |
| `unsupported_claim` | Нет основания в MVP, Product Vision, Roadmap или owner decision | Не использовать до фиксации основания или удаления. |

## 3. Capability Matrix

| Capability | Current implementation | MVP | Alpha next | Roadmap | Target product | Claim status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Chat-first сценарий | Есть в текущем demo runtime | Да | Улучшение UX and persistence | Да | Да | `implemented_now` | Можно говорить как текущую capability, если не обещать production SLA. |
| Проект ТК | Есть как document draft flow | Да | Улучшить шаблоны | Да | Да | `implemented_now` / `mvp_scope` | Формулировать как проект, не финальная карта. |
| Проект ТТК | Есть как MVP-сценарий для адаптированных блюд | Да | Улучшить выбор ТК/ТТК | Да | Да | `implemented_now` / `mvp_scope` | Особенно важен для авторских/адаптированных блюд. |
| Кулинарная гипотеза | Есть в rules/workflow | Да | Улучшить UX подтверждения | Да | Да | `mvp_hypothesis` | Показывать как проверяемый механизм, не как автоматически подтвержденный вывод. |
| Уточняющий диалог | Есть | Да | Улучшить branching | Да | Да | `implemented_now` | Safe current claim. |
| Брутто/нетто | Есть как расчетная основа/draft data | Да | Улучшить validation | Да | Да | `mvp_scope` | Не обещать точные нормы без источника. |
| Выход блюда | Есть как подтверждаемое поле | Да | Улучшить production test loop | Да | Да | `mvp_scope` | Реальный выход требует проработки. |
| Порции | Есть | Да | Да | Да | Да | `mvp_scope` | Safe claim. |
| Warnings | Есть | Да | Улучшить классификацию | Да | Да | `implemented_now` | Один из ключевых trust claims. |
| Data statuses | Есть | Да | Расширить статусы | Да | Да | `implemented_now` | Safe claim. |
| Structured JSON | Есть как neutral JSON | Да | Stabilize schema | Да | Да | `mvp_scope` | Не формат 1С/iiko/r_keeper/StoreHouse. |
| Пищевая ценность | Частично, при справочных данных | Да, с caveat | Улучшить справочники | Да | Да | `mvp_scope` | Всегда с источником/статусом проверки. |
| Потери/отходы | Как неподтвержденные поля/statuses | Да, как review/proработка | Production test loop | Да | Да | `mvp_scope` | Не обещать автоматическое подтверждение. |
| Сроки хранения | Только warning/status | Да, как требует проверки | Better workflow | Да | Да | `mvp_scope` | Forbidden as auto-confirmed. |
| Температуры | Только warning/status | Да, как требует проверки | Better workflow | Да | Да | `mvp_scope` | Forbidden as auto-confirmed. |
| Себестоимость | Нет full cost engine | Нет | Discovery/decision | Да | Да | `target_product_claim` | Можно как целевой контур, не как current feature. |
| Закупочные цены | Нет | Нет | Нет | Да | Да | `roadmap_claim` | Требуют отдельной модели цен/поставщиков. |
| Складской учет | Нет | Нет | Нет | Возможно | Дальний target/vision | `vision_claim` / `decision_needed` | Не core landing без решения. |
| Поставщики | Нет | Нет | Нет | Возможно | Vision | `vision_claim` / `decision_needed` | Не current claim. |
| Калькуляционные карты | Нет | Нет | После cost model | Да | Да | `roadmap_claim` | Допустимо как roadmap/target, не как current. |
| DOCX/PDF/Excel export | Нет | Нет | Возможный alpha-next для sample/export | Да | Да | `roadmap_claim` | Не показывать как доступный download без реализации. |
| План-меню | Нет | Нет | Нет | Возможно | Vision | `vision_claim` / `decision_needed` | Не core MVP claim. |
| Этикетки | Нет | Нет | Нет | Возможно | Vision | `vision_claim` / `decision_needed` | Требуют отдельного контекста маркировки. |
| Накопительные ведомости | Нет | Нет | Нет | Возможно | Vision | `vision_claim` / `decision_needed` | Не current. |
| Approval workflow | Нет production workflow | Нет | Lightweight review states | Да | Да | `roadmap_claim` | Не путать с human approval requirement. |
| 1С/iiko/r_keeper/StoreHouse integrations | Нет | Нет | Нет | Да, после JSON stabilization | Да | `roadmap_claim` | Только future integrations. |
| База знаний | Нет | Нет | Возможный content layer | Да | Да | `decision_needed` | Нужен owner decision. |
| Тарифы/onboarding | Нет | Нет | Product decision | Да | Да | `decision_needed` | CTA зависит от go-to-market. |
| Агентное управление лендингом | Документация есть, реализации нет | Не product MVP | Alpha/roadmap tooling | Да | Internal tooling | `roadmap_claim` | Не пользовательская product capability. |
| AI Asset Generation Pipeline | Документация есть, реализации нет | Не product MVP | Later tooling | Да | Internal tooling | `roadmap_claim` | Только для landing/content ops. |
| Автоматическое юридическое соответствие | Нет | Нет | Нет | Нет | Нет | `forbidden_claim` | Запрещено. |
| AI сам утверждает документ | Нет | Нет | Нет | Нет | Нет | `forbidden_claim` | Запрещено. |
| «Без ошибок» | Нет | Нет | Нет | Нет | Нет | `forbidden_claim` | Запрещено. |

## 4. Public Claim Guidance

Можно как current/MVP:

* проект ТК/ТТК;
* управляемый диалог;
* расчетная основа по ингредиентам, выходу and порциям;
* warnings and data statuses;
* structured JSON для будущих интеграций.

Можно как target/roadmap с оговоркой:

* себестоимость;
* калькуляционные карты;
* DOCX/PDF export;
* режим технолога;
* integrations.

Обычно не в core landing до решения:

* план-меню;
* этикетки;
* накопительные ведомости;
* склад;
* поставщики;
* тарифы/self-service onboarding.

Запрещено:

* legal guarantee;
* automatic compliance;
* AI autonomous approval;
* ready accounting import without adapter;
* current availability для vision-функций.

## 5. Roadmap Interpretation

Если claim шире MVP, это не ошибка само по себе. Он становится проблемой только если:

1. отсутствует в Product Vision, Roadmap and owner decisions и становится `unsupported_claim`;
2. имеет `decision_needed`, но используется как утвержденный public copy;
3. звучит как current availability, хотя является roadmap/vision;
4. относится к `forbidden_claim`;
5. не имеет maturity status.

## 6. Open Questions

1. Какие roadmap capabilities владелец продукта разрешает показывать на первом лендинге?
2. Себестоимость должна быть `target_product_claim` или `roadmap_claim`?
3. DOCX/PDF export - alpha-next или roadmap?
4. Калькуляционные карты - обязательный target product слой?
5. План-меню/этикетки/накопительные ведомости - roadmap или vision?
6. Нужна ли отдельная public roadmap section на лендинге?
