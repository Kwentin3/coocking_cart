# MVP / Target Product / Landing Traceability Matrix

Статус: refined traceability matrix.
Дата: 2026-06-11.

Связанные документы:

* [Product Vision](../product/PRODUCT_VISION_v0.1.md)
* [Capability Roadmap](../product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md)
* [Product Scope Alignment Audit](product-consistency-audit.md)
* [Canonical Product Positioning Summary](product-positioning-canonical-summary.md)
* [Open Questions](product-consistency-open-questions.md)
* [PRD лендинга](LANDING_PRD_v0.1.md)

## 1. Purpose

Матрица связывает claims and features публичного лендинга со слоями: current implementation, MVP, alpha-next, roadmap, Target Product, vision and forbidden-zone. Отличие от MVP больше не считается ошибкой само по себе. Ошибка возникает, если claim не имеет основания или создает ложное ощущение текущей доступности.

## 2. Legend

Claim maturity:

| Claim maturity | Значение | Landing usage |
| --- | --- | --- |
| `implemented_now` | Уже реализовано сейчас | Да, как current feature. |
| `mvp_scope` | Входит в утвержденный MVP scope | Да, как MVP/current capability. |
| `mvp_hypothesis` | Проверяется MVP, но требует подтверждения demo/discovery | Да, осторожно, как проверяемую гипотезу. |
| `alpha_next` | Ближайший следующий слой | Осторожно; лучше не в hero без решения. |
| `roadmap_claim` | Запланировано | Можно как roadmap/future, не как доступную функцию. |
| `target_product_claim` | Часть целевого продукта | Можно как продуктовую перспективу, без ложного current availability. |
| `vision_claim` | Дальняя перспектива | Только осторожно, обычно не в core landing. |
| `decision_needed` | Нужно решение владельца | Не фиксировать в публичном copy без approval. |
| `forbidden_claim` | Нельзя обещать | Запрещено. |
| `unsupported_claim` | Нет основания в MVP, Product Vision, Roadmap или owner decision | Не использовать до фиксации основания или удаления. |

Compatibility statuses:

| Status | Meaning |
| --- | --- |
| `aligned` | Claim корректен для своего maturity. |
| `needs_labeling` | Claim допустим, но нужно явно обозначить roadmap/target/current. |
| `landing_gap` | Важная подтвержденная тема слабо отражена на лендинге. |
| `unsupported_claim` | Claim нет в MVP, Target Product, Roadmap or decisions. |
| `blocked` | Claim forbidden. |
| `decision_needed` | Нужен product owner decision. |

## 3. Product Positioning Matrix

| Claim / Feature | Current implementation | MVP status | Target product status | Landing status | Claim maturity | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| AI-ассистент для ТК/ТТК | Есть в demo | Подтверждено | Часть продукта | Есть | `implemented_now` / `mvp_scope` | Использовать как интерфейс/helping layer, не как magic/autonomous approval. |
| Сервис технологических карт | Частично через draft | Подтверждено как проект | Core target | Core landing | `target_product_claim` | Можно как broader product positioning, с уточнением maturity в detailed copy. |
| Управляемая система для рецептур, расчетов and документов | Нет как full system | Частично | Core target | Есть в PRD | `target_product_claim` | Допустимо как целевой продукт. Не писать, что все модули уже доступны. |
| Производственный учет | Нет | Нет | Возможный future | Считывается в PRD | `vision_claim` / `decision_needed` | Не делать core current claim без отдельного решения. |
| Себестоимость как часть продукта | Нет full cost | Исключено из MVP | Target/Roadmap | Есть | `target_product_claim` | Допустимо как целевой контур; current claim должен быть осторожным. |
| «AI сам все делает» | Нет | Противоречит MVP | Не target | Нельзя | `forbidden_claim` | Блокировать. |

## 4. Audience Matrix

| Audience | MVP status | Target product status | Landing status | Claim maturity | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Рестораны и кафе | Подтверждено | Primary | Есть | `mvp_scope` | Core audience. |
| Шеф-повара | Подтверждено | Primary | Есть | `mvp_scope` | Core audience. |
| Технологи | Подтверждено базово | Primary with expanded mode | Есть | `target_product_claim` | Можно как target; full technologist mode не current. |
| Управляющие | Подтверждено | Primary | Есть | `mvp_scope` | Core audience. |
| Владельцы бизнеса | Подтверждено | Primary buyer | Слабо | `mvp_scope` | Можно усилить. |
| Dark kitchen / доставка | Подтверждено | Primary | Слабо | `mvp_scope` | Landing gap: добавить или уточнить. |
| Небольшие сети | Подтверждено | Primary/secondary | Слабо | `mvp_scope` / `target_product_claim` | Landing gap, не drift. |
| Производства и цеха общепита | Частично | Target | Есть | `target_product_claim` | Допустимо, если речь о foodservice/factory kitchen, not broad food industry. |
| Крупные пищевые производства | Нет | Не решено | Может считываться | `decision_needed` | Не использовать явно без решения. |
| 1С-интеграторы | Нет | Future ecosystem | Нет | `vision_claim` / `decision_needed` | Не добавлять в core landing. |

## 5. Feature Matrix

| Claim / Feature | MVP status | Target product status | Landing status | Claim maturity | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Chat-first сценарий | Подтверждено and implemented | Да | Неявно | `implemented_now` | Можно показать в product UI. |
| Проект ТК | Подтверждено and implemented | Да | Есть | `implemented_now` / `mvp_scope` | Current claim. |
| Проект ТТК | Подтверждено | Да | Есть | `mvp_scope` | Current/MVP claim. |
| Кулинарная гипотеза | Проверяется MVP | Да | Слабо | `mvp_hypothesis` | Landing gap: добавить как trust mechanism without overclaim. |
| Уточняющий диалог | Подтверждено | Да | Слабо | `implemented_now` | Landing gap. |
| Брутто/нетто | Подтверждено | Да | Есть | `mvp_scope` | Current/MVP claim with caveat. |
| Выход блюда | Подтверждено | Да | Есть | `mvp_scope` | Current/MVP claim. |
| Порции | Подтверждено | Да | Есть | `mvp_scope` | Current/MVP claim. |
| Warnings | Подтверждено | Да | Слабо | `implemented_now` | Усилить на лендинге. |
| Data statuses | Подтверждено | Да | Слабо | `implemented_now` | Усилить на лендинге. |
| Structured JSON | Подтверждено | Да | Слабо | `mvp_scope` | Future integration bridge. |
| Пищевая ценность | Подтверждено с источником | Да | Есть | `mvp_scope` | Всегда с caveat про справочник/проверку. |
| Потери/отходы | Только status/review/proработка | Да | Есть | `mvp_scope` | Не обещать auto-confirmation. |
| Сроки хранения | Только warning/status | Да | Standards context | `mvp_scope` | Только «требует проверки», no guarantee. |
| Температуры | Только warning/status | Да | Standards context | `mvp_scope` | Только «требует проверки». |
| Себестоимость | Не MVP | Target/Roadmap | Есть | `target_product_claim` | Допустимо как целевой контур; маркировать, если детально. |
| Закупочные цены | Не MVP | Roadmap | Неявно | `roadmap_claim` | Не current. |
| Складской учет | Не MVP | Vision/decision | Неявно через себестоимость | `vision_claim` / `decision_needed` | Не использовать как текущий. |
| Поставщики | Не MVP | Vision/decision | Нет | `vision_claim` / `decision_needed` | Не core. |
| Калькуляционные карты | Не MVP | Roadmap/target | Есть | `roadmap_claim` | Можно в product ecosystem, не current output. |
| DOCX/PDF/Excel export | Не MVP | Roadmap | DOCX CTA есть | `roadmap_claim` | Не использовать как доступный download до реализации. |
| План-меню | Не MVP | Vision/decision | Есть | `vision_claim` / `decision_needed` | Обычно убрать из core или пометить future. |
| Этикетки | Не MVP | Vision/decision | Есть | `vision_claim` / `decision_needed` | Не core без решения. |
| Накопительные ведомости | Не MVP | Vision/decision | Есть | `vision_claim` / `decision_needed` | Не core без решения. |
| Approval workflow | Не MVP | Roadmap | «Проверьте и утвердите» | `roadmap_claim` | Формулировать как human review, не system approval. |
| 1С/iiko/r_keeper/StoreHouse integrations | Explicit out of MVP | Roadmap | Not direct | `roadmap_claim` | Только future integrations, no ready import. |
| База знаний | Нет | Decision | Nav item | `decision_needed` | Требует content strategy. |
| Тарифы/onboarding | Нет | Decision | Nav/CTA | `decision_needed` | Требует go-to-market decision. |
| Agent-native landing control | Не product MVP | Internal tooling target | Docs | `roadmap_claim` | Не product user claim. |
| AI Asset Generation Pipeline | Не product MVP | Internal tooling target | Docs | `roadmap_claim` | Не product user claim. |

## 6. Document / Output Matrix

| Output | MVP | Target product | Landing | Claim maturity | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Проект ТК | Да | Да | Да | `mvp_scope` | Current/MVP output. |
| Проект ТТК | Да | Да | Да | `mvp_scope` | Current/MVP output. |
| Structured JSON | Да | Да | Слабо | `mvp_scope` | Упоминать как integration bridge. |
| Предупреждения | Да | Да | Слабо | `implemented_now` | Усилить. |
| Data statuses | Да | Да | Слабо | `implemented_now` | Усилить. |
| Калькуляционная карта | Нет | Да | Да | `roadmap_claim` | Future/roadmap framing. |
| DOCX/PDF/Excel | Нет | Да | DOCX CTA | `roadmap_claim` | Не current download. |
| План-меню | Нет | Не решено / vision | Да | `vision_claim` / `decision_needed` | Не core без approval. |
| Этикетки | Нет | Не решено / vision | Да | `vision_claim` / `decision_needed` | Не core без approval. |
| Approval status | Нет production | Да | Есть «утвердите» | `roadmap_claim` | Human review wording. |

## 7. Claims Matrix

| Claim | Basis | Claim maturity | Landing usage |
| --- | --- | --- | --- |
| «помогает подготовить проект ТК/ТТК» | MVP + Product Vision | `mvp_scope` | Да, current. |
| «управляемая система для рецептур, расчетов and документов» | Product Vision | `target_product_claim` | Да, как target product. |
| «рассчитывает себестоимость» | Product Vision/Roadmap | `target_product_claim` | Только как целевой контур, не current full engine. |
| «калькуляционные карты» | Product Vision/Roadmap | `roadmap_claim` | Future/roadmap, not current. |
| «DOCX/PDF export» | Product Vision/Roadmap | `roadmap_claim` | Future/roadmap, not current download. |
| «План-меню/этикетки» | Not decided | `vision_claim` / `decision_needed` | Не core without approval. |
| «соответствие требованиям» | Research supports cautious wording | `target_product_claim` with legal guard | Только «с учетом требований». |
| «автоматическое соответствие» | Contradicts safety boundary | `forbidden_claim` | Запрещено. |
| «AI утверждает документы» | Contradicts human review | `forbidden_claim` | Запрещено. |
| «готовый импорт в 1С/iiko» | Roadmap not implemented | `roadmap_claim` / forbidden if current | Только future integrations. |

## 8. CTA Matrix

| CTA | Current support | Target/roadmap support | Claim maturity | Recommendation |
| --- | --- | --- | --- | --- |
| «Записаться на демо» | Да | Да | `implemented_now` / `mvp_scope` | Safe primary CTA until onboarding decision. |
| «Посмотреть пример документа» | Да, if sample draft | Да | `mvp_scope` | Safe if example marked as project. |
| «Начать бесплатно» | Not documented | Possible GTM | `decision_needed` | Не фиксировать без onboarding/free-plan decision. |
| «Посмотреть тарифы» | Not documented | Possible GTM | `decision_needed` | Не core until pricing model. |
| «Открыть базу знаний» | Not documented | Possible content layer | `decision_needed` | Roadmap/content decision. |
| «Скачать DOCX» | Not implemented | Roadmap | `roadmap_claim` | Not current CTA unless export implemented. |

## 9. Risk Matrix

| Risk | Severity | Trigger | Mitigation |
| --- | --- | --- | --- |
| Maturity confusion | High | Target/roadmap claim звучит как current feature | Claim maturity in content modules and validation. |
| Legal/normative overclaim | High | «соответствие», «по законодательству», ГОСТ/СанПиН/ХАССП | Use cautious wording; block forbidden claims. |
| Cost/accounting overclaim | High | Full cost, stock, supplier claims | Mark cost as target/roadmap until implementation. |
| Integration expectation | Medium/High | 1С/iiko terms in copy | Future integrations only; no ready import. |
| Vision overload | Medium | Plan-menu/labels/all docs in core landing | Move to roadmap/vision or owner decision. |
| AI trust risk | Medium | AI as autonomous author/approver | Keep human review boundary visible. |
| Generated asset prompt drift | Medium | Visuals show unavailable UI as current | Prompt templates must include maturity and forbidden claims. |

## 10. Summary Of Required Actions

Before landing copy freeze:

1. Assign claim maturity to each strong claim in hero, benefits, documents, standards, CTA and SEO.
2. Use Product Vision for target product framing.
3. Use Capability Roadmap for roadmap/future labels.
4. Keep MVP-specific copy honest: project, warnings, statuses, structured JSON.
5. Block `unsupported_claim` until the claim gets a source in Product Vision, Capability Roadmap or owner decision.
6. Block `forbidden_claim` regardless of marketing value.
7. Resolve `decision_needed` claims before publishing.
