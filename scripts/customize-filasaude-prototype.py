#!/usr/bin/env python3
"""Personaliza dados e mocks HTML do Project Hub para FilaSaúde."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RENAME_MAP = {
    "CRUD itens": "Painel de fila",
    "Checkout": "Agendamento (LGPD)",
    "SLA alertas": "Triagem e priorização",
    "SLA API": "Triagem e priorização (SLA)",
    "Relatórios export": "Relatórios e indicadores",
    "Login e sessão": "Login profissional",
    "Auth + login": "Auth + login profissional",
    "Formulário de item": "Formulário de triagem",
    "Formulário item": "Formulário de triagem",
    "Dashboard": "Painel da fila",
    "Demo API": "FilaSaúde API",
    "Project Hub Demo": "FilaSaúde",
}

SCREEN_FILES = {
    "login": "login.html",
    "fila-dashboard": "fila-dashboard.html",
    "triagem-form": "triagem-form.html",
}


def deep_rename(obj):
    if isinstance(obj, str):
        s = obj
        for old, new in RENAME_MAP.items():
            s = s.replace(old, new)
        s = s.replace("item-form.html", "triagem-form.html")
        s = s.replace("dashboard.html", "fila-dashboard.html")
        s = s.replace("demo@exemplo.com", "enfermeiro@filasaude.gov.br")
        s = s.replace("/design-references/", "../design-references/")
        return s
    if isinstance(obj, list):
        return [deep_rename(x) for x in obj]
    if isinstance(obj, dict):
        return {k: deep_rename(v) for k, v in obj.items()}
    return obj


def patch_hub_data(data_dir: Path) -> None:
    hub = json.loads((data_dir / "hub.data.json").read_text(encoding="utf-8"))
    hub["project_name"] = "FilaSaúde"
    hub = deep_rename(hub)
    hub["next_step"] = {
        "phase": "design",
        "label": "Aprovar padrão visual FilaSaúde",
        "prompt": "Revise os mocks HTML em design-references/, complete o checklist de a11y e aprove o padrão visual para iniciar o framework de UI.",
        "skill": "project-bootstrap",
        "blockers": ["design.status: in_review"],
        "hub_hash": "#design",
    }
    if hub.get("openapi", {}).get("info"):
        hub["openapi"]["info"]["title"] = "FilaSaúde API"
        hub["openapi"]["info"]["version"] = "0.2.0"
    (data_dir / "hub.data.json").write_text(
        json.dumps(hub, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for name in data_dir.glob("*.json"):
        if name.name == "hub.data.json":
            continue
        obj = json.loads(name.read_text(encoding="utf-8"))
        obj = deep_rename(obj)
        if name.name == "design.data.json":
            patch_design(obj)
        if name.name == "a11y.data.json":
            patch_a11y(obj)
        if name.name == "security.data.json":
            patch_security(obj)
        name.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_design(data: dict) -> None:
    screens = []
    for sid, title in [
        ("login", "Login profissional"),
        ("fila-dashboard", "Painel da fila"),
        ("triagem-form", "Formulário de triagem"),
    ]:
        html = f"design-references/screens/{SCREEN_FILES[sid]}"
        screens.append({
            "id": sid,
            "title": title,
            "html": html,
            "preview_url": f"../design-references/screens/{SCREEN_FILES[sid]}",
            "mocks_complete": True,
            "linked_reqs": ["REQ-001"] if sid == "login" else (["REQ-002"] if sid == "fila-dashboard" else ["REQ-003"]),
            "approval_row": {
                "screen": title,
                "file": html,
                "mocks_complete": True,
                "preview_url": f"../design-references/screens/{SCREEN_FILES[sid]}",
            },
        })
    data["screens"] = screens
    data["mock_table"] = [
        {"screen": s["title"], "file": s["html"], "mocks_complete": True, "preview_url": s["preview_url"]}
        for s in screens
    ]


def patch_a11y(data: dict) -> None:
    data["screens"] = [
        {
            "id": "login",
            "title": "Login profissional",
            "html": "design-references/screens/login.html",
            "preview_url": "../design-references/screens/login.html",
            "mocks_complete": True,
            "a11y_status": "partial",
            "a11y_label": "Parcial",
            "linked_reqs": ["REQ-001"],
        },
        {
            "id": "fila-dashboard",
            "title": "Painel da fila",
            "html": "design-references/screens/fila-dashboard.html",
            "preview_url": "../design-references/screens/fila-dashboard.html",
            "mocks_complete": True,
            "a11y_status": "partial",
            "a11y_label": "Parcial",
            "linked_reqs": ["REQ-002"],
        },
        {
            "id": "triagem-form",
            "title": "Formulário de triagem",
            "html": "design-references/screens/triagem-form.html",
            "preview_url": "../design-references/screens/triagem-form.html",
            "mocks_complete": True,
            "a11y_status": "partial",
            "a11y_label": "Parcial",
            "linked_reqs": ["REQ-003"],
        },
    ]
    data["gaps"] = [
        {"type": "checklist", "label": "Checklist a11y incompleto em APPROVAL.md"},
        {"type": "a11y", "id": "login", "label": "A11y Parcial — Login profissional"},
        {"type": "a11y", "id": "fila-dashboard", "label": "A11y Parcial — Painel da fila"},
        {"type": "a11y", "id": "triagem-form", "label": "A11y Parcial — Formulário de triagem"},
    ]


def patch_security(data: dict) -> None:
    for req in data.get("requirements", []):
        if req.get("req_id") == "REQ-004":
            req["title"] = "Agendamento e dados do paciente (LGPD)"
    for gap in data.get("gaps", []):
        if gap.get("req_id") == "REQ-004":
            gap["title"] = "Agendamento e dados do paciente (LGPD)"
            gap["gap"] = "Threat model LGPD ausente na spec"


def patch_index(html_path: Path) -> None:
    html = html_path.read_text(encoding="utf-8")
    html = html.replace("Project Hub — Modelo", "FilaSaúde — Project Hub")
    html = html.replace("Modelo · Project Hub", "FilaSaúde · Project Hub")
    html = html.replace(
        'id="hubProjectName">Visão unificada do projeto',
        'id="hubProjectName">Gestão de filas em unidades de saúde',
    )
    html_path.write_text(html, encoding="utf-8")


def write_design_assets(design_dir: Path) -> None:
    shared = design_dir / "shared"
    shared.mkdir(parents=True, exist_ok=True)
    (shared / "design-tokens.css").write_text(DESIGN_TOKENS, encoding="utf-8")
    (shared / "components.css").write_text(COMPONENTS_CSS, encoding="utf-8")
    (shared / "mock-data.js").write_text(MOCK_DATA_JS, encoding="utf-8")
    (shared / "mock-api.js").write_text(MOCK_API_JS, encoding="utf-8")
    (shared / "mock-router.js").write_text(MOCK_ROUTER_JS, encoding="utf-8")
    screens = design_dir / "screens"
    screens.mkdir(parents=True, exist_ok=True)
    (screens / "login.html").write_text(LOGIN_HTML, encoding="utf-8")
    (screens / "fila-dashboard.html").write_text(FILA_DASHBOARD_HTML, encoding="utf-8")
    (screens / "triagem-form.html").write_text(TRIAGEM_FORM_HTML, encoding="utf-8")
    (design_dir / "APPROVAL.md").write_text(APPROVAL_MD, encoding="utf-8")


DESIGN_TOKENS = """:root {
  --color-primary: #0d9488;
  --color-primary-hover: #0f766e;
  --color-primary-soft: #ccfbf1;
  --color-secondary: #64748b;
  --color-danger: #dc2626;
  --color-warning: #d97706;
  --color-success: #059669;
  --color-bg: #f0fdfa;
  --color-surface: #ffffff;
  --color-text: #134e4a;
  --color-text-muted: #5f6b6a;
  --color-border: #99f6e4;
  --font-family: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.35rem;
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --shadow-sm: 0 1px 3px rgba(13, 148, 136, 0.08);
  --shadow-md: 0 8px 24px rgba(13, 148, 136, 0.12);
}
"""

COMPONENTS_CSS = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import 'design-tokens.css';

*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--font-family);
  background: linear-gradient(160deg, var(--color-bg) 0%, #ecfeff 50%, #f8fafc 100%);
  color: var(--color-text);
  min-height: 100vh;
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}
.app-header .brand { display: flex; align-items: center; gap: var(--spacing-md); }
.app-header .brand-mark {
  width: 40px; height: 40px; border-radius: var(--radius-md);
  background: var(--color-primary); color: #fff;
  display: grid; place-items: center; font-weight: 700; font-size: var(--font-size-sm);
}
.app-title { margin: 0; font-size: var(--font-size-xl); font-weight: 700; }
.app-subtitle { margin: 0; font-size: var(--font-size-sm); color: var(--color-text-muted); }
.app-main { padding: var(--spacing-xl); max-width: 1100px; margin: 0 auto; }
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
}
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.35rem;
  padding: 0.55rem 1rem; border-radius: var(--radius-md); border: none;
  font-weight: 600; font-size: var(--font-size-sm); cursor: pointer; text-decoration: none;
  font-family: inherit; transition: background 0.15s, transform 0.1s;
}
.btn:hover { transform: translateY(-1px); }
.btn-primary { background: var(--color-primary); color: #fff; }
.btn-primary:hover { background: var(--color-primary-hover); }
.btn-secondary { background: #e2e8f0; color: var(--color-text); }
.btn-danger { background: #fee2e2; color: var(--color-danger); }
.input-group { margin-bottom: var(--spacing-md); }
.input-group label { display: block; font-weight: 600; font-size: var(--font-size-sm); margin-bottom: 0.35rem; }
.input, select, textarea {
  width: 100%; padding: 0.65rem 0.85rem; border: 1px solid var(--color-border);
  border-radius: var(--radius-md); font-size: var(--font-size-base); font-family: inherit;
}
.input:focus, select:focus, textarea:focus {
  outline: 2px solid var(--color-primary); outline-offset: 1px;
}
.input.error { border-color: var(--color-danger); }
.form-error { color: var(--color-danger); font-size: var(--font-size-sm); margin-top: 0.25rem; }
.alert { padding: var(--spacing-md); border-radius: var(--radius-md); margin-bottom: var(--spacing-md); }
.alert-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.alert-success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.alert-warning { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.hidden { display: none !important; }
.table { width: 100%; border-collapse: collapse; font-size: var(--font-size-sm); }
.table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--color-border); }
.table th { font-weight: 700; color: var(--color-text-muted); font-size: var(--font-size-xs); text-transform: uppercase; letter-spacing: 0.04em; }
.badge {
  display: inline-block; padding: 0.2rem 0.55rem; border-radius: 999px;
  font-size: var(--font-size-xs); font-weight: 700;
}
.badge-urgent { background: #fee2e2; color: #991b1b; }
.badge-priority { background: #ffedd5; color: #9a3412; }
.badge-normal { background: var(--color-primary-soft); color: #115e59; }
.badge-waiting { background: #e0f2fe; color: #075985; }
.badge-done { background: #dcfce7; color: #166534; }
.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: var(--spacing-md); margin-bottom: var(--spacing-lg); }
.kpi { background: var(--color-primary-soft); border-radius: var(--radius-md); padding: var(--spacing-md); }
.kpi strong { display: block; font-size: 1.5rem; }
.kpi span { font-size: var(--font-size-xs); color: var(--color-text-muted); text-transform: uppercase; }
.spinner {
  display: inline-block; width: 1rem; height: 1rem;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty-state { text-align: center; padding: var(--spacing-xl); color: var(--color-text-muted); }
.login-wrap { min-height: 100vh; display: grid; place-items: center; padding: var(--spacing-xl); }
.login-card { width: 100%; max-width: 420px; }
.login-hero { text-align: center; margin-bottom: var(--spacing-lg); }
.login-hero .logo {
  width: 56px; height: 56px; margin: 0 auto var(--spacing-md);
  border-radius: 14px; background: var(--color-primary); color: #fff;
  display: grid; place-items: center; font-weight: 800; font-size: 1.1rem;
}
"""

MOCK_DATA_JS = """const MockData = {
  users: [
    { id: "1", email: "enfermeiro@filasaude.gov.br", name: "Ana Silva", role: "enfermeira", unit: "UBS Centro" },
    { id: "2", email: "medico@filasaude.gov.br", name: "Dr. Carlos Mendes", role: "medico", unit: "UBS Centro" },
  ],
  queue: [
    { id: "P-1042", name: "Maria Oliveira", cpf_mask: "***.442.118-**", priority: "urgente", status: "aguardando", wait_min: 42, specialty: "Clínico geral" },
    { id: "P-1043", name: "João Pereira", cpf_mask: "***.881.229-**", priority: "prioritário", status: "em_triagem", wait_min: 18, specialty: "Pediatria" },
    { id: "P-1044", name: "Helena Costa", cpf_mask: "***.119.337-**", priority: "normal", status: "aguardando", wait_min: 8, specialty: "Enfermagem" },
    { id: "P-1045", name: "Roberto Lima", cpf_mask: "***.556.901-**", priority: "normal", status: "atendido", wait_min: 0, specialty: "Clínico geral" },
  ],
  session: { token: "mock-token-filasaude", userId: "1" },
};
"""

MOCK_API_JS = """const MockApi = {
  async login(email, password) {
    await new Promise((r) => setTimeout(r, 600));
    const user = MockData.users.find((u) => u.email === email);
    if (!user || password !== "filasaude123") {
      return { ok: false, message: "Credenciais inválidas. Use enfermeiro@filasaude.gov.br / filasaude123" };
    }
    sessionStorage.setItem("mockSession", JSON.stringify({ userId: user.id, token: MockData.session.token }));
    return { ok: true, user };
  },
  async logout() {
    sessionStorage.removeItem("mockSession");
    return { ok: true };
  },
  async getQueue() {
    await new Promise((r) => setTimeout(r, 400));
    if (sessionStorage.getItem("mockSimulateError")) throw new Error("Falha ao sincronizar fila — tente novamente");
    return [...MockData.queue];
  },
  async createTriage(data) {
    await new Promise((r) => setTimeout(r, 500));
    const id = "P-" + (1046 + MockData.queue.length);
    MockData.queue.unshift({
      id, name: data.patientName, cpf_mask: "***.***.***-**",
      priority: data.priority, status: "aguardando", wait_min: 0, specialty: data.specialty,
    });
    return { ok: true, id };
  },
};
"""

MOCK_ROUTER_JS = """const MockRouter = {
  go(path) { window.location.href = path; },
  requireAuth() {
    if (!sessionStorage.getItem("mockSession")) { this.go("login.html"); return false; }
    return true;
  },
};
"""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Entrar — FilaSaúde</title>
  <link rel="stylesheet" href="../shared/components.css" />
</head>
<body>
  <div class="login-wrap">
    <section class="card login-card">
      <div class="login-hero">
        <div class="logo" aria-hidden="true">FS</div>
        <h1 class="app-title">FilaSaúde</h1>
        <p class="app-subtitle">Acesso profissional — UBS Centro</p>
      </div>
      <div id="alert" class="alert alert-error hidden" role="alert"></div>
      <form id="loginForm" novalidate>
        <div class="input-group">
          <label for="email">E-mail institucional</label>
          <input class="input" type="email" id="email" name="email" autocomplete="username" required placeholder="nome@filasaude.gov.br" />
        </div>
        <div class="input-group">
          <label for="password">Senha</label>
          <input class="input" type="password" id="password" name="password" autocomplete="current-password" required />
        </div>
        <button type="submit" class="btn btn-primary" id="submitBtn" style="width:100%;">Entrar na unidade</button>
      </form>
      <p style="font-size:var(--font-size-sm);color:var(--color-text-muted);margin-top:var(--spacing-md);text-align:center;">
        Demo: enfermeiro@filasaude.gov.br / filasaude123
      </p>
    </section>
  </div>
  <script src="../shared/mock-data.js"></script>
  <script src="../shared/mock-api.js"></script>
  <script src="../shared/mock-router.js"></script>
  <script>
    if (sessionStorage.getItem("mockSession")) MockRouter.go("fila-dashboard.html");
    const form = document.getElementById("loginForm");
    const alertEl = document.getElementById("alert");
    const submitBtn = document.getElementById("submitBtn");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      alertEl.classList.add("hidden");
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner"></span> Autenticando…';
      const result = await MockApi.login(
        document.getElementById("email").value.trim(),
        document.getElementById("password").value
      );
      submitBtn.disabled = false;
      submitBtn.textContent = "Entrar na unidade";
      if (result.ok) MockRouter.go("fila-dashboard.html");
      else { alertEl.textContent = result.message; alertEl.classList.remove("hidden"); }
    });
  </script>
</body>
</html>
"""

FILA_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Painel da fila — FilaSaúde</title>
  <link rel="stylesheet" href="../shared/components.css" />
</head>
<body>
  <header class="app-header">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">FS</div>
      <div>
        <h1 class="app-title">Painel da fila</h1>
        <p class="app-subtitle">UBS Centro · atualização em tempo real</p>
      </div>
    </div>
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
      <button type="button" class="btn btn-secondary" id="simulateError">Simular falha</button>
      <a href="triagem-form.html" class="btn btn-primary">Nova triagem</a>
      <button type="button" class="btn btn-secondary" id="logoutBtn">Sair</button>
    </div>
  </header>
  <main class="app-main">
    <div id="alert" class="alert alert-error hidden" role="alert"></div>
    <div class="kpi-row" id="kpis">
      <div class="kpi"><strong id="kpiWaiting">—</strong><span>Aguardando</span></div>
      <div class="kpi"><strong id="kpiTriage">—</strong><span>Em triagem</span></div>
      <div class="kpi"><strong id="kpiUrgent">—</strong><span>Urgentes</span></div>
      <div class="kpi"><strong id="kpiAvg">—</strong><span>Espera média (min)</span></div>
    </div>
    <div id="loading" class="card hidden"><span class="spinner" style="border-color:rgba(13,148,136,0.3);border-top-color:var(--color-primary)"></span> Sincronizando fila…</div>
    <section class="card" id="content">
      <h2 style="margin-top:0;">Pacientes na fila</h2>
      <table class="table" id="queueTable">
        <thead>
          <tr><th>Senha</th><th>Paciente</th><th>Especialidade</th><th>Prioridade</th><th>Status</th><th>Espera</th><th></th></tr>
        </thead>
        <tbody id="queueBody"></tbody>
      </table>
      <div id="empty" class="empty-state hidden">Nenhum paciente na fila. <a href="triagem-form.html">Registrar triagem</a></div>
    </section>
  </main>
  <script src="../shared/mock-data.js"></script>
  <script src="../shared/mock-api.js"></script>
  <script src="../shared/mock-router.js"></script>
  <script>
    if (!MockRouter.requireAuth()) throw new Error("redirect");
    const priorityBadge = { urgente: "badge-urgent", prioritário: "badge-priority", normal: "badge-normal" };
    const statusBadge = { aguardando: "badge-waiting", em_triagem: "badge-priority", atendido: "badge-done" };
    const statusLabel = { aguardando: "Aguardando", em_triagem: "Em triagem", atendido: "Atendido" };
    document.getElementById("logoutBtn").addEventListener("click", async () => { await MockApi.logout(); MockRouter.go("login.html"); });
    document.getElementById("simulateError").addEventListener("click", () => { sessionStorage.setItem("mockSimulateError", "1"); loadQueue(); });
    async function loadQueue() {
      const loading = document.getElementById("loading");
      const content = document.getElementById("content");
      const alertEl = document.getElementById("alert");
      const tbody = document.getElementById("queueBody");
      alertEl.classList.add("hidden");
      loading.classList.remove("hidden");
      content.classList.add("hidden");
      try {
        const items = await MockApi.getQueue();
        sessionStorage.removeItem("mockSimulateError");
        const waiting = items.filter((i) => i.status === "aguardando");
        const triage = items.filter((i) => i.status === "em_triagem");
        const urgent = items.filter((i) => i.priority === "urgente" && i.status !== "atendido");
        const avg = waiting.length ? Math.round(waiting.reduce((a, b) => a + b.wait_min, 0) / waiting.length) : 0;
        document.getElementById("kpiWaiting").textContent = waiting.length;
        document.getElementById("kpiTriage").textContent = triage.length;
        document.getElementById("kpiUrgent").textContent = urgent.length;
        document.getElementById("kpiAvg").textContent = avg;
        tbody.innerHTML = items.map((p) => `<tr>
          <td><strong>${p.id}</strong></td>
          <td>${p.name}<br><small style="color:var(--color-text-muted)">${p.cpf_mask}</small></td>
          <td>${p.specialty}</td>
          <td><span class="badge ${priorityBadge[p.priority] || "badge-normal"}">${p.priority}</span></td>
          <td><span class="badge ${statusBadge[p.status] || "badge-waiting"}">${statusLabel[p.status] || p.status}</span></td>
          <td>${p.wait_min ? p.wait_min + " min" : "—"}</td>
          <td>${p.status !== "atendido" ? '<button type="button" class="btn btn-secondary" style="padding:0.3rem 0.6rem;font-size:0.75rem">Chamar</button>' : ""}</td>
        </tr>`).join("");
        document.getElementById("empty").classList.toggle("hidden", items.length > 0);
        document.getElementById("queueTable").classList.toggle("hidden", items.length === 0);
      } catch (err) {
        alertEl.textContent = err.message || "Erro ao carregar fila";
        alertEl.classList.remove("hidden");
        sessionStorage.removeItem("mockSimulateError");
      } finally {
        loading.classList.add("hidden");
        content.classList.remove("hidden");
      }
    }
    loadQueue();
    setInterval(loadQueue, 15000);
  </script>
</body>
</html>
"""

TRIAGEM_FORM_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Nova triagem — FilaSaúde</title>
  <link rel="stylesheet" href="../shared/components.css" />
</head>
<body>
  <header class="app-header">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">FS</div>
      <div>
        <h1 class="app-title">Nova triagem</h1>
        <p class="app-subtitle">Classificação de risco e encaminhamento</p>
      </div>
    </div>
    <a href="fila-dashboard.html" class="btn btn-secondary">Voltar ao painel</a>
  </header>
  <main class="app-main" style="max-width:560px;">
    <section class="card">
      <div id="success" class="alert alert-success hidden" role="status">Paciente incluído na fila com sucesso.</div>
      <form id="triageForm">
        <div class="input-group">
          <label for="patientName">Nome do paciente</label>
          <input class="input" type="text" id="patientName" required minlength="3" placeholder="Nome completo" />
          <p class="form-error hidden" id="nameError">Informe o nome completo (mín. 3 caracteres).</p>
        </div>
        <div class="input-group">
          <label for="specialty">Especialidade / destino</label>
          <select id="specialty" required>
            <option value="">Selecione…</option>
            <option>Clínico geral</option>
            <option>Pediatria</option>
            <option>Enfermagem</option>
            <option>Odontologia</option>
          </select>
        </div>
        <div class="input-group">
          <label for="priority">Classificação de risco</label>
          <select id="priority" required>
            <option value="normal">Normal</option>
            <option value="prioritário">Prioritário</option>
            <option value="urgente">Urgente</option>
          </select>
        </div>
        <div class="input-group">
          <label for="symptoms">Queixa principal</label>
          <textarea id="symptoms" rows="3" placeholder="Descreva sintomas e sinais observados…"></textarea>
        </div>
        <div class="alert alert-warning" role="note" style="font-size:var(--font-size-sm);">
          Dados sensíveis (LGPD): não registre informações além do necessário para triagem.
        </div>
        <button type="submit" class="btn btn-primary">Incluir na fila</button>
        <a href="fila-dashboard.html" class="btn btn-secondary" style="margin-left:0.5rem;">Cancelar</a>
      </form>
    </section>
  </main>
  <script src="../shared/mock-data.js"></script>
  <script src="../shared/mock-api.js"></script>
  <script src="../shared/mock-router.js"></script>
  <script>
    if (!MockRouter.requireAuth()) throw new Error("redirect");
    document.getElementById("triageForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("patientName").value.trim();
      const nameError = document.getElementById("nameError");
      if (name.length < 3) {
        nameError.classList.remove("hidden");
        document.getElementById("patientName").classList.add("error");
        return;
      }
      nameError.classList.add("hidden");
      document.getElementById("patientName").classList.remove("error");
      await MockApi.createTriage({
        patientName: name,
        specialty: document.getElementById("specialty").value,
        priority: document.getElementById("priority").value,
        symptoms: document.getElementById("symptoms").value,
      });
      document.getElementById("success").classList.remove("hidden");
      setTimeout(() => MockRouter.go("fila-dashboard.html"), 900);
    });
  </script>
</body>
</html>
"""

APPROVAL_MD = """# Aprovação visual — FilaSaúde

**Status:** in_review

## Telas

| Tela | Arquivo | Mocks | A11y |
|------|---------|-------|------|
| Login profissional | screens/login.html | ✓ | Parcial |
| Painel da fila | screens/fila-dashboard.html | ✓ | Parcial |
| Formulário de triagem | screens/triagem-form.html | ✓ | Parcial |

## Checklist geral

- [x] Botões e links funcionam
- [x] Formulários validam e simulam submit
- [ ] Loading / erro / vazio testáveis em todos os fluxos
- [x] Navegação entre telas sem 404
- [ ] Sem botões mortos

## Acessibilidade

- [x] Contraste WCAG AA alvo
- [x] Foco visível em interativos
- [x] Labels em inputs
- [ ] `lang` validado em todas as telas
- [ ] Navegação por teclado nos fluxos críticos
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub-data", type=Path, required=True)
    ap.add_argument("--design-dir", type=Path, required=True)
    ap.add_argument("--hub-html", type=Path, required=True)
    args = ap.parse_args()
    write_design_assets(args.design_dir)
    patch_hub_data(args.hub_data)
    patch_index(args.hub_html)
    print(f"OK: FilaSaúde prototype em {args.hub_data.parent.parent}")


if __name__ == "__main__":
    main()
