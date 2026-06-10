const A11yModule = {
  async load() {
    const res = await fetch(`data/a11y.data.json?t=${Date.now()}`, { cache: "no-store" });
    if (!res.ok) throw new Error("a11y.data.json ausente");
    return res.json();
  },
  esc(s) {
    return PanelUtils.esc(s);
  },
  helpBlock(help) {
    if (!help) return "";
    const glossary = (help.glossary || [])
      .map((g) => `<dt>${this.esc(g.term)}</dt><dd>${this.esc(g.definition)}</dd>`)
      .join("");
    return `
      <details class="hub-module-help" open>
        <summary>O que é a11y?</summary>
        <p>${this.esc(help.summary || "")}</p>
        ${glossary ? `<dl class="hub-glossary">${glossary}</dl>` : ""}
      </details>`;
  },
  statusBadge(status, label) {
    const cls = { done: "hub-badge-ok", partial: "hub-badge-warn", pending: "hub-badge-bad", unknown: "hub-badge-muted" }[status] || "hub-badge-muted";
    return `<span class="hub-badge ${cls}">${this.esc(label || status)}</span>`;
  },
  async mount(root) {
    const data = await this.load();
    const rep = data.report || {};
    const help = data.module_help || {};
    const checklist = data.checklist || [];
    const screens = data.screens || [];
    const gaps = data.gaps || [];
    root.innerHTML = `
      ${this.helpBlock(help)}
      <div class="pm-card">
        <h2>${this.esc(help.title || "Acessibilidade (a11y)")}</h2>
        <p class="qh-card-lead">Checklist WCAG básico + status por tela mockada</p>
        <div class="hub-kpi-row">
          <div class="hub-kpi-mini"><span class="pm-kpi-label">Checklist a11y</span><strong>${rep.checklist_pct ?? 0}%</strong></div>
          <div class="hub-kpi-mini"><span class="pm-kpi-label">Telas prontas</span><strong>${rep.screens_ready ?? 0}/${rep.screens_total ?? 0}</strong></div>
          <div class="hub-kpi-mini"><span class="pm-kpi-label">Gaps</span><strong>${rep.gap_count ?? 0}</strong></div>
        </div>
      </div>
      <div class="pm-grid-2">
        <div class="pm-card">
          <h3>Checklist a11y (APPROVAL.md)</h3>
          <ul class="hub-checklist">${checklist.length ? checklist
            .map((i) => `<li class="${i.checked ? "done" : "pending"}">${i.checked ? "✓" : "○"} ${this.esc(i.label)}</li>`)
            .join("") : "<li class='pm-empty'>Seção a11y não encontrada em APPROVAL.md</li>"}</ul>
        </div>
        <div class="pm-card">
          <h3>Telas mockadas</h3>
          ${screens.length ? `<div class="hub-screen-grid">${screens
            .map(
              (s) => `<article class="hub-screen-card ${s.mocks_complete ? "" : "hub-screen-pending"}">
                <header><strong>${this.esc(s.title || s.id)}</strong> ${this.statusBadge(s.a11y_status, s.a11y_label)}</header>
                <p class="hub-cell-sub">${s.mocks_complete ? "Mock completo" : "Mock pendente"}</p>
                ${s.preview_url ? `<a class="hub-mock-link" href="${this.esc(s.preview_url)}" target="_blank" rel="noopener">Abrir mock HTML</a>` : ""}
                ${(s.linked_reqs || []).length ? `<p class="hub-cell-sub">REQs: ${s.linked_reqs.map((r) => this.esc(r)).join(", ")}</p>` : ""}
              </article>`
            )
            .join("")}</div>` : '<p class="pm-empty">Nenhuma tela em project.config.yaml → design.screens</p>'}
        </div>
      </div>
      ${gaps.length ? `<div class="pm-card"><h3>Lacunas</h3>${gaps.map((g) => `<p class="qh-tag">${this.esc(g.label)}</p>`).join("")}</div>` : ""}`;
  },
};
window.A11yModule = A11yModule;
