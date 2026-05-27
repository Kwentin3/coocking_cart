# Документация проекта

## Что это за проект

Проект `coocking_cart` описывает продукт AI-ассистента для подготовки проектов технологических и технико-технологических карт для предприятий общественного питания.

На текущем этапе проект находится в фазе product discovery и подготовки Demo MVP-документации. Код приложения, backend, frontend, инфраструктура и зависимости пока не создаются.

Для реализации Demo MVP использовать финальную документационную ветку `docs/mvp-final-docs-before-implementation` или cleanup-ветку после merge. Default branch может быть устаревшим источником для реализации.

## Навигация

- [PRD MVP v0.2](prd/PRD_AI_TECH_CARDS_MVP_v0.2.md) - актуальный продуктовый refine.
- [PRD MVP v0.1](prd/PRD_AI_TECH_CARDS_MVP_v0.1.md) - сохраненный первый черновик.
- [Research: нормативная база РФ](research/RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_v0.1.md) - краткие выводы по ТК, ТТК, ТИ и связанным требованиям.
- [Research addendum v0.2](research/RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_ADDENDUM_v0.2.md) - уточнения нормативного контекста для PRD v0.2.
- [Research: справочные данные и экспорты](research/RESEARCH_REFERENCE_DATA_AND_EXPORTS_v0.1.md) - заметки по БЖУ, справочникам пищевой ценности и будущим интеграциям.
- [Product workflow v0.2](product/PRODUCT_WORKFLOW_v0.2.md) - актуальный путь пользователя от идеи блюда до проекта документа.
- [Product workflow v0.1](product/PRODUCT_WORKFLOW_v0.1.md) - сохраненная первая версия workflow.
- [Demo MVP documentation pack](mvp/README.md) - минимальный пакет документации для демонстрационного прототипа.
- [MVP implementation handoff](mvp/MVP_IMPLEMENTATION_HANDOFF_v0.1.md) - порядок чтения и инварианты для будущей реализации.
- [MVP implementation roadmap](mvp/MVP_IMPLEMENTATION_ROADMAP_v0.1.md) - фазовый порядок реализации Demo MVP с gate-критериями и stop rules.
- [MVP domain-layered refactoring plan](mvp/MVP_DOMAIN_LAYERED_REFACTORING_PLAN_v0.1.md) - план разнесения текущих backend/frontend монолитов по доменам, слоям и контрактам.
- [MVP demo scenarios](mvp/MVP_DEMO_SCENARIOS_v0.1.md) - первые сценарии проверки демо.
- [MVP acceptance criteria](mvp/MVP_ACCEPTANCE_CRITERIA_v0.1.md) - критерии готовности документации и будущего прототипа.
- [MVP frontend visual contract](mvp/MVP_FRONTEND_VISUAL_CONTRACT_v0.1.md) - UI/composition contract для чата, результата, Context Inspector, desktop/mobile и states.
- [MVP frontend states and errors](mvp/MVP_FRONTEND_STATES_AND_ERRORS_v0.1.md) - loading/error/empty/success states для будущего UI.
- [MVP responsive chat layout blueprint](mvp/MVP_RESPONSIVE_CHAT_LAYOUT_BLUEPRINT_v0.1.md) - адаптивная mobile/desktop композиция чатов, ввода и артефактов без общей простыни.
- [Admin context workspace PRD](prd/PRD_ADMIN_CONTEXT_WORKSPACE_v0.1.md) - продуктовый контракт read-only admin dashboard и prompt/context просмотра.
- [Admin context workspace blueprint](mvp/MVP_ADMIN_CONTEXT_WORKSPACE_BLUEPRINT_v0.1.md) - implementation blueprint для служебной admin-зоны.
- [MVP context contracts](mvp/MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md) - контракт context window и связанные prompt/turn contracts.
- [MVP Context Inspector](mvp/MVP_CONTEXT_INSPECTOR_v0.1.md) - концепт debug-view для сборки контекстного окна.
- [MVP LLM provider adapter](mvp/MVP_LLM_PROVIDER_ADAPTER_NOTE_v0.1.md) - минимальная граница интеграции с LLM provider.
- [MVP roles/env/bootstrap](mvp/MVP_ROLES_AND_ACCESS_v0.1.md) - минимальные роли, environment contract и bootstrap data contract.
- [MVP admin user CRUD blueprint](mvp/MVP_ADMIN_USER_CRUD_BLUEPRINT_v0.1.md) - admin-only CRUD пользователей без production IAM/RBAC.
- [MVP voice input transcription blueprint](mvp/MVP_VOICE_INPUT_TRANSCRIPTION_BLUEPRINT_v0.1.md) - голосовой ввод как STT в редактируемый chat input без voice chat.
- [MVP Gemini Live streaming voice research](mvp/MVP_GEMINI_LIVE_STREAMING_VOICE_RESEARCH_v0.1.md) - low-latency voice input через Gemini Live API, ephemeral tokens и adapter/factory boundary.
- [Safe env example](../.env.example) - безопасный шаблон переменного окружения; реальные `.env` не коммитятся.
- [Demo MVP context layers](mvp/context/) - markdown-слои статического контекста для будущего runtime context pack.
- [Ops docs](ops/README.md) - deployment context, server audit и шаблоны будущего deployment task.
- [Deployment context: coocking-cart.speechbattle.com](ops/DEPLOYMENT_CONTEXT_coocking-cart.speechbattle.com_v0.1.md) - target domain/server для будущего Demo MVP.
- [Deployment preparation handoff](ops/DEPLOYMENT_PREPARATION_HANDOFF_v0.1.md) - порядок подготовки будущего deployment task.
- [Local testing and production runtime runbook](ops/LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md) - локальные проверки Windows/PowerShell, отсутствие локального Docker/Linux и production runtime на сервере.
- [Server audit report: 91.132.48.224](ops/SERVER_AUDIT_REPORT_91.132.48.224_v0.1.md) - результат read-only аудита сервера.
- [Production future track](production/README.md) - placeholder будущей production-архитектуры.
- [Documentation audits](audits/) - аудит документационного пула и рекомендация по разделению MVP/production.
- [Decision log](decisions/DECISION_LOG.md) - зафиксированные стартовые продуктовые решения.
- [Glossary](glossary/GLOSSARY.md) - простые определения терминов.
- [Templates](templates/) - шаблоны для будущих PRD и продуктовых решений.

## Документационные контуры

- Common product baseline: PRD, workflow, research, glossary и decision log.
- Demo MVP: быстрый демонстрационный прототип с file-driven context, markdown context layers, SQLite для короткой истории диалога и минимальным structured output.
- Ops docs: deployment context, read-only server audit и шаблоны будущего deployment task без secrets и private credentials.
- Future production architecture: будущий контур managed state, state machine, semantic context, calculation, validation, audit, versioning и integrations.

Production architecture сейчас является future track и не блокирует Demo MVP.

## Текущий статус

PRD v0.2 и workflow v0.2 являются актуальным common baseline. Документы в `docs/mvp/` описывают Demo MVP как демонстрационный прототип, а не production-ready систему.
