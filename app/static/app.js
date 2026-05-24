const state = {
  user: null,
  sessions: [],
  sessionId: null,
  latestTurn: null,
};

const el = (id) => document.getElementById(id);

async function api(path, options = {}) {
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
  el("newSessionBtn").classList.remove("hidden");
  el("inspectorTab").classList.toggle("hidden", !state.user?.is_admin);
}

async function init() {
  const me = await api("/api/me");
  if (me.user) {
    state.user = me.user;
    showWorkspace();
    await loadSessions();
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
  await loadSessions();
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
  state.sessionId = null;
  state.latestTurn = null;
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
  await loadSessions();
  await openSession(payload.session_id);
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
    const item = document.createElement("div");
    item.className = `session-item ${session.id === state.sessionId ? "active" : ""}`;
    item.textContent = session.title;
    item.title = session.owner_email ? `owner: ${session.owner_email}` : "";
    item.addEventListener("click", () => openSession(session.id));
    list.appendChild(item);
  }
  if (!state.sessions.length) {
    list.innerHTML = `<div class="empty-state">Нет сессий.</div>`;
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
  await navigator.clipboard.writeText(text);
  showToast("Скопировано.");
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
document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => setActiveTab(tab.dataset.tab)));

init();
