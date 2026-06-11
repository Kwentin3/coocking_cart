# Landing Owner Gates v0.1

Статус: обязательные решения владельца продукта перед showcase publish, beta и public launch лендинга «ТехКухня».
Дата: 2026-06-11.

Engineering scaffold может считаться готовым без этих решений. Публикация `showcase` и полноценный `launch` требуют разных gates: showcase может быть витриной Target Product без открытой SaaS-воронки, а launch требует готовых коммерческих CTA, onboarding, pricing, legal и analytics.

<!-- STICKY-ACTION-POLICY:
CTA типа signup/pricing/export/MVP-entry не вырезаются из документации и registry.
Они должны быть hidden/disabled/enabled через Landing Mode, Action Visibility Policy и owner gates.
-->

## 1. Landing Mode Gate

1. Выбрать режим следующей публикации: `showcase`, `beta`, `launch`, `internal` или `maintenance`.
2. Подтвердить, что текущая модель лендинга - Target Product showcase, а не MVP-only страница.
3. Решить, может ли `showcase` быть опубликован публично как витрина без полноценного SaaS launch.
4. Зафиксировать, какие CTA допустимы в выбранном режиме.
5. Подтвердить, что future/commercial actions остаются в registry и управляются состоянием, а не удалением.

Текущее инженерное состояние:

* owner decision получен: следующий публичный режим лендинга - `showcase`;
* `landingModeConfig.mode` по умолчанию равен `showcase`;
* `landingModeConfig.ownerGates.landingMode` закрыт;
* Action Visibility Resolver применяет mode + owner/function gates перед render;
* engineering scaffold ready;
* showcase publish допустим как controlled Target Product storefront, не как полноценный SaaS launch;
* public `launch` blocked by owner gates;
* `LANDING_SHOWCASE_MODE_STRATEGY_v0.1.md` фиксирует mode policy.

## 2. MVP Entry Gate

1. Подтвердить URL/route текущего MVP или тестового контура.
2. Подтвердить label: например `Войти`, `MVP`, `Вход` или другой owner-approved вариант.
3. Подтвердить icon и визуальную плотность действия.
4. Решить, виден ли вход внешнему пользователю в `showcase`.
5. Решить, нужна ли авторизация до входа в MVP.
6. Подтвердить, что MVP entry не является primary marketing CTA.

Текущее инженерное состояние:

* `header.json` содержит `loginActionId: "nav.login"`;
* `HeaderSection` умеет отрендерить login action через общий `Button`;
* `nav.login` существует в Action Registry;
* owner decision получен: `nav.login` является icon-only service action, а не primary CTA;
* `nav.login` имеет maturity `mvp_scope`, но URL не хранится в registry;
* URL берётся из `NEXT_PUBLIC_MVP_ENTRY_URL` через config/resolver;
* если `NEXT_PUBLIC_MVP_ENTRY_URL` задан, resolved state для `nav.login` становится visible/enabled;
* если URL не задан или некорректен, resolved state остаётся hidden/owner_gated;
* видимый label отсутствует; accessibility label: `Вход в MVP`;
* auth обрабатывает текущий MVP.

## 3. CTA Visibility Gate

1. Подтвердить primary CTA для `showcase`.
2. Подтвердить primary CTA для `beta`.
3. Подтвердить primary CTA для `launch`.
4. Решить, существует ли реальный free onboarding для формулировки «Начать бесплатно».
5. Решить, показывать ли тарифы до фиксации pricing model.
6. Подтвердить, какой сценарий стоит за `demo.request`: форма, ссылка, календарь, письмо или внутренний lead flow.
7. Подтвердить fallback для disabled actions.

Текущее инженерное состояние:

* `demo.request` enabled как безопасный scroll action.
* `sample.project.view` enabled как безопасный scroll action к documents preview.
* `signup.freeStart` disabled, maturity `decision_needed`, fallback на `demo.request`.
* `pricing.view` hidden, maturity `decision_needed`.
* sections получают actions из registry/model и не должны удалять CTA локально.
* sections получают resolved actions; CTA visibility решается resolver-слоем.

## 4. Exports And Documents

1. Решить, показывать ли DOCX/PDF/Excel export в первой публичной версии.
2. Если показывать, выбрать режим: hidden, disabled roadmap, beta-only, alpha-next или implemented-now.
3. Подтвердить document types первой витрины.
4. Подтвердить формулировку для «пакета документов».

Текущее инженерное состояние:

* `docx.download` disabled, maturity `roadmap_claim`;
* Documents Demo показывает preview как target-product workflow, не как active export;
* export action не удаляется, а остается gated.

## 5. Cost And Calculations

1. Решить, как публично формулировать себестоимость.
2. Выбрать maturity: core target claim, SEO-only, roadmap-only или hidden.
3. Подтвердить, какие расчётные показатели можно показывать в UI mockups.

Текущее инженерное состояние:

* cost wording используется осторожно;
* claim `claim.roadmap.costControl` имеет maturity `roadmap_claim`.

## 6. Standards And Legal Copy

1. Подтвердить legal wording standards block.
2. Уточнить, какие нормативные обещания допустимы.
3. Подтвердить дисклеймер: продукт помогает готовить материалы, но не заменяет юридическую или санитарную экспертизу.

Текущее инженерное состояние:

* standards copy cautious;
* claim `claim.cautious.standards` не обещает абсолютное соответствие.

## 7. Product UI Mockups

1. Подтвердить, какие roadmap features можно показывать в product UI preview.
2. Решить, нужен ли watermark/status для target-product preview.
3. Подтвердить production-ready assets вместо local scaffold SVG.
4. Решить дату и критерии production asset freeze.

Текущее инженерное состояние:

* hero visual использует registry-backed local scaffold assets;
* status `Target Product preview` показывается в hero visual;
* generated/final assets не публиковались.
* owner decision получен: текущая showcase-публикация может использовать placeholder/scaffold assets;
* placeholder assets имеют `rightsStatus: "local-scaffold"` и не считаются production-ready;
* production asset freeze переносится на следующий этап: candidates, review, provenance/rights approval, registry replacement.

## 8. Testimonials

1. Решить: скрыть testimonials, использовать internal placeholder или публиковать реальные approved quotes.
2. Для реальных отзывов подтвердить автора, роль, право публикации и текст.

Текущее инженерное состояние:

* testimonials section disabled в `sectionRegistry`;
* `testimonials.json` имеет `mode: hidden`;
* fake testimonials не рендерятся.

## 9. Public Launch Gate

Полноценный `launch` требует:

1. закрытый Landing Mode Gate со значением `launch`;
2. включённый и проверенный primary conversion flow;
3. owner-approved signup/onboarding или явное отсутствие signup;
4. owner-approved pricing или явное скрытие pricing;
5. legal/copy approval;
6. production assets/provenance approval;
7. analytics dispatch, если метрики нужны для запуска;
8. accessibility smoke/automated audit;
9. deployment/runbook decision для `frontend/`.

Showcase publish exception:

* controlled `showcase` может использовать local scaffold assets, если они зарегистрированы, промаркированы как `local-scaffold` и не выдают себя за production-approved.
* Это исключение не распространяется на полноценный `launch`.

## 10. Launch Rule

До закрытия owner gates статус лендинга:

```text
engineering scaffold ready
showcase publish allowed as controlled storefront when deploy env includes MVP entry URL
placeholder assets accepted for current showcase stage
public launch blocked by owner gates
```
