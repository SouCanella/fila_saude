const DesignModule = {
  async load() {
    const res = await fetch(`data/design.data.json?t=${Date.now()}`, { cache: "no-store" });
    if (!res.ok) throw new Error("design.data.json ausente");
    return res.json();
  },
  esc(s) {
    return PanelUtils.esc(s);
  },
  helpBlock(help) {
    if (!help) return "";
    return `
      <details class="hub-module-help">
        <summary>Design = mocks HTML</summary>
        <p>${this.esc(help.summary || "")}</p>
        ${help.gate ? `<p class="hub-help-meta">${this.esc(help.gate)}</p>` : ""}
      </details>`;
  },
  statusClass(status) {
    if (status === "approved") return "hub-badge-ok";
    if (status === "in_review") return "hub-badge-warn";
    return "hub-badge-muted";
  },
  async mount(root) {
    const data = await this.load();
    const rep = data.report || {};
    const help = data.module_help || {};
    const general = data.general_checklist || [];
    const screens = data.screens || [];
    const gaps = data.gaps || [];
    const status = data.design_status || "draft";
    root.innerHTML = `
      ${this.helpBlock(help)}
      <div class="pm-card">
        <h2>${this.esc(help.title || "Design readiness")}</h2>
        <p class="qh-card-lead">Mocks HTML em design-references/ antes do framework de UI</p>
        <div class="hub-kpi-row">
          <div class="hub-kpi-mini"><span class="pm-kpi-label">Status</span><strong><span class="hub-badge ${this.statusClass(status)}">${this.esc(status)}</span></strong></div>
          <div class="hub-kpi-mini"><span class="pm-kpi-label">Pronto p/ UI</span><strong>${rep.ready_for_ui_impl ? "Sim" : "Não"}</strong></div>
          <div class="hub-kpi-mini"><span class="pm-kpi-label">Telas</span><strong>${rep.screens_with_mock ?? 0}/${rep.screens_count ?? 0}</strong></div>
        </div>
      </div>
      <div class="pm-grid-2">
        <div class="pm-card">
          <h3>Checklist geral (APPROVAL)</h3>
          <ul class="hub-checklist">${general.length ? general
            .map((i) => `<li class="${i.checked ? "done" : "pending"}">${i.checked ? "✓" : "○"} ${this.esc(i.label)}</li>`)
            .join("") : "<li class='pm-empty'>Checklist geral ausente</li>"}</ul>
        </div>
        <div class="pm-card">
          <h3>Telas do MVP</h3>
          ${screens.length ? `<div class="hub-screen-grid">${screens
            .map(
              (s) => `<article class="hub-screen-card ${s.mocks_complete ? "" : "hub-screen-pending"}">
                <header><strong>${this.esc(s.title || s.id)}</strong></header>
                <p class="hub-cell-sub">${this.esc(s.html || "—")}</p>
                <p>${s.mocks_complete ? "✓ mocks_complete" : "○ mock pendente"}</p>
                ${s.preview_url ? `<a class="hub-mock-link" href="${this.esc(s.preview_url)}" target="_blank" rel="noopener">Abrir mock HTML</a>` : ""}
                ${(s.linked_reqs || []).length ? `<p class="hub-cell-sub">REQs: ${s.linked_reqs.map((r) => this.esc(r)).join(", ")}</p>` : ""}
              </article>`
            )
            .join("")}</div>` : '<p class="pm-empty">Configure design.screens no project.config.yaml</p>'}
        </div>
      </div>
      <div class="pm-card">
        <h3>Lacunas</h3>
        ${gaps.length ? gaps.map((g) => `<p class="qh-tag">${this.esc(g.label)}</p>`).join("") : '<p class="pm-empty">Nenhuma lacuna de design.</p>'}
      </div>`;
  },
};
window.DesignModule = DesignModule;
