# MVP prompt layer contract v0.1

- Статус: контракт markdown prompt/context layer
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Prompt/context layer - управляемый markdown-файл, который входит в статическую часть context window Demo MVP.

Слой не является случайным "куском промпта". У него должны быть понятные роль, порядок, источник, статус и границы ответственности. Это нужно, чтобы context window можно было воспроизвести, проверить и объяснить.

Текущие слои живут в `docs/mvp/context/`.

## Обязательные свойства слоя

Каждый слой должен иметь:

- имя файла;
- стабильный порядок подключения;
- краткую роль;
- производный источник;
- статус;
- описание, что слой должен делать;
- описание, чего слой не должен делать;
- короткий текст, пригодный для вставки в LLM context.

## Naming convention

Файлы слоев именуются так:

```text
NN_LAYER_NAME.md
```

Где:

- `NN` - двузначный порядок сборки;
- `LAYER_NAME` - короткое имя роли слоя в верхнем регистре;
- расширение `.md` показывает, что слой редактируется как документационный артефакт.

Пример:

```text
00_AGENT_ROLE.md
01_PRODUCT_RULES.md
02_WORKFLOW.md
```

## Порядок подключения

Порядок задается в `docs/mvp/context/context_manifest.yml`.

Порядок важен:

1. Роль ассистента.
2. Продуктовые правила.
3. Workflow.
4. Сжатый доменный контекст.
5. Структура документа.
6. Статусы данных.
7. Правила ответа.
8. Ограничения Demo MVP.

Runtime не должен сам придумывать порядок слоев.

## Источник слоя

Слой должен быть производным от common product baseline или MVP contracts:

- PRD v0.2;
- product workflow v0.2;
- research;
- glossary;
- decision log;
- MVP structured output contract;
- MVP context window contract;
- MVP demo limitations.

Слой не должен вводить новое продуктово-архитектурное решение без обновления соответствующего документа или decision log.

## Что слой должен содержать

- Сжатые правила, нужные LLM на каждом такте.
- Четкую предметную инструкцию.
- Ограничения, которые влияют на ответ.
- Стабильные термины и статусы.
- Только статический контекст.

## Чего слой не должен содержать

- Историю user/assistant сообщений.
- Runtime state.
- Secrets или environment-specific config.
- SQL-схемы.
- Production state machine.
- Детальную production architecture.
- Интеграционные mapping под iiko, r_keeper, StoreHouse или 1С.
- Обещание production-ready результата.

## Review rules

Изменение слоя считается документационным изменением и должно ревьюиться как часть поведения ассистента.

Минимальная проверка:

- слой короткий;
- текст не дублирует полный PRD или research;
- роль слоя понятна;
- источник слоя понятен;
- слой не конфликтует с MVP limitations;
- слой не подменяет production architecture;
- `context_manifest.yml` остается согласованным с фактическими файлами.

## Почему LLM не может расширять слои

В Demo MVP LLM не должна автоматически создавать, переписывать или подключать новые context layers.

Причины:

- это ломает воспроизводимость context window;
- усложняет диагностику ответа;
- размывает ответственность за prompt behavior;
- может незаметно изменить продуктовые правила;
- мешает будущему audit/observability path.

Новые или измененные слои появляются только как осознанное изменение документации.

## Связанные документы

- [Markdown context layers](MVP_MARKDOWN_CONTEXT_LAYERS_v0.1.md)
- [Context window contract](MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md)
- [Context manifest](context/context_manifest.yml)
- [Demo limitations](MVP_DEMO_LIMITATIONS_v0.1.md)
