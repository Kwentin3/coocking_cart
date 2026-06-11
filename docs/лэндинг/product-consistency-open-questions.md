# Product Consistency Open Questions

Статус: вопросы владельцу продукта после Product Scope Alignment audit.
Дата: 2026-06-11.

Связанные документы:

* [Product Vision](../product/PRODUCT_VISION_v0.1.md)
* [Product Capability Roadmap](../product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md)
* [Product Scope Alignment Audit](product-consistency-audit.md)
* [MVP / Target Product / Landing Traceability Matrix](mvp-landing-traceability-matrix.md)
* [Canonical Product Positioning Summary](product-positioning-canonical-summary.md)
* [PRD лендинга](LANDING_PRD_v0.1.md)

## 1. Critical Decisions Before Landing Copy Freeze

1. Какой слой зрелости должен доминировать в hero: MVP-safe, Target Product или roadmap?
2. Что важнее в первом экране: проекты ТК/ТТК, AI-помощник, документы, себестоимость или стандартизация кухни?
3. Можно ли использовать бренд «ТехКухня» как окончательное название или это рабочее имя для лендинга?
4. Нужно ли явно писать на лендинге, что результат - проект документа, требующий проверки?
5. Какую степень осторожности использовать в claims про СанПиН/ХАССП/ГОСТ/ТР ТС?

## 2. MVP Scope Questions

1. Является ли AI-помощник частью MVP как основной интерфейс или только marketing framing?
2. Какие документы реально поддерживаются в MVP: только ТК/ТТК или также ТИ?
3. Есть ли в MVP экспорт DOCX/PDF/Excel?
4. Есть ли в MVP только structured JSON или также пользовательский download?
5. Есть ли базовый расчет пищевой ценности в MVP при справочных данных?
6. Есть ли расчет себестоимости в MVP или только учет доступности/дороговизны ингредиентов без цен?
7. Есть ли в MVP сохранение версий документа на уровне продукта или только runtime/demo storage?
8. Есть ли в MVP роли, кроме `user` и `admin`?
9. Есть ли в MVP полноценный approval workflow?
10. Есть ли в MVP production audit/event log?

## 3. Feature And Output Questions

1. Можно ли показывать на лендинге калькуляционные карты как текущий output?
2. Можно ли показывать план-меню как текущий output?
3. Можно ли показывать этикетки как текущий output?
4. Можно ли показывать накопительные ведомости как текущий output?
5. Можно ли показывать «лист контроля» как текущий output?
6. Должна ли карточка документа в лендинге показывать «Скачать DOCX» или «Посмотреть пример проекта»?
7. Нужны ли реальные sample documents до запуска верстки?
8. Должны ли sample documents содержать warnings/data statuses?
9. Нужно ли показывать structured JSON на публичном лендинге или оставить это техническим trust-detail?

## 4. Audience Questions

1. Какие аудитории являются primary для первого лендинга?
2. Нужно ли выделить dark kitchen / доставку отдельной карточкой?
3. Нужно ли выделить небольшие сети отдельной карточкой?
4. Производства и цеха - primary segment, secondary segment или future expansion?
5. Пищевые производства входят в текущий product story или это слишком широкая категория?
6. Владельцы бизнеса должны быть отдельной аудиторией или частью «рестораны и кафе»?
7. Технологи являются покупателями, пользователями или экспертами-проверяющими?
8. Нужны ли 1С-франчайзи, интеграторы или консультанты как отдельная аудитория?

## 5. Cost / Accounting Questions

1. Нужно ли слово «себестоимость» оставить в SEO, но убрать из hero/core claims?
2. Если «себестоимость» остается, какая безопасная формулировка допустима до появления price/stock engine?
3. Есть ли в ближайшем roadmap закупочные цены?
4. Есть ли в ближайшем roadmap складской учет?
5. Есть ли в ближайшем roadmap поставщики и номенклатура?
6. Нужно ли отделять «расчет ингредиентов/выхода» от «расчета себестоимости» в лендинге?
7. Нужно ли прямо писать «полноценная себестоимость - следующий этап»?

## 6. Compliance / Legal Questions

1. Какие нормативные формулировки разрешены публично?
2. Можно ли писать «по требованиям законодательства» или только «с учетом требований»?
3. Нужно ли добавить legal disclaimer в standards block?
4. Нужна ли ручная юридическая проверка landing copy перед публикацией?
5. Можно ли упоминать ХАССП как feature, если продукт не строит HACCP system?
6. Можно ли упоминать СанПиН/ТР ТС/ГОСТ в SEO без обещания проверки?
7. Кто отвечает за финальную проверку нормативных claims?

## 7. Integrations Questions

1. Есть ли интеграция с 1С в текущем roadmap?
2. Есть ли интеграции с iiko, r_keeper или StoreHouse?
3. Нужно ли упоминать учетные системы вообще?
4. Если да, использовать формулировку «structured JSON для будущих интеграций»?
5. Нужна ли отдельная страница/раздел «Интеграции» или это преждевременно?

## 8. CTA / Funnel Questions

1. Есть ли реальный бесплатный onboarding flow для «Начать бесплатно»?
2. Есть ли тарифы, которые можно показывать?
3. Есть ли база знаний?
4. Что должно быть primary CTA до production launch: «Записаться на демо», «Посмотреть пример документа» или «Начать бесплатно»?
5. Нужно ли собирать leads через форму вместо self-service регистрации?
6. Есть ли готовый demo script for sales call?

## 9. Landing Control Plane / Content Governance Questions

1. Нужно ли встроить product consistency audit как validation input для будущего `landingctl validate`?
2. Должны ли risk gates помечать claims про себестоимость, legal compliance, integrations и exports как medium/high risk?
3. Нужно ли content modules хранить `claimMaturity`: `implemented_now`, `mvp_scope`, `mvp_hypothesis`, `alpha_next`, `roadmap_claim`, `target_product_claim`, `vision_claim`, `decision_needed`, `forbidden_claim`, `unsupported_claim`?
4. Должны ли prompt templates для AI-generated assets ссылаться на canonical positioning summary?
5. Кто будет approve изменения high-risk claims в лендинге?

## 10. Recommended Owner Decisions

Минимальный набор решений перед правкой лендинга:

1. Принять главный one-liner из [Canonical Product Positioning Summary](product-positioning-canonical-summary.md) или заменить его.
2. Решить: «себестоимость» остается core claim, SEO-only claim или roadmap claim.
3. Решить: DOCX/PDF export есть в ближайшей версии или убирается из landing PRD.
4. Решить: какие document types считаются MVP outputs.
5. Решить: производственные сегменты остаются primary или сужаются.
6. Утвердить safe legal wording для standards block.
7. Утвердить primary CTA для первой версии лендинга.

## 11. Target Product / Roadmap Decisions

1. Какие target-product capabilities считаются обязательной частью витрины?
2. Какие roadmap capabilities можно показывать на лендинге без явной пометки «скоро»?
3. Какие функции входят в ближайший alpha-next слой?
4. Какие claims требуют owner approval?
5. Какие claims требуют юридической проверки?
6. Какие claims запрещены независимо от Product Vision?
7. Какие возможности нельзя показывать как доступные сейчас?
8. Нужно ли на лендинге разделять «доступно сейчас» и «целевая возможность», или лендинг остается общей витриной?
9. Можно ли подавать себестоимость как целевой контур продукта?
10. Можно ли подавать DOCX/PDF export как roadmap?
11. Какие document types относятся к target product?
12. Какие document types являются long-term vision?
13. Какие target product capabilities можно показывать визуально в product UI mockups?
14. Кто утверждает перевод claim из `decision_needed` в `roadmap_claim` или `target_product_claim`?
