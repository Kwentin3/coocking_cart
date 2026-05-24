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

function showLogin(configErrors = []) {
  el("loginView").classList.remove("hidden");
  el("workspace").classList.add("hidden");
  el("roleBadge").textContent = "guest";
  el("logoutBtn").classList.add("hidden");
  el("newSessionBtn").classList.add("hidden");
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
  el("inspectorTab").classList.toggle("hidden", !state.user?.is_admin);
  el("usersTab").classList.toggle("hidden", !state.user?.is_admin);
  el("railTitle").textContent = state.user?.is_admin ? "Админка" : "Сессии";
  el("newSessionRailBtn").classList.toggle("hidden", !!state.user?.is_admin);
  if (!state.user?.is_admin && (!el("usersPanel").classList.contains("hidden") || !el("inspectorPanel").classList.contains("hidden"))) {
    setActiveTab("draft");
  }
}

async function init() {
  const me = await api("/api/me");
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
    const node = document.createElement("div");
    node.className = `message ${message.role}`;
    node.textContent = message.content;
    box.appendChild(node);
  }
  box.scrollTop = box.scrollHeight;
}

async function sendMessage(event) {
  event?.preventDefault();
  const text = el("messageInput").value.trim();
  if (!text) return;
  if (!state.sessionId) {
    await createSession(text.slice(0, 80));
  }
  if (!state.sessionId) return;
  setLoading(true);
  const payload = await api(`/api/sessions/${state.sessionId}/messages`, {
    method: "POST",
    body: JSON.stringify({message: text}),
  });
  el("messageInput").value = "";
  setLoading(false);
  if (!payload.ok) {
    showToast(payload.error || "Не удалось отправить сообщение.");
    return;
  }
  await openSession(state.sessionId);
}

function setLoading(isLoading) {
  el("sendBtn").disabled = isLoading;
  el("sendBtn").textContent = isLoading ? "…" : "➤";
}

function renderStructured(output) {
  renderDraft(output);
  renderWarnings(output);
  renderJson(output);
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
el("newSessionBtn").addEventListener("click", () => createSession());
el("newSessionRailBtn").addEventListener("click", () => createSession());
el("messageForm").addEventListener("submit", sendMessage);
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

init();
