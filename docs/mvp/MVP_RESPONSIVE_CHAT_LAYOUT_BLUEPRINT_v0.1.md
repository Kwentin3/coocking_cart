# MVP responsive chat layout blueprint v0.1

- Статус: UI/UX implementation blueprint
- Дата: 2026-05-25
- Контур: Demo MVP

## Problem

Текущий mobile layout превращает экран в длинную страницу: список чатов, чат, ввод и артефакты живут в одном scroll flow. Пользователь вынужден прокручивать чат, чтобы добраться до ввода или результата.

Нужна адаптивная композиция, где:

- ввод всегда доступен в текущем viewport;
- список чатов не смешивается с артефактами;
- артефакты текущего чата не растягивают основной chat flow;
- avatar/system actions живут в верхней панели;
- размеры задаются визуальным контрактом, а не разрозненными magic numbers.

## Decision

Разделить интерфейс на три независимые поверхности:

1. `Sessions drawer` - навигация по чатам.
2. `Chat surface` - сообщения и composer текущего чата.
3. `Artifacts surface` - проект, риски, JSON и admin/debug tabs текущего чата.

На desktop surfaces могут быть видимыми колонками. На mobile sessions и artifacts становятся overlay surfaces, а основной экран остается chat-first.

## Layout Modes

Layout mode определяется шириной visual viewport:

| Mode | Condition | Composition |
| --- | --- | --- |
| `compact` | `Vw < bpCompact` | Chat only; sessions left drawer; artifacts bottom/fullscreen sheet. |
| `medium` | `bpCompact <= Vw < bpWide` | Chat primary; sessions drawer; artifacts side drawer or collapsible panel. |
| `wide` | `Vw >= bpWide` | Sessions rail + chat + artifacts panel. |

Breakpoints являются design tokens:

```css
--bp-compact: 720px;
--bp-wide: 1100px;
```

Числа нельзя дублировать в компонентах. Если breakpoint меняется, он меняется в одном contract/token layer.

## Responsive Layout Math Contract

Definitions:

```text
Vw = visual viewport width
Vh = visual viewport height
TopBarH = clamp(52px, 7svh, 64px)
SafeTop = env(safe-area-inset-top)
SafeBottom = env(safe-area-inset-bottom)
MainH = 100svh - TopBarH
ComposerH = content-sized, max clamp(96px, 22svh, 180px)
ArtifactSummaryH = content-sized, max clamp(40px, 8svh, 72px)
MessagesH = MainH - ComposerH - visible(ArtifactSummaryH)
```

Invariants:

```text
TopBarH + MessagesH + ComposerH + visible(ArtifactSummaryH) <= 100svh
Composer is visible without body scroll.
Messages scroll inside ChatMessages, not through body scroll.
Artifacts do not push composer below viewport.
Drawers and sheets overlay the chat surface in compact mode.
Long artifact content scrolls inside artifact body.
```

Use `svh` / `dvh` where appropriate. Do not rely on `100vh` as the only mobile height source because browser chrome can change the visible viewport.

## Design Tokens

All fixed-format dimensions must come from named tokens:

```css
:root {
  --topbar-h: clamp(52px, 7svh, 64px);
  --rail-w: clamp(220px, 18vw, 280px);
  --artifact-w: clamp(360px, 30vw, 480px);
  --drawer-w: min(88vw, 360px);
  --composer-max-h: min(22svh, 180px);
  --artifact-summary-max-h: min(8svh, 72px);
  --sheet-max-h: 88svh;
  --gap: clamp(8px, 1.2vw, 14px);
  --touch-target: 44px;
}
```

Rules:

- No hardcoded layout heights like `520px`.
- No fixed mobile-only widths outside named tokens.
- No media query with unexplained numeric threshold.
- No UI card nested inside another UI card.
- Long JSON/draft content must scroll inside its own container.

## Surface Contracts

### Top bar

Top bar owns global/system actions:

- left: sessions drawer trigger;
- center: current session title or fallback title;
- right: artifacts trigger with status badge, then avatar/system menu.

Avatar/system menu owns:

- current role;
- login/logout;
- future system actions.

Top bar must stay visible in all layout modes.

### Sessions drawer

Sessions drawer owns only chat navigation:

- list sessions;
- create session;
- rename session;
- delete session.

It must not contain project draft, warnings, JSON or current chat artifacts.

Compact mode:

```text
DrawerW = min(88vw, 360px)
Drawer overlays chat.
Scrim covers rest of viewport.
```

Wide mode:

```text
RailW = clamp(220px, 18vw, 280px)
Rail participates in main grid.
```

### Chat surface

Chat surface owns:

- quick prompts, if visible;
- messages scroll area;
- artifact summary strip, if current result exists;
- composer with textarea, voice button and send button.

Composer is sticky to bottom of chat surface and remains visible without body scroll.

Messages are the only primary scroll area in chat mode.

### Artifacts surface

Artifacts surface owns current-chat output:

- project draft;
- warnings/risks;
- data statuses;
- structured JSON;
- admin trace/users tabs only when role allows.

Compact mode:

- closed state: artifact summary strip above composer;
- open state: bottom sheet or fullscreen sheet;
- sheet max height: `--sheet-max-h`;
- sheet body scrolls independently.

Wide mode:

- right panel uses `--artifact-w`;
- panel may be collapsible;
- collapsing must not lose artifact state.

## Mobile UX Contract

Compact screen structure:

```text
TopBar
ChatMessages scroll container
ArtifactSummary strip, if result exists
Composer
SessionsDrawer overlay, when open
ArtifactsSheet overlay, when open
```

User actions:

- tap sessions icon: opens sessions drawer;
- tap avatar: opens system menu;
- tap artifact icon or summary strip: opens artifacts sheet;
- tap sheet close or scrim: closes overlay;
- send and voice controls remain in composer, not inside overlays.

## State Contract

Required visible states:

- no authenticated user;
- authenticated user with no session;
- session list empty;
- active session with no messages;
- active session with messages and no artifacts;
- active session with draft/warnings/json;
- sessions drawer open/closed;
- artifacts sheet open/closed;
- chat sending/loading;
- voice recording/transcribing;
- API error for chat/session/artifacts.

No state may require the user to infer what is happening from a frozen button or missing content.

## Implementation Slices

1. Introduce layout tokens in CSS.
2. Split DOM classes into top bar, sessions surface, chat surface, artifacts surface.
3. Add JS UI state: `sessionsDrawerOpen`, `artifactsOpen`, `systemMenuOpen`.
4. Make mobile body non-primary scroll; messages and artifact bodies own scrolling.
5. Convert current result panel to responsive artifact panel/sheet.
6. Move system actions behind avatar menu.
7. Verify compact, medium and wide screenshots manually or with Playwright.

## Implementation Notes

- `app/templates/index.html` owns the semantic surface split: `topbar`, `sessionsPanel`, `chatColumn`, `artifactSummary`, `resultPanel`.
- `app/static/styles.css` owns the visual math contract. Sticky comments mark the token layer and the breakpoint layer; do not introduce layout constants outside those sections without updating this document.
- `app/static/app.js` owns only presentation state for surfaces: drawer open/closed, artifacts open/closed and avatar menu open/closed. Sticky comment marks this UI boundary; session data, messages and structured output remain in the existing runtime state.
- `compact` uses chat-first layout with sessions as a left drawer and artifacts as a bottom sheet.
- `medium` uses chat-first layout with sessions as a left drawer and artifacts as a right drawer.
- `wide` keeps sessions, chat and artifacts visible as grid columns; the artifact summary/button is suppressed by CSS because the result panel is already visible.

## Acceptance Criteria

- On mobile, composer is visible immediately after opening an active chat.
- User can open sessions without losing current chat scroll position.
- User can open artifacts without pushing composer below viewport.
- Project, risks and JSON are accessible from the artifacts sheet.
- Closing artifacts returns to the same chat and composer state.
- Desktop still supports simultaneous chat and artifact view.
- Admin-only trace/users remain role-gated.
- No primary workflow depends on body scroll.
- No hardcoded mobile layout height is introduced outside named tokens.

## Non-goals

- New backend behavior.
- New domain workflow.
- Prompt/context changes.
- New artifact types.
- Production design system.
- Native mobile app.

## Related Documents

- [Frontend visual contract](MVP_FRONTEND_VISUAL_CONTRACT_v0.1.md)
- [Frontend states and errors](MVP_FRONTEND_STATES_AND_ERRORS_v0.1.md)
- [Voice input transcription blueprint](MVP_VOICE_INPUT_TRANSCRIPTION_BLUEPRINT_v0.1.md)
- [Acceptance criteria](MVP_ACCEPTANCE_CRITERIA_v0.1.md)
