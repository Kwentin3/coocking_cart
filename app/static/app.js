const state = {
  user: null,
  sessions: [],
  users: [],
  adminDashboard: null,
  adminContext: null,
  adminScreen: "dashboard",
  adminSelectedSessionId: null,
  sessionId: null,
  latestTurn: null,
  editingSessionId: null,
  sending: false,
  ui: {
    sessionsDrawerOpen: false,
    artifactsOpen: false,
    systemMenuOpen: false,
  },
  voice: {
    supported: false,
    streamingEnabled: false,
    streamingTransport: "direct_client",
    batchEnabled: true,
    enabled: true,
    // Sticky Voice UI contract: batch fallback uses record/stop controls;
    // live streaming uses an animated mic. Transport names stay out of UI copy.
    mode: "batch",
    connecting: false,
    recording: false,
    transcribing: false,
    startedAt: 0,
    timerId: null,
    audioContext: null,
    source: null,
    processor: null,
    gain: null,
    stream: null,
    chunks: [],
    totalSamples: 0,
    inputSampleRate: 0,
    liveInputSampleRate: 16000,
    websocket: null,
    setupComplete: false,
    setupResolver: null,
    setupRejecter: null,
    liveTranscript: "",
    liveHadError: false,
    maxSeconds: 180,
    countdownSeconds: 15,
  },
};

const el = (id) => document.getElementById(id);

async function api(path, options = {}) {
  try {
    const response = await fetch(path, {
      credentials: "same-origin",
      headers: {"Content-Type": "application/json", ...(options.headers || {})},
      ...options,
    });
    const payload = await response.json().catch(() => ({ok: false, error: "Некорректный ответ сервера."}));
    if (!response.ok && payload.ok !== false) {
      payload.ok = false;
      payload.error = "Ошибка запроса.";
    }
    return payload;
  } catch (_error) {
    return {ok: false, error: "Сервер недоступен. Проверьте подключение и повторите действие."};
  }
}

function showToast(text) {
  const toast = el("toast");
  toast.textContent = text;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 2200);
}

function activeSession() {
  return state.sessions.find((session) => session.id === state.sessionId) || null;
}

function avatarLabel() {
  const source = state.user?.email || state.user?.role || "?";
  return String(source).trim().slice(0, 1).toUpperCase() || "?";
}

function artifactStatus(output) {
  const warningCount = output?.warnings?.length || 0;
  const questionCount = output?.open_questions?.length || 0;
  if (output?.document_draft) {
    return {
      title: "Проект готов",
      detail: warningCount ? `${warningCount} риск(ов) · JSON доступен` : "Рисков нет · JSON доступен",
    };
  }
  if (questionCount) {
    return {
      title: "Нужно уточнить",
      detail: `${questionCount} вопрос(ов) · черновик пока не готов`,
    };
  }
  return {
    title: "Есть результат",
    detail: "Открыть проект, риски и JSON",
  };
}

function renderTopbar() {
  const authenticated = !!state.user;
  const admin = !!state.user?.is_admin;
  const session = activeSession();
  const title = admin ? "Админка" : session?.title || (state.sessionId ? `Чат #${state.sessionId}` : "Новый чат");
  const hasArtifacts = authenticated && !admin && !!state.latestTurn?.structured_output;

  el("currentChatTitle").textContent = title;
  el("currentChatTitle").classList.toggle("hidden", !authenticated);
  el("sessionsDrawerBtn").classList.toggle("hidden", !authenticated);
  el("sessionsDrawerBtn").setAttribute("aria-expanded", String(state.ui.sessionsDrawerOpen));
  el("artifactTopBtn").classList.toggle("hidden", !hasArtifacts);
  el("artifactTopBtn").setAttribute("aria-expanded", String(state.ui.artifactsOpen));
  el("artifactTopBadge").classList.toggle("hidden", !hasArtifacts);
  el("avatarBtn").classList.toggle("hidden", !authenticated);
  el("avatarBtn").textContent = authenticated ? avatarLabel() : "?";
  el("avatarBtn").setAttribute("aria-expanded", String(state.ui.systemMenuOpen));
  el("artifactPanelSubtitle").textContent = title;
}

function renderSurfaceState() {
  el("sessionsPanel").classList.toggle("open", state.ui.sessionsDrawerOpen);
  el("sessionsScrim").classList.toggle("hidden", !state.ui.sessionsDrawerOpen);
  el("resultPanel").classList.toggle("open", state.ui.artifactsOpen);
  el("artifactScrim").classList.toggle("hidden", !state.ui.artifactsOpen);
  el("systemMenu").classList.toggle("hidden", !state.ui.systemMenuOpen);
  renderTopbar();
}

// Sticky UI boundary: drawers and sheets only change presentation; session and artifact data stay in existing state.
function setSessionsDrawer(open) {
  state.ui.sessionsDrawerOpen = !!open;
  if (open) {
    state.ui.artifactsOpen = false;
    state.ui.systemMenuOpen = false;
  }
  renderSurfaceState();
}

function setArtifactsOpen(open) {
  state.ui.artifactsOpen = !!open;
  if (open) {
    state.ui.sessionsDrawerOpen = false;
    state.ui.systemMenuOpen = false;
  }
  renderSurfaceState();
}

function setSystemMenu(open) {
  state.ui.systemMenuOpen = !!open;
  if (open) {
    state.ui.sessionsDrawerOpen = false;
    state.ui.artifactsOpen = false;
  }
  renderSurfaceState();
}

function closeOverlays() {
  state.ui.sessionsDrawerOpen = false;
  state.ui.artifactsOpen = false;
  state.ui.systemMenuOpen = false;
  renderSurfaceState();
}

function renderArtifactSummary(output) {
  const summary = el("artifactSummary");
  const hasOutput = !!output && !state.user?.is_admin;
  if (!hasOutput) {
    summary.innerHTML = "";
    summary.classList.add("hidden");
    state.ui.artifactsOpen = false;
    return;
  }
  const status = artifactStatus(output);
  summary.innerHTML = `
    <span>
      <strong>${escapeHtml(status.title)}</strong>
      <small>${escapeHtml(status.detail)}</small>
    </span>
    <span aria-hidden="true">▤</span>
  `;
  summary.title = `${status.title}. ${status.detail}`;
  summary.classList.remove("hidden");
  el("artifactTopBtn").title = summary.title;
  el("artifactTopBtn").setAttribute("aria-label", `Открыть результат: ${status.title}`);
}

function showLogin(configErrors = []) {
  el("loginView").classList.remove("hidden");
  el("workspace").classList.add("hidden");
  el("roleBadge").textContent = "guest";
  el("logoutBtn").classList.add("hidden");
  el("newSessionBtn").classList.add("hidden");
  closeOverlays();
  const box = el("configErrors");
  if (configErrors.length) {
    box.innerHTML = configErrors.map((item) => `<div>⚠ ${escapeHtml(item)}</div>`).join("");
    box.classList.remove("hidden");
  } else {
    box.classList.add("hidden");
  }
}

function showWorkspace() {
  el("loginView").classList.add("hidden");
  el("workspace").classList.remove("hidden");
  el("roleBadge").textContent = state.user?.role || "user";
  el("logoutBtn").classList.remove("hidden");
  el("newSessionBtn").classList.toggle("hidden", !!state.user?.is_admin);
  el("workspace").classList.toggle("admin-mode", !!state.user?.is_admin);
  el("chatColumn").classList.toggle("hidden", !!state.user?.is_admin);
  el("adminWorkspace").classList.toggle("hidden", !state.user?.is_admin);
  el("resultPanel").classList?.toggle?.("hidden", !!state.user?.is_admin);
  if (state.user?.is_admin) {
    state.ui.artifactsOpen = false;
  }
  el("inspectorTab").classList.toggle("hidden", !state.user?.is_admin);
  el("usersTab").classList.toggle("hidden", !state.user?.is_admin);
  el("railTitle").textContent = state.user?.is_admin ? "Админка" : "Сессии";
  el("newSessionRailBtn").classList.toggle("hidden", !!state.user?.is_admin);
  if (!state.user?.is_admin && (!el("usersPanel").classList.contains("hidden") || !el("inspectorPanel").classList.contains("hidden"))) {
    setActiveTab("draft");
  }
  renderSurfaceState();
}

async function init() {
  const me = await api("/api/me");
  applyVoiceConfig(me.voice_input || null);
  if (me.user) {
    state.user = me.user;
    showWorkspace();
    if (state.user?.is_admin) {
      setAdminScreen(state.adminScreen || "dashboard");
    } else {
      await loadSessions();
    }
  } else {
    showLogin(me.config_errors || []);
  }
}

function applyVoiceConfig(config) {
  if (!config) return;
  state.voice.maxSeconds = Number(config.max_audio_seconds || state.voice.maxSeconds);
  state.voice.countdownSeconds = Number(config.countdown_seconds || state.voice.countdownSeconds);
  state.voice.streamingEnabled = !!config.streaming_enabled;
  state.voice.streamingTransport = config.streaming_transport || state.voice.streamingTransport;
  state.voice.batchEnabled = config.batch_enabled !== false && config.enabled !== false;
  state.voice.liveInputSampleRate = Number(config.streaming_sample_rate || state.voice.liveInputSampleRate);
  state.voice.enabled = state.voice.batchEnabled || state.voice.streamingEnabled;
  if (!state.voice.enabled) {
    updateVoiceStatus("");
    refreshVoiceControls();
  }
}

async function login(event) {
  event.preventDefault();
  const payload = await api("/api/login", {
    method: "POST",
    body: JSON.stringify({email: el("emailInput").value, password: el("passwordInput").value}),
  });
  if (!payload.ok) {
    showToast(payload.error || "Не удалось войти.");
    return;
  }
  state.user = payload.user;
  showWorkspace();
  if (state.user?.is_admin) {
    setAdminScreen("dashboard");
  } else {
    await loadSessions();
  }
}

async function demoLogin() {
  const payload = await api("/api/demo-login", {method: "POST", body: "{}"});
  if (!payload.ok) {
    showToast(payload.error || "Demo user недоступен.");
    return;
  }
  state.user = payload.user;
  showWorkspace();
  await loadSessions();
}

async function logout() {
  await api("/api/logout", {method: "POST", body: "{}"});
  state.user = null;
  state.sessions = [];
  state.users = [];
  state.adminDashboard = null;
  state.adminContext = null;
  state.adminScreen = "dashboard";
  state.adminSelectedSessionId = null;
  state.sessionId = null;
  state.latestTurn = null;
  state.editingSessionId = null;
  showLogin([]);
}

async function loadSessions() {
  const payload = await api("/api/sessions");
  if (!payload.ok) {
    showToast(payload.error || "Не удалось загрузить сессии.");
    return;
  }
  state.sessions = payload.sessions || [];
  renderSessions();
  if (!state.sessionId && state.sessions.length) {
    await openSession(state.sessions[0].id);
  } else {
    renderSurfaceState();
  }
}

async function createSession(title = "Новая сессия") {
  const payload = await api("/api/sessions", {method: "POST", body: JSON.stringify({title})});
  if (!payload.ok) {
    showToast(payload.error || "Не удалось создать сессию.");
    return null;
  }
  state.sessionId = payload.session_id;
  state.editingSessionId = null;
  await loadSessions();
  await openSession(payload.session_id);
  showToast("Чат создан.");
  return payload.session_id;
}

async function openSession(sessionId) {
  const payload = await api(`/api/sessions/${sessionId}`);
  if (!payload.ok) {
    showToast(payload.error || "Не удалось открыть сессию.");
    return;
  }
  state.sessionId = sessionId;
  state.latestTurn = payload.latest_turn;
  state.editingSessionId = null;
  renderSessions();
  renderMessages(payload.messages || []);
  renderStructured(payload.latest_turn?.structured_output || null);
  state.ui.sessionsDrawerOpen = false;
  state.ui.systemMenuOpen = false;
  state.ui.artifactsOpen = false;
  renderSurfaceState();
  if (state.user?.is_admin) {
    await loadInspector();
  }
}

function renderSessions() {
  const list = el("sessionsList");
  list.innerHTML = "";
  for (const session of state.sessions) {
    const row = document.createElement("div");
    row.className = `session-row ${session.id === state.sessionId ? "active" : ""}`;
    row.dataset.sessionId = String(session.id);
    if (state.editingSessionId === session.id) {
      row.innerHTML = `
        <form class="session-edit-form">
          <input class="session-title-input" value="${escapeHtml(session.title)}" maxlength="120" aria-label="Название чата" />
          <button type="submit" class="icon-btn compact-icon" title="Сохранить название" aria-label="Сохранить название">✓</button>
          <button type="button" class="icon-btn compact-icon" data-cancel-session="${session.id}" title="Отменить" aria-label="Отменить">×</button>
        </form>
      `;
      row.querySelector(".session-edit-form").addEventListener("submit", (event) => saveSessionTitle(event, session.id));
      row.querySelector("[data-cancel-session]").addEventListener("click", () => {
        state.editingSessionId = null;
        renderSessions();
      });
    } else {
      const owner = session.owner_email ? `<small>${escapeHtml(session.owner_email)}</small>` : "";
      row.innerHTML = `
        <button type="button" class="session-item ${session.id === state.sessionId ? "active" : ""}" title="${escapeHtml(session.owner_email ? `owner: ${session.owner_email}` : session.title)}">
          <span>${escapeHtml(session.title)}</span>
          ${owner}
        </button>
        <div class="session-actions" aria-label="Управление чатом">
          <button type="button" class="icon-btn compact-icon" data-edit-session="${session.id}" title="Переименовать чат" aria-label="Переименовать чат">✎</button>
          <button type="button" class="icon-btn compact-icon danger-btn" data-delete-session="${session.id}" title="Удалить чат" aria-label="Удалить чат">×</button>
        </div>
      `;
      row.querySelector(".session-item").addEventListener("click", () => openSession(session.id));
      row.querySelector("[data-edit-session]").addEventListener("click", () => {
        state.editingSessionId = session.id;
        renderSessions();
        list.querySelector(`[data-session-id="${session.id}"] .session-title-input`)?.focus();
      });
      row.querySelector("[data-delete-session]").addEventListener("click", () => deleteSession(session.id));
    }
    list.appendChild(row);
  }
  if (!state.sessions.length) {
    list.innerHTML = `<div class="empty-state">Нет сессий.</div>`;
  }
  renderTopbar();
}

async function saveSessionTitle(event, sessionId) {
  event.preventDefault();
  const form = event.currentTarget;
  const title = form.querySelector(".session-title-input").value.trim();
  const button = form.querySelector("button[type='submit']");
  setButtonBusy(button, true);
  const payload = await api(`/api/sessions/${sessionId}`, {method: "PATCH", body: JSON.stringify({title})});
  setButtonBusy(button, false);
  if (!payload.ok) {
    showToast(payload.error || "Не удалось переименовать чат.");
    return;
  }
  state.editingSessionId = null;
  showToast("Чат переименован.");
  await loadSessions();
  if (state.sessionId === sessionId) {
    await openSession(sessionId);
  }
}

async function deleteSession(sessionId) {
  const session = state.sessions.find((item) => item.id === sessionId);
  if (!session || !window.confirm(`Удалить чат "${session.title}"? Сообщения и результаты этого чата будут удалены.`)) {
    return;
  }
  const button = document.querySelector(`[data-delete-session="${sessionId}"]`);
  setButtonBusy(button, true);
  const payload = await api(`/api/sessions/${sessionId}`, {method: "DELETE"});
  setButtonBusy(button, false);
  if (!payload.ok) {
    showToast(payload.error || "Не удалось удалить чат.");
    return;
  }
  showToast("Чат удален.");
  if (state.sessionId === sessionId) {
    state.sessionId = null;
    state.latestTurn = null;
    renderMessages([]);
    renderStructured(null);
    state.ui.artifactsOpen = false;
    if (state.user?.is_admin) {
      el("inspectorPanel").innerHTML = "";
    }
  }
  await loadSessions();
  if (!state.sessionId && state.sessions.length) {
    await openSession(state.sessions[0].id);
  }
}

function renderMessages(messages) {
  const box = el("messages");
  box.classList.remove("empty-state");
  box.innerHTML = "";
  if (!messages.length) {
    box.classList.add("empty-state");
    box.textContent = "Напишите первое сообщение или выберите сценарий.";
    return;
  }
  for (const message of messages) {
    appendMessageBubble(message.role, message.content);
  }
  box.scrollTop = box.scrollHeight;
}

const chatMarkdownRenderer = createChatMarkdownRenderer();

function createChatMarkdownRenderer() {
  if (!window.markdownit) {
    return null;
  }
  const md = window.markdownit({
    breaks: true,
    html: false,
    linkify: false,
    typographer: false,
  });
  md.validateLink = isSafeMarkdownUrl;
  md.renderer.rules.image = (tokens, idx) => {
    const token = tokens[idx];
    return md.utils.escapeHtml(token.content || token.attrGet("alt") || "");
  };
  const defaultLinkOpen = md.renderer.rules.link_open || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options));
  md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    token.attrSet("target", "_blank");
    token.attrSet("rel", "noopener noreferrer");
    return defaultLinkOpen(tokens, idx, options, env, self);
  };
  return md;
}

function renderAssistantMarkdown(node, content) {
  // Sticky chat Markdown contract: render only LLM output, keep user input and
  // typing bubbles as plain DOM/text paths.
  node.classList.add("markdown-body");
  if (!chatMarkdownRenderer) {
    node.textContent = content;
    return;
  }
  try {
    node.innerHTML = chatMarkdownRenderer.render(String(content || ""));
  } catch (_error) {
    node.textContent = content;
  }
}

function isSafeMarkdownUrl(rawUrl) {
  const value = String(rawUrl || "").trim();
  if (!value) {
    return false;
  }
  const compact = value.replace(/[\u0000-\u001f\u007f\s]+/g, "").toLowerCase();
  if (compact.startsWith("javascript:") || compact.startsWith("vbscript:") || compact.startsWith("data:") || compact.startsWith("file:")) {
    return false;
  }
  try {
    const hasScheme = /^[a-z][a-z0-9+.-]*:/i.test(value);
    const parsed = new URL(value, window.location.origin);
    if (!hasScheme && parsed.origin === window.location.origin) {
      return true;
    }
    return ["http:", "https:", "mailto:"].includes(parsed.protocol);
  } catch (_error) {
    return false;
  }
}

function appendMessageBubble(role, content = "", options = {}) {
  const box = el("messages");
  const wasEmptyState = box.classList.contains("empty-state");
  box.classList.remove("empty-state");
  if (wasEmptyState) {
    box.innerHTML = "";
  }
  const node = document.createElement("div");
  node.className = `message ${role}${options.pending ? " pending" : ""}${options.typing ? " typing" : ""}`;
  if (options.typing) {
    node.setAttribute("role", "status");
    node.setAttribute("aria-live", "polite");
    node.setAttribute("aria-label", "Ассистент печатает");
    const dots = document.createElement("span");
    dots.className = "typing-dots";
    dots.setAttribute("aria-hidden", "true");
    dots.innerHTML = "<span></span><span></span><span></span>";
    node.appendChild(dots);
  } else if (role === "assistant") {
    renderAssistantMarkdown(node, content);
  } else {
    node.textContent = content;
  }
  box.appendChild(node);
  box.scrollTop = box.scrollHeight;
  return node;
}

function appendOptimisticChatTurn(text) {
  // Sticky chat turn UI contract: send shows the user bubble immediately and
  // uses a non-text typing bubble until server truth replaces local nodes.
  return {
    userNode: appendMessageBubble("user", text, {pending: true}),
    assistantNode: appendMessageBubble("assistant", "", {pending: true, typing: true}),
  };
}

function removeOptimisticChatTurn(turn) {
  turn?.assistantNode?.remove();
  turn?.userNode?.remove();
  const box = el("messages");
  if (!box.children.length) {
    renderMessages([]);
  }
}

async function sendMessage(event) {
  event?.preventDefault();
  if (state.voice.connecting || state.voice.recording || state.voice.transcribing) {
    showToast("Дождитесь завершения голосового ввода.");
    return;
  }
  const text = el("messageInput").value.trim();
  if (!text) return;
  setLoading(true);
  if (!state.sessionId) {
    await createSession(text.slice(0, 80));
  }
  if (!state.sessionId) {
    setLoading(false);
    return;
  }
  el("messageInput").value = "";
  const optimisticTurn = appendOptimisticChatTurn(text);
  try {
    const payload = await api(`/api/sessions/${state.sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({message: text}),
    });
    setLoading(false);
    if (!payload.ok) {
      setLoading(false);
      removeOptimisticChatTurn(optimisticTurn);
      el("messageInput").value = text;
      el("messageInput").focus();
      showToast(payload.error || "Не удалось отправить сообщение.");
      return;
    }
    await openSession(state.sessionId);
    setLoading(false);
  } catch (_error) {
    setLoading(false);
    removeOptimisticChatTurn(optimisticTurn);
    el("messageInput").value = text;
    el("messageInput").focus();
    showToast("Сервер недоступен. Сообщение не отправлено.");
  }
}

function setLoading(isLoading) {
  state.sending = isLoading;
  const sendBtn = el("sendBtn");
  const input = el("messageInput");
  sendBtn.disabled = isLoading;
  sendBtn.setAttribute("aria-busy", isLoading ? "true" : "false");
  sendBtn.textContent = "➤";
  input.disabled = isLoading;
  refreshVoiceControls();
}

function renderStructured(output) {
  renderDraft(output);
  renderWarnings(output);
  renderJson(output);
  renderArtifactSummary(output);
  renderSurfaceState();
}

function renderDraft(output) {
  const target = el("draftTab");
  if (!output) {
    target.innerHTML = `<div class="empty-state">Проект появится после уточнений.</div>`;
    return;
  }
  const draft = output.document_draft;
  const known = output.known_facts || [];
  const questions = output.open_questions || [];
  if (!draft) {
    target.innerHTML = `
      <div class="draft-status">Проект пока не сформирован</div>
      ${listBlock("Известно", known)}
      ${listBlock("Нужно уточнить", questions)}
      <p>${escapeHtml(output.next_step || "")}</p>
    `;
    return;
  }
  const sections = (draft.sections || [])
    .map((section) => `<h3>${escapeHtml(section.title || "")}</h3><p>${escapeHtml(section.content || "")}</p>`)
    .join("");
  target.innerHTML = `
    <div class="copy-row">
      <button id="copyDraftBtn">Скопировать документ</button>
    </div>
    <h2>${escapeHtml(draft.title || "Проект карты")}</h2>
    <div class="draft-status">Проект, требует проверки</div>
    <p><strong>Тип:</strong> ${escapeHtml(draft.document_type || "ТК/ТТК")}</p>
    ${sections}
  `;
  el("copyDraftBtn").addEventListener("click", () => copyText(textFromDraft(draft)));
}

function renderWarnings(output) {
  const target = el("warningsTab");
  if (!output) {
    target.innerHTML = `<div class="empty-state">Предупреждения и статусы появятся после ответа.</div>`;
    return;
  }
  const warnings = output.warnings || [];
  const statuses = output.data_statuses || [];
  target.innerHTML = `
    ${warnings.length ? `<div class="warning-list">${warnings.map((item) => `<div>⚠ ${escapeHtml(item)}</div>`).join("")}</div>` : `<div class="empty-state">Критических предупреждений нет.</div>`}
    <h3>Статусы данных</h3>
    <div class="status-list">
      ${statuses.map((item) => `<div class="status-item"><strong>${escapeHtml(item.field || "")}</strong><br><span>${escapeHtml(item.status || "")}</span><br><small>${escapeHtml(item.comment || "")}</small></div>`).join("") || `<div class="empty-state">Статусы пока не заполнены.</div>`}
    </div>
  `;
}

function renderJson(output) {
  const target = el("jsonTab");
  if (!output) {
    target.innerHTML = `<div class="empty-state">Structured JSON появится вместе с результатом.</div>`;
    return;
  }
  const json = JSON.stringify(output.structured_json || output, null, 2);
  target.innerHTML = `
    <div class="copy-row"><button id="copyJsonBtn">Скопировать JSON</button></div>
    <pre>${escapeHtml(json)}</pre>
  `;
  el("copyJsonBtn").addEventListener("click", () => copyText(json));
}

async function loadUsers() {
  if (!state.user?.is_admin) return;
  const payload = await api("/api/admin/users");
  if (!payload.ok) {
    el("usersPanel").innerHTML = `<div class="warning-list">${escapeHtml(payload.error || "Пользователи недоступны.")}</div>`;
    return;
  }
  state.users = payload.users || [];
  renderUsers();
}

function renderUsers() {
  const panel = state.user?.is_admin && state.adminScreen === "users" ? el("adminWorkspace") : el("usersPanel");
  if (!state.user?.is_admin) {
    panel.innerHTML = "";
    return;
  }
  const rows = state.users.map((user) => userRowHtml(user)).join("");
  panel.innerHTML = `
    <div class="admin-users">
      <div class="hint-line">
        <span class="hint-icon" title="MVP CRUD пользователей без production IAM/RBAC" aria-label="MVP CRUD пользователей">ⓘ</span>
        <span>Только роли user/admin. Секреты и password hashes не показываются.</span>
      </div>
      <form id="createUserForm" class="user-create-form">
        <label>Email
          <input id="newUserEmail" type="email" autocomplete="off" placeholder="user@example.com" required />
        </label>
        <label>Роль
          <select id="newUserRole">
            <option value="user">user</option>
            <option value="admin">admin</option>
          </select>
        </label>
        <label>Пароль
          <input id="newUserPassword" type="password" autocomplete="new-password" placeholder="Временный пароль" required />
        </label>
        <button type="submit">Создать</button>
      </form>
      <div class="users-list">${rows || `<div class="empty-state">Пользователей пока нет.</div>`}</div>
    </div>
  `;
  el("createUserForm").addEventListener("submit", createUser);
  panel.querySelectorAll("[data-save-user]").forEach((button) => {
    button.addEventListener("click", () => saveUser(Number(button.dataset.saveUser)));
  });
  panel.querySelectorAll("[data-delete-user]").forEach((button) => {
    button.addEventListener("click", () => deleteUser(Number(button.dataset.deleteUser)));
  });
}

function userRowHtml(user) {
  const current = user.is_current ? `<span class="badge">текущий</span>` : "";
  const passwordState = user.has_password ? "пароль задан" : "без пароля";
  const deleteDisabled = user.is_current ? "disabled title=\"Нельзя удалить текущего admin\"" : "";
  return `
    <div class="user-row" data-user-id="${user.id}">
      <div class="user-meta">
        <strong>#${user.id}</strong>
        ${current}
        <span class="muted">${escapeHtml(passwordState)}</span>
      </div>
      <label>Email
        <input class="user-email" type="email" value="${escapeHtml(user.email)}" />
      </label>
      <label>Роль
        <select class="user-role">
          <option value="user" ${user.role === "user" ? "selected" : ""}>user</option>
          <option value="admin" ${user.role === "admin" ? "selected" : ""}>admin</option>
        </select>
      </label>
      <label>Новый пароль
        <input class="user-password" type="password" autocomplete="new-password" placeholder="Не менять" />
      </label>
      <div class="user-actions">
        <button type="button" data-save-user="${user.id}">Сохранить</button>
        <button type="button" class="danger-btn" data-delete-user="${user.id}" ${deleteDisabled}>Удалить</button>
      </div>
    </div>
  `;
}

async function createUser(event) {
  event.preventDefault();
  const button = event.submitter;
  setButtonBusy(button, true);
  const payload = await api("/api/admin/users", {
    method: "POST",
    body: JSON.stringify({
      email: el("newUserEmail").value,
      role: el("newUserRole").value,
      password: el("newUserPassword").value,
    }),
  });
  setButtonBusy(button, false);
  if (!payload.ok) {
    showToast(payload.error || "Не удалось создать пользователя.");
    return;
  }
  showToast("Пользователь создан.");
  await loadUsers();
}

async function saveUser(userId) {
  const row = document.querySelector(`[data-user-id="${userId}"]`);
  if (!row) return;
  const button = row.querySelector("[data-save-user]");
  const password = row.querySelector(".user-password").value;
  const body = {
    email: row.querySelector(".user-email").value,
    role: row.querySelector(".user-role").value,
  };
  if (password.trim()) {
    body.password = password;
  }
  setButtonBusy(button, true);
  const payload = await api(`/api/admin/users/${userId}`, {method: "PATCH", body: JSON.stringify(body)});
  setButtonBusy(button, false);
  if (!payload.ok) {
    showToast(payload.error || "Не удалось сохранить пользователя.");
    return;
  }
  showToast("Пользователь сохранен.");
  await loadUsers();
}

async function deleteUser(userId) {
  const user = state.users.find((item) => item.id === userId);
  if (!user || !window.confirm(`Удалить пользователя ${user.email}? Его demo-сессии будут удалены.`)) {
    return;
  }
  const button = document.querySelector(`[data-delete-user="${userId}"]`);
  setButtonBusy(button, true);
  const payload = await api(`/api/admin/users/${userId}`, {method: "DELETE"});
  setButtonBusy(button, false);
  if (!payload.ok) {
    showToast(payload.error || "Не удалось удалить пользователя.");
    return;
  }
  showToast("Пользователь удален.");
  await loadUsers();
}

function renderAdminNav() {
  const items = [
    {key: "dashboard", icon: "▦", label: "Дашборд", title: "Чаты и активность"},
    {key: "prompts", icon: "◎", label: "Промты", title: "Prompt/context layers"},
    {key: "users", icon: "☷", label: "Пользователи", title: "Пользователи Demo MVP"},
  ];
  el("sessionsList").innerHTML = items.map((item) => `
    <button type="button" class="admin-nav-item ${state.adminScreen === item.key ? "active" : ""}" data-admin-screen="${item.key}" title="${item.title}" aria-label="${item.title}">
      <span class="admin-nav-icon">${item.icon}</span>
      <span>${item.label}</span>
    </button>
  `).join("");
  document.querySelectorAll("[data-admin-screen]").forEach((button) => {
    button.addEventListener("click", () => setAdminScreen(button.dataset.adminScreen));
  });
}

function setAdminScreen(screen) {
  if (!state.user?.is_admin) return;
  state.adminScreen = screen || "dashboard";
  renderAdminNav();
  setAdminWorkspaceLoading();
  if (state.adminScreen === "prompts") {
    loadAdminContext();
  } else if (state.adminScreen === "users") {
    loadUsers();
  } else {
    loadAdminDashboard();
  }
}

function setAdminWorkspaceLoading() {
  el("adminWorkspace").innerHTML = `<div class="admin-screen"><div class="empty-state">Загрузка...</div></div>`;
}

async function loadAdminDashboard() {
  const payload = await api("/api/admin/dashboard");
  if (!payload.ok) {
    el("adminWorkspace").innerHTML = `<div class="warning-list">${escapeHtml(payload.error || "Дашборд недоступен.")}</div>`;
    return;
  }
  state.adminDashboard = payload.dashboard;
  renderAdminDashboard();
}

function renderAdminDashboard() {
  const dashboard = state.adminDashboard || {};
  const periods = dashboard.periods || [];
  const latest = dashboard.latest_activity || [];
  el("adminWorkspace").innerHTML = `
    <div class="admin-screen">
      <div class="admin-screen-header">
        <div>
          <h1>Дашборд чатов</h1>
          <p class="muted">Read-only обзор demo sessions, активности и approximate token usage.</p>
        </div>
        <button type="button" class="icon-btn" id="refreshDashboardBtn" title="Обновить" aria-label="Обновить">↻</button>
      </div>
      <div class="metrics-grid">
        ${periods.map(periodMetricCard).join("")}
      </div>
      <div class="admin-two-column">
        <section class="admin-card">
          <h2>Последняя активность</h2>
          ${latest.length ? latestActivityTable(latest) : `<div class="empty-state">Активных чатов пока нет.</div>`}
        </section>
        <section class="admin-card" id="adminChatPreview">
          <h2>Просмотр чата</h2>
          <div class="empty-state">Выберите чат в таблице слева.</div>
        </section>
      </div>
    </div>
  `;
  el("refreshDashboardBtn").addEventListener("click", loadAdminDashboard);
  document.querySelectorAll("[data-admin-session-preview]").forEach((button) => {
    button.addEventListener("click", () => loadAdminSessionPreview(Number(button.dataset.adminSessionPreview)));
  });
}

function periodMetricCard(period) {
  const maxTokens = Math.max(...(state.adminDashboard?.periods || []).map((item) => item.estimated_tokens || 0), 1);
  const width = Math.max(4, Math.round(((period.estimated_tokens || 0) / maxTokens) * 100));
  return `
    <section class="metric-card">
      <div class="metric-title">${escapeHtml(period.label)}</div>
      <div class="metric-main">${formatNumber(period.sessions)} чатов</div>
      <div class="metric-sub">${formatNumber(period.messages)} сообщений · ${formatNumber(period.turns)} turns</div>
      <div class="metric-sub">${formatNumber(period.active_users)} активных users · ${formatNumber(period.document_drafts)} drafts</div>
      <div class="metric-sub">≈ ${formatNumber(period.estimated_tokens)} tokens</div>
      <div class="metric-bar" aria-hidden="true"><span style="width:${width}%"></span></div>
    </section>
  `;
}

function latestActivityTable(items) {
  return `
    <div class="activity-list">
      ${items.map((item) => `
        <button type="button" class="activity-row ${state.adminSelectedSessionId === item.id ? "active" : ""}" data-admin-session-preview="${item.id}" title="Открыть read-only просмотр чата" aria-label="Открыть чат ${item.id}">
          <span class="activity-title">${escapeHtml(item.title)}</span>
          <span>${escapeHtml(item.owner_email || "")}</span>
          <span>${formatDate(item.last_message_at || item.updated_at)}</span>
          <span>${formatNumber(item.message_count)} msg · ${formatNumber(item.turn_count)} turns</span>
          <span>${escapeHtml(item.workflow_status || "no status")}</span>
          <span>≈ ${formatNumber(item.estimated_tokens)} tok</span>
        </button>
      `).join("")}
    </div>
  `;
}

async function loadAdminSessionPreview(sessionId) {
  state.adminSelectedSessionId = sessionId;
  renderAdminDashboard();
  const target = el("adminChatPreview");
  target.innerHTML = `<h2>Просмотр чата</h2><div class="empty-state">Загрузка...</div>`;
  const payload = await api(`/api/sessions/${sessionId}`);
  if (!payload.ok) {
    target.innerHTML = `<h2>Просмотр чата</h2><div class="warning-list">${escapeHtml(payload.error || "Чат недоступен.")}</div>`;
    return;
  }
  const session = payload.session || {};
  const messages = payload.messages || [];
  const latest = payload.latest_turn || {};
  target.innerHTML = `
    <div class="admin-preview-header">
      <div>
        <h2>${escapeHtml(session.title || `Чат #${sessionId}`)}</h2>
        <p class="muted">${escapeHtml(session.owner_email || "")} · ${formatDate(session.updated_at)}</p>
      </div>
      <button type="button" class="icon-btn" id="openPromptForSessionBtn" title="Открыть context trace" aria-label="Открыть context trace">◎</button>
    </div>
    <div class="admin-message-preview">
      ${messages.map((message) => `<div class="message ${escapeHtml(message.role)}">${escapeHtml(message.content)}</div>`).join("") || `<div class="empty-state">Сообщений нет.</div>`}
    </div>
    <h3>Latest structured output</h3>
    <pre>${escapeHtml(JSON.stringify(latest.structured_output || null, null, 2))}</pre>
  `;
  el("openPromptForSessionBtn").addEventListener("click", () => setAdminScreen("prompts"));
}

async function loadAdminContext() {
  const payload = await api("/api/admin/context");
  if (!payload.ok) {
    el("adminWorkspace").innerHTML = `<div class="warning-list">${escapeHtml(payload.error || "Context workspace недоступен.")}</div>`;
    return;
  }
  if (state.adminSelectedSessionId) {
    const selected = await api(`/api/sessions/${state.adminSelectedSessionId}/inspector`);
    if (selected.ok) {
      payload.selected_session = selected;
      payload.selected_session_id = state.adminSelectedSessionId;
    }
  }
  state.adminContext = payload;
  renderAdminContext();
}

function renderAdminContext() {
  const payload = state.adminContext || {};
  const selected = payload.selected_session || null;
  const latest = selected?.latest_turn || payload.latest_turn || {};
  const trace = latest.trace || {};
  el("adminWorkspace").innerHTML = `
    <div class="admin-screen">
      <div class="admin-screen-header">
        <div>
          <h1>Промты и context window</h1>
          <p class="muted">Read-only просмотр manifest, markdown layers, schema и последнего assembled context.</p>
        </div>
        <button type="button" class="icon-btn" id="refreshContextBtn" title="Обновить" aria-label="Обновить">↻</button>
      </div>
      <div class="context-summary-grid">
        <section class="admin-card">
          <h2>Manifest</h2>
          <pre>${escapeHtml(JSON.stringify(payload.manifest || {}, null, 2))}</pre>
        </section>
        <section class="admin-card">
          <h2>Health</h2>
          <pre>${escapeHtml(JSON.stringify(payload.health || {}, null, 2))}</pre>
          <p class="muted">Token usage: ${escapeHtml(payload.token_policy || "")}</p>
        </section>
      </div>
      <div class="admin-two-column wide-left">
        <section class="admin-card">
          <div class="admin-card-title">
            <h2>Markdown layers</h2>
            <button type="button" class="icon-btn compact-icon" data-copy-admin="static" title="Скопировать static context" aria-label="Скопировать static context">⧉</button>
          </div>
          ${(payload.layers || []).map(promptLayerHtml).join("") || `<div class="empty-state">Layers не загружены.</div>`}
        </section>
        <section class="admin-card">
          <div class="admin-card-title">
          <h2>Context window</h2>
          <button type="button" class="icon-btn compact-icon" data-copy-admin="assembled" title="Скопировать assembled preview" aria-label="Скопировать assembled preview">⧉</button>
        </div>
        <h3>Latest turn</h3>
          <p class="muted">${latest.id ? `${selected ? `Selected session #${payload.selected_session_id} · ` : ""}Turn #${latest.id} · ${escapeHtml(latest.owner_email || "")} · ${formatDate(latest.created_at)}` : "Turn results еще нет."}</p>
          <h3>Assembled preview</h3>
          <pre>${escapeHtml(trace.assembled_context_preview || "Нет assembled context preview.")}</pre>
          <h3>Structured output schema</h3>
          <pre>${escapeHtml(JSON.stringify(payload.structured_output_schema || null, null, 2))}</pre>
          <h3>Latest structured output</h3>
          <pre>${escapeHtml(JSON.stringify(latest.structured_output || null, null, 2))}</pre>
        </section>
      </div>
    </div>
  `;
  el("refreshContextBtn").addEventListener("click", loadAdminContext);
  document.querySelectorAll("[data-copy-layer]").forEach((button) => {
    button.addEventListener("click", () => {
      const layer = (payload.layers || []).find((item) => item.file === button.dataset.copyLayer);
      copyText(layer?.text || "");
    });
  });
  document.querySelectorAll("[data-copy-admin]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.copyAdmin;
      if (key === "static") {
        copyText(payload.static_context_preview || "");
      } else if (key === "assembled") {
        copyText(trace.assembled_context_preview || "");
      }
    });
  });
}

function promptLayerHtml(layer) {
  return `
    <details class="prompt-layer">
      <summary>
        <span>${formatNumber(layer.order)}. ${escapeHtml(layer.file)}</span>
        <span class="badge">${escapeHtml(layer.status || "")}</span>
      </summary>
      <div class="layer-meta">
        <div><strong>role:</strong> ${escapeHtml(layer.role || "")}</div>
        <div><strong>source:</strong> ${escapeHtml(layer.source || "")}</div>
        <div><strong>description:</strong> ${escapeHtml(layer.description || "")}</div>
      </div>
      <div class="copy-row">
        <button type="button" class="icon-btn compact-icon" data-copy-layer="${escapeHtml(layer.file)}" title="Скопировать layer" aria-label="Скопировать layer">⧉</button>
      </div>
      <pre>${escapeHtml(layer.text || "")}</pre>
    </details>
  `;
}

function setButtonBusy(button, isBusy) {
  if (!button) return;
  button.disabled = isBusy;
  button.dataset.busy = isBusy ? "true" : "false";
}

function initVoiceInput() {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  state.voice.supported = !!(navigator.mediaDevices?.getUserMedia && AudioContextClass);
  refreshVoiceControls();
  updateVoiceStatus("");
  if (!state.voice.supported) {
    el("voiceBtn").title = "Голосовой ввод недоступен в этом браузере";
    el("voiceBtn").setAttribute("aria-label", "Голосовой ввод недоступен");
  }
}

async function toggleVoiceRecording() {
  if (state.voice.transcribing) return;
  if (state.voice.recording) {
    await stopVoiceRecording({transcribe: true});
    return;
  }
  await startVoiceRecording();
}

async function startVoiceRecording() {
  if (!state.voice.supported) {
    showToast("Браузер не поддерживает запись аудио.");
    return;
  }
  if (!state.voice.enabled) {
    updateVoiceStatus("Голосовой ввод выключен.");
    refreshVoiceControls();
    return;
  }
  if (state.voice.streamingEnabled && window.WebSocket) {
    try {
      await startLiveVoiceRecording();
      return;
    } catch (error) {
      cleanupLiveVoiceSession();
      if (!state.voice.batchEnabled) {
        const message = error?.message || "Не удалось запустить потоковый голосовой ввод.";
        updateVoiceStatus(message);
        showToast(message);
        refreshVoiceControls();
        return;
      }
      updateVoiceStatus("Потоковый режим недоступен. Использую обычную запись.");
    }
  }
  if (!state.voice.batchEnabled) {
    updateVoiceStatus("Голосовой ввод выключен.");
    refreshVoiceControls();
    return;
  }
  await startBatchVoiceRecording();
}

async function startBatchVoiceRecording() {
  if (!state.voice.supported) {
    showToast("Браузер не поддерживает запись аудио.");
    return;
  }
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    const stream = await navigator.mediaDevices.getUserMedia({audio: true});
    const audioContext = new AudioContextClass();
    const source = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    const gain = audioContext.createGain();
    gain.gain.value = 0;
    state.voice.mode = "batch";
    state.voice.chunks = [];
    state.voice.totalSamples = 0;
    state.voice.inputSampleRate = audioContext.sampleRate;
    processor.onaudioprocess = (event) => {
      if (!state.voice.recording) return;
      const input = event.inputBuffer.getChannelData(0);
      state.voice.chunks.push(new Float32Array(input));
      state.voice.totalSamples += input.length;
    };
    source.connect(processor);
    processor.connect(gain);
    gain.connect(audioContext.destination);
    state.voice.audioContext = audioContext;
    state.voice.source = source;
    state.voice.processor = processor;
    state.voice.gain = gain;
    state.voice.stream = stream;
    state.voice.startedAt = Date.now();
    state.voice.recording = true;
    state.voice.timerId = setInterval(updateVoiceRecordingUi, 250);
    updateVoiceRecordingUi();
    refreshVoiceControls();
  } catch (_error) {
    cleanupVoiceRecorder();
    showToast("Не удалось получить доступ к микрофону.");
    updateVoiceStatus("Микрофон недоступен.");
  }
}

async function cancelVoiceRecording() {
  if (!state.voice.recording && !state.voice.connecting) return;
  await stopVoiceRecording({transcribe: false});
  updateVoiceStatus("");
  showToast("Запись отменена.");
}

async function stopVoiceRecording({transcribe}) {
  if (state.voice.mode === "live" || state.voice.connecting) {
    await stopLiveVoiceRecording({transcribe});
    return;
  }
  if (!state.voice.recording) return;
  const durationMs = Date.now() - state.voice.startedAt;
  state.voice.recording = false;
  clearInterval(state.voice.timerId);
  state.voice.timerId = null;
  cleanupVoiceRecorder();
  refreshVoiceControls();
  if (!transcribe) {
    state.voice.chunks = [];
    state.voice.totalSamples = 0;
    return;
  }
  if (!state.voice.totalSamples) {
    updateVoiceStatus("Запись пустая.");
    showToast("Запись пустая.");
    return;
  }
  const wavBlob = encodeVoiceToWav();
  state.voice.chunks = [];
  state.voice.totalSamples = 0;
  await transcribeVoiceBlob(wavBlob, durationMs);
}

async function startLiveVoiceRecording() {
  state.voice.mode = "live";
  state.voice.connecting = true;
  state.voice.liveHadError = false;
  state.voice.liveTranscript = "";
  state.voice.setupComplete = false;
  state.voice.chunks = [];
  state.voice.totalSamples = 0;
  refreshVoiceControls();
  updateVoiceStatus("Подключаю потоковое распознавание...");

  const tokenPayload = await api("/api/live-voice/token", {method: "POST", body: "{}"});
  if (!tokenPayload.ok) {
    throw new Error(tokenPayload.error || "Не удалось получить временный Live API token.");
  }
  state.voice.streamingTransport = tokenPayload.transport || state.voice.streamingTransport;
  updateVoiceStatus("Подключаю потоковое распознавание...");
  if (!tokenPayload.websocket_url) {
    throw new Error("Сервер не вернул Live Voice WebSocket URL.");
  }
  const websocket = new WebSocket(tokenPayload.websocket_url);
  state.voice.websocket = websocket;
  await waitForLiveSetup(websocket, tokenPayload.setup || {});
  await startLiveAudioCapture(Number(tokenPayload.input_sample_rate || state.voice.liveInputSampleRate));
}

function waitForLiveSetup(websocket, setup) {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      reject(new Error("Live API не подтвердил подключение."));
    }, 10000);
    state.voice.setupResolver = () => {
      clearTimeout(timeoutId);
      resolve();
    };
    state.voice.setupRejecter = (error) => {
      clearTimeout(timeoutId);
      reject(error);
    };
    websocket.onopen = () => {
      websocket.send(JSON.stringify({setup}));
    };
    websocket.onmessage = handleLiveVoiceMessage;
    websocket.onerror = () => {
      state.voice.liveHadError = true;
      if (!state.voice.setupComplete) {
        state.voice.setupRejecter?.(new Error("Ошибка WebSocket Live API."));
        return;
      }
      if (state.voice.recording) {
        handleUnexpectedLiveClose();
      }
    };
    websocket.onclose = () => {
      if (state.voice.connecting && !state.voice.setupComplete) {
        state.voice.setupRejecter?.(new Error("Live API закрыл соединение до начала записи."));
        return;
      }
      if (state.voice.recording) {
        handleUnexpectedLiveClose();
      }
    };
  });
}

async function startLiveAudioCapture(targetSampleRate) {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {channelCount: 1, echoCancellation: true, noiseSuppression: true},
  });
  const audioContext = new AudioContextClass();
  await audioContext.resume?.();
  const source = audioContext.createMediaStreamSource(stream);
  const processor = audioContext.createScriptProcessor(4096, 1, 1);
  const gain = audioContext.createGain();
  gain.gain.value = 0;
  state.voice.inputSampleRate = audioContext.sampleRate;
  state.voice.liveInputSampleRate = targetSampleRate || 16000;
  processor.onaudioprocess = (event) => {
    if (!state.voice.recording || state.voice.mode !== "live") return;
    const input = event.inputBuffer.getChannelData(0);
    const samples = downsampleBuffer(input, state.voice.inputSampleRate, state.voice.liveInputSampleRate);
    const pcm = float32ToPcm16(samples);
    state.voice.totalSamples += samples.length;
    sendLiveAudioChunk(pcm, state.voice.liveInputSampleRate);
  };
  source.connect(processor);
  processor.connect(gain);
  gain.connect(audioContext.destination);
  state.voice.audioContext = audioContext;
  state.voice.source = source;
  state.voice.processor = processor;
  state.voice.gain = gain;
  state.voice.stream = stream;
  state.voice.startedAt = Date.now();
  state.voice.connecting = false;
  state.voice.recording = true;
  state.voice.timerId = setInterval(updateVoiceRecordingUi, 250);
  updateVoiceRecordingUi();
  refreshVoiceControls();
}

async function stopLiveVoiceRecording({transcribe}) {
  const websocket = state.voice.websocket;
  const hadText = !!state.voice.liveTranscript.trim();
  state.voice.connecting = false;
  state.voice.recording = false;
  clearInterval(state.voice.timerId);
  state.voice.timerId = null;
  cleanupVoiceRecorder();
  refreshVoiceControls();

  if (!transcribe) {
    closeLiveWebSocket(websocket);
    cleanupLiveVoiceSession();
    return;
  }

  state.voice.transcribing = true;
  refreshVoiceControls();
  updateVoiceStatus(hadText ? "Завершаю потоковый транскрипт..." : "Завершаю потоковое распознавание...");
  if (websocket?.readyState === WebSocket.OPEN) {
    websocket.send(JSON.stringify({realtimeInput: {audioStreamEnd: true}}));
    await delay(1200);
  }
  closeLiveWebSocket(websocket);
  const transcript = state.voice.liveTranscript.trim();
  if (transcript) {
    insertTranscript(transcript);
    updateVoiceStatus("Распознано потоково. Проверьте текст перед отправкой.");
    showToast("Текст распознан.");
  } else {
    updateVoiceStatus("Потоковый транскрипт пустой.");
    showToast("Транскрипт пустой.");
  }
  state.voice.transcribing = false;
  cleanupLiveVoiceSession();
  refreshVoiceControls();
}

function handleLiveVoiceMessage(event) {
  const parse = (raw) => {
    try {
      return JSON.parse(raw);
    } catch (_error) {
      return null;
    }
  };
  const handlePayload = (payload) => {
    if (!payload) return;
    if (payload.setupComplete) {
      state.voice.setupComplete = true;
      state.voice.setupResolver?.();
      return;
    }
    const transcript = payload.serverContent?.inputTranscription?.text || "";
    if (transcript) {
      appendLiveTranscript(transcript);
    }
    if (payload.serverContent?.turnComplete && state.voice.liveTranscript.trim()) {
      updateVoiceStatus(`Слышу: ${shortVoicePreview(state.voice.liveTranscript)}`);
    }
    if (payload.goAway?.timeLeft) {
      updateVoiceStatus("Live API скоро закроет соединение. Завершите запись.");
    }
  };
  if (event.data instanceof Blob) {
    event.data.text().then((text) => handlePayload(parse(text)));
    return;
  }
  handlePayload(parse(String(event.data)));
}

function appendLiveTranscript(text) {
  const incoming = String(text || "").trim();
  if (!incoming) return;
  const current = state.voice.liveTranscript.trim();
  if (!current) {
    state.voice.liveTranscript = incoming;
  } else if (incoming.startsWith(current)) {
    state.voice.liveTranscript = incoming;
  } else if (!current.endsWith(incoming)) {
    state.voice.liveTranscript = `${current} ${incoming}`.replace(/\s+/g, " ");
  }
  updateVoiceStatus(`Слышу: ${shortVoicePreview(state.voice.liveTranscript)}`);
}

function shortVoicePreview(text) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  return clean.length > 90 ? `...${clean.slice(-90)}` : clean;
}

function sendLiveAudioChunk(pcmBytes, sampleRate) {
  const websocket = state.voice.websocket;
  if (!websocket || websocket.readyState !== WebSocket.OPEN || !state.voice.setupComplete) return;
  if (websocket.bufferedAmount > 1_000_000) return;
  websocket.send(JSON.stringify({
    realtimeInput: {
      audio: {
        data: bytesToBase64(pcmBytes),
        mimeType: `audio/pcm;rate=${sampleRate}`,
      },
    },
  }));
}

function float32ToPcm16(samples) {
  const bytes = new Uint8Array(samples.length * 2);
  const view = new DataView(bytes.buffer);
  for (let i = 0; i < samples.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(i * 2, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
  }
  return bytes;
}

function bytesToBase64(bytes) {
  let binary = "";
  const chunkSize = 0x8000;
  for (let i = 0; i < bytes.length; i += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
  }
  return btoa(binary);
}

function closeLiveWebSocket(websocket) {
  if (websocket && websocket.readyState <= WebSocket.OPEN) {
    websocket.close();
  }
}

function cleanupLiveVoiceSession() {
  closeLiveWebSocket(state.voice.websocket);
  state.voice.mode = "batch";
  state.voice.connecting = false;
  state.voice.setupComplete = false;
  state.voice.setupResolver = null;
  state.voice.setupRejecter = null;
  state.voice.websocket = null;
  state.voice.liveHadError = false;
}

function handleUnexpectedLiveClose() {
  const transcript = state.voice.liveTranscript.trim();
  state.voice.recording = false;
  state.voice.connecting = false;
  clearInterval(state.voice.timerId);
  state.voice.timerId = null;
  cleanupVoiceRecorder();
  if (transcript) {
    insertTranscript(transcript);
    updateVoiceStatus("Соединение прервано. Полученный фрагмент вставлен в поле ввода.");
  } else {
    updateVoiceStatus("Соединение потокового распознавания прервано.");
  }
  cleanupLiveVoiceSession();
  refreshVoiceControls();
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function cleanupVoiceRecorder() {
  if (state.voice.processor) {
    state.voice.processor.disconnect();
    state.voice.processor.onaudioprocess = null;
  }
  state.voice.source?.disconnect();
  state.voice.gain?.disconnect();
  state.voice.stream?.getTracks().forEach((track) => track.stop());
  state.voice.audioContext?.close?.();
  state.voice.audioContext = null;
  state.voice.source = null;
  state.voice.processor = null;
  state.voice.gain = null;
  state.voice.stream = null;
}

function updateVoiceRecordingUi() {
  if (!state.voice.recording) return;
  const elapsedSeconds = Math.floor((Date.now() - state.voice.startedAt) / 1000);
  const remaining = Math.max(0, state.voice.maxSeconds - elapsedSeconds);
  if (remaining <= 0) {
    stopVoiceRecording({transcribe: true});
    return;
  }
  const elapsedLabel = formatDuration(elapsedSeconds);
  const maxLabel = formatDuration(state.voice.maxSeconds);
  const livePrefix = state.voice.mode === "live" && state.voice.liveTranscript.trim()
    ? `Слышу: ${shortVoicePreview(state.voice.liveTranscript)} · `
    : "";
  if (remaining <= state.voice.countdownSeconds) {
    updateVoiceStatus(`${livePrefix}Запись ${elapsedLabel} / ${maxLabel}. Автостоп через ${remaining} сек.`);
  } else {
    updateVoiceStatus(`${livePrefix}Запись ${elapsedLabel} / ${maxLabel}`);
  }
}

function encodeVoiceToWav() {
  const merged = mergeAudioChunks(state.voice.chunks, state.voice.totalSamples);
  const samples = downsampleBuffer(merged, state.voice.inputSampleRate, 16000);
  const wav = encodeWav(samples, 16000);
  return new Blob([wav], {type: "audio/wav"});
}

function mergeAudioChunks(chunks, totalSamples) {
  const result = new Float32Array(totalSamples);
  let offset = 0;
  for (const chunk of chunks) {
    result.set(chunk, offset);
    offset += chunk.length;
  }
  return result;
}

function downsampleBuffer(buffer, inputRate, outputRate) {
  if (!inputRate || inputRate === outputRate) return buffer;
  if (inputRate < outputRate) return buffer;
  const ratio = inputRate / outputRate;
  const newLength = Math.floor(buffer.length / ratio);
  const result = new Float32Array(newLength);
  let offsetBuffer = 0;
  for (let offsetResult = 0; offsetResult < newLength; offsetResult += 1) {
    const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio);
    let accum = 0;
    let count = 0;
    for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i += 1) {
      accum += buffer[i];
      count += 1;
    }
    result[offsetResult] = count ? accum / count : 0;
    offsetBuffer = nextOffsetBuffer;
  }
  return result;
}

function encodeWav(samples, sampleRate) {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);
  writeAscii(view, 0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeAscii(view, 8, "WAVE");
  writeAscii(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeAscii(view, 36, "data");
  view.setUint32(40, samples.length * 2, true);
  let offset = 44;
  for (let i = 0; i < samples.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
    offset += 2;
  }
  return buffer;
}

function writeAscii(view, offset, text) {
  for (let i = 0; i < text.length; i += 1) {
    view.setUint8(offset + i, text.charCodeAt(i));
  }
}

async function transcribeVoiceBlob(blob, durationMs) {
  state.voice.transcribing = true;
  refreshVoiceControls();
  updateVoiceStatus("Распознаю аудио...");
  try {
    const response = await fetch("/api/transcribe", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "audio/wav",
        "X-Audio-Duration-Ms": String(Math.max(1, Math.round(durationMs))),
      },
      body: blob,
    });
    const payload = await response.json().catch(() => ({ok: false, error: "Некорректный ответ сервера."}));
    if (!response.ok || !payload.ok) {
      updateVoiceStatus(payload.error || "Не удалось распознать аудио.");
      showToast(payload.error || "Не удалось распознать аудио.");
      return;
    }
    insertTranscript(payload.text || "");
    updateVoiceStatus("Распознано. Проверьте текст перед отправкой.");
    showToast("Текст распознан.");
  } catch (_error) {
    updateVoiceStatus("Сервер недоступен. Повторите распознавание.");
    showToast("Сервер недоступен.");
  } finally {
    state.voice.transcribing = false;
    refreshVoiceControls();
  }
}

function insertTranscript(text) {
  const input = el("messageInput");
  const transcript = text.trim();
  if (!transcript) return;
  const current = input.value.trim();
  input.value = current ? `${current}\n${transcript}` : transcript;
  input.focus();
}

function updateVoiceStatus(text) {
  const node = el("voiceStatus");
  node.textContent = text;
  node.classList.toggle("hidden", !text);
}

function voicePrefersLiveMode() {
  return state.voice.streamingEnabled && !!window.WebSocket;
}

function currentVoiceUiMode() {
  const busy = state.voice.connecting || state.voice.recording || state.voice.transcribing;
  if (busy && state.voice.mode === "live") return "live";
  if (busy && state.voice.mode === "batch") return "batch";
  return voicePrefersLiveMode() ? "live" : "batch";
}

function ensureVoiceButtonChrome(voiceBtn) {
  if (voiceBtn.querySelector(".voice-icon")) return;
  voiceBtn.textContent = "";
  const pulse = document.createElement("span");
  pulse.className = "voice-pulse";
  pulse.setAttribute("aria-hidden", "true");
  const icon = document.createElement("span");
  icon.className = "voice-icon";
  icon.setAttribute("aria-hidden", "true");
  voiceBtn.append(pulse, icon);
}

function refreshVoiceControls() {
  const voiceBtn = el("voiceBtn");
  const cancelBtn = el("voiceCancelBtn");
  const sendBtn = el("sendBtn");
  const busy = state.voice.connecting || state.voice.recording || state.voice.transcribing;
  const voiceEnabled = state.voice.enabled && (state.voice.batchEnabled || state.voice.streamingEnabled);
  const uiMode = currentVoiceUiMode();
  ensureVoiceButtonChrome(voiceBtn);
  voiceBtn.disabled = !state.voice.supported || !voiceEnabled || state.voice.connecting || state.voice.transcribing;
  voiceBtn.classList.toggle("voice-live", uiMode === "live");
  voiceBtn.classList.toggle("voice-batch", uiMode === "batch");
  voiceBtn.classList.toggle("recording", state.voice.recording);
  voiceBtn.classList.toggle("connecting", state.voice.connecting);
  voiceBtn.classList.toggle("transcribing", state.voice.transcribing);
  voiceBtn.classList.toggle("streaming", uiMode === "live" && (state.voice.connecting || state.voice.recording));
  voiceBtn.dataset.voiceMode = uiMode;
  voiceBtn.setAttribute("aria-busy", state.voice.connecting || state.voice.transcribing ? "true" : "false");
  voiceBtn.setAttribute("aria-pressed", state.voice.recording || state.voice.connecting ? "true" : "false");
  if (!voiceEnabled) {
    voiceBtn.title = "Голосовой ввод выключен";
    voiceBtn.setAttribute("aria-label", "Голосовой ввод выключен");
  } else if (!state.voice.supported) {
    voiceBtn.title = "Голосовой ввод недоступен в этом браузере";
    voiceBtn.setAttribute("aria-label", "Голосовой ввод недоступен");
  } else if (state.voice.connecting) {
    voiceBtn.title = uiMode === "live" ? "Подключается потоковый голосовой ввод" : "Готовится запись";
    voiceBtn.setAttribute("aria-label", voiceBtn.title);
  } else if (state.voice.transcribing) {
    voiceBtn.title = uiMode === "live" ? "Завершается потоковый транскрипт" : "Распознаётся запись";
    voiceBtn.setAttribute("aria-label", voiceBtn.title);
  } else if (state.voice.recording) {
    voiceBtn.title = uiMode === "live" ? "Остановить потоковый ввод" : "Остановить запись и распознать";
    voiceBtn.setAttribute("aria-label", voiceBtn.title);
  } else {
    voiceBtn.title = uiMode === "live" ? "Начать потоковый голосовой ввод" : "Начать обычную запись";
    voiceBtn.setAttribute("aria-label", voiceBtn.title);
  }
  cancelBtn.classList.toggle("hidden", !(state.voice.recording || state.voice.connecting));
  cancelBtn.disabled = !(state.voice.recording || state.voice.connecting);
  sendBtn.disabled = state.sending || busy;
}

function formatDuration(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

async function loadInspector() {
  if (!state.sessionId || !state.user?.is_admin) return;
  const payload = await api(`/api/sessions/${state.sessionId}/inspector`);
  const panel = el("inspectorPanel");
  if (!payload.ok) {
    panel.innerHTML = `<div class="warning-list">${escapeHtml(payload.error || "Inspector недоступен.")}</div>`;
    return;
  }
  const latest = payload.latest_turn || {};
  panel.innerHTML = `
    <h3>Context manifest</h3>
    <pre>${escapeHtml(JSON.stringify(payload.manifest, null, 2))}</pre>
    <h3>Layers</h3>
    ${(payload.layers || []).map((layer) => `
      <details class="inspector-layer">
        <summary>${layer.order}. ${escapeHtml(layer.file)} · ${escapeHtml(layer.status || "")}</summary>
        <pre>${escapeHtml(layer.text || "")}</pre>
      </details>
    `).join("")}
    <h3>Latest structured output</h3>
    <pre>${escapeHtml(JSON.stringify(latest.structured_output || null, null, 2))}</pre>
    <h3>Trace</h3>
    <pre>${escapeHtml(JSON.stringify(latest.trace || null, null, 2))}</pre>
  `;
}

function setActiveTab(name) {
  document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === name));
  el("draftTab").classList.toggle("hidden", name !== "draft");
  el("warningsTab").classList.toggle("hidden", name !== "warnings");
  el("jsonTab").classList.toggle("hidden", name !== "json");
  el("inspectorPanel").classList.toggle("hidden", name !== "inspector");
  el("usersPanel").classList.toggle("hidden", name !== "users");
}

function listBlock(title, items) {
  if (!items.length) return "";
  return `<h3>${escapeHtml(title)}</h3><ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function textFromDraft(draft) {
  return [
    draft.title || "Проект карты",
    `Статус: ${draft.project_status || "Проект, требует проверки"}`,
    `Тип: ${draft.document_type || "ТК/ТТК"}`,
    ...(draft.sections || []).map((section) => `\n${section.title}\n${section.content}`),
  ].join("\n");
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast("Скопировано.");
  } catch (_error) {
    showToast("Не удалось скопировать автоматически.");
  }
}

function formatNumber(value) {
  return new Intl.NumberFormat("ru-RU").format(Number(value || 0));
}

function formatDate(value) {
  if (!value) return "нет данных";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

el("loginForm").addEventListener("submit", login);
el("demoLoginBtn").addEventListener("click", demoLogin);
el("logoutBtn").addEventListener("click", logout);
el("newSessionBtn").addEventListener("click", async () => {
  setSystemMenu(false);
  await createSession();
});
el("newSessionRailBtn").addEventListener("click", () => createSession());
el("sessionsDrawerBtn").addEventListener("click", () => setSessionsDrawer(!state.ui.sessionsDrawerOpen));
el("sessionsScrim").addEventListener("click", () => setSessionsDrawer(false));
el("artifactTopBtn").addEventListener("click", () => setArtifactsOpen(!state.ui.artifactsOpen));
el("artifactSummary").addEventListener("click", () => setArtifactsOpen(true));
el("artifactCloseBtn").addEventListener("click", () => setArtifactsOpen(false));
el("artifactScrim").addEventListener("click", () => setArtifactsOpen(false));
el("avatarBtn").addEventListener("click", () => setSystemMenu(!state.ui.systemMenuOpen));
el("messageForm").addEventListener("submit", sendMessage);
el("voiceBtn").addEventListener("click", toggleVoiceRecording);
el("voiceCancelBtn").addEventListener("click", cancelVoiceRecording);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeOverlays();
  }
});
document.addEventListener("click", (event) => {
  if (!state.ui.systemMenuOpen || event.target.closest(".topbar-actions")) return;
  setSystemMenu(false);
});
document.querySelectorAll("[data-demo]").forEach((button) => {
  button.addEventListener("click", async () => {
    if (!state.sessionId) {
      await createSession(button.dataset.demo.slice(0, 80));
    }
    el("messageInput").value = button.dataset.demo;
    await sendMessage();
  });
});
document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", async () => {
  setActiveTab(tab.dataset.tab);
  // Sticky MVP note: user management is admin demo tooling, not a production IAM console.
  if (tab.dataset.tab === "users") {
    await loadUsers();
  }
}));

initVoiceInput();
init();
