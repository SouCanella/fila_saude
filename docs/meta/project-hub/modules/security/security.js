const SecurityModule = {
  async load() {
    const res = await fetch(`data/security.data.json?t=${Date.now()}`, { cache: "no-store" });
    if (!res.ok) throw new Error("security.data.json ausente");
    return res.json();
  },
  esc(s) {
    return PanelUtils.esc(s);
  },
  helpBlock(help) {
    if (!help) return "";
    const actions = (help.actions || [])
      .map((a) => `<li>${this.esc(a)}</li>`)
      .join("");
    return `
      <details class="hub-module-help">
        <summary>O que é este painel?</summary>
        <p>${this.esc(help.summary || "")}</p>
        ${help.sources ? `<p class="hub-help-meta"><strong>Fontes:</strong> ${help.sources.map((s) => this.esc(s)).join(" · ")}</p>` : ""}
        ${actions ? `<ul class="hub-help-list">${actions}</ul>` : ""}
      </details>`;
  },
  async mount(root) {
    const data = await this.load();
    const rep = data.report || {};
    const help = data.module_help || {};
    const checklist = data.checklist || [];
    const gaps = data.gaps || [];
    const reqs = (data.requirements || []).filter((r) => r.sensitive || r.security_required);
    root.innerHTML = `
      ${this.helpBlock(help)}
      <div class="pm-card">
        <h2>${this.esc(help.title || "Segurança do projeto")}</h2>
        <p class="qh-card-lead">Checklist por entrega + REQs sensíveis. Fonte: ${this.esc(data.checklist_path || "docs/security/")}</p>
        <div class="hub-kpi-row">
          <div class="hub-kpi-mini"><span class="pm-kpi-label">Checklist global</span><strong>${rep.checklist_pct ?? 0}%</strong></div>
          <div class="hub-kpi-mini"><span class="pm-kpi-label">REQs sensíveis</span><strong>${rep.sensitive_count ?? 0}</strong></div>
          <div class="hub-kpi-mini"><span class="pm-kpi-label">Lacunas</span><strong>${rep.gap_count ?? 0}</strong></div>
        </div>
      </div>
      <div class="pm-grid-2">
        <div class="pm-card">
          <h3>Checklist global</h3>
          <ul class="hub-checklist">${checklist.length ? checklist
            .map((i) => `<li class="${i.checked ? "done" : "pending"}">${i.checked ? "✓" : "○"} ${this.esc(i.label)}</li>`)
            .join("") : "<li class='pm-empty'>Checklist vazio — preencher docs/security/security-checklist.md</li>"}</ul>
        </div>
        <div class="pm-card">
          <h3>REQs sensíveis / security</h3>
          ${reqs.length ? `<div class="pm-table-wrap"><table class="qh-table"><thead><tr><th>REQ</th><th>Sensível</th><th>Threat model</th><th>Spec</th></tr></thead><tbody>${reqs
            .map(
              (r) => `<tr class="${r.sensitive && !r.has_threat_model ? "hub-row-warn" : ""}"><td><strong>${this.esc(r.req_id)}</strong><br><span class="hub-cell-sub">${this.esc(r.title || "")}</span></td><td>${r.sensitive ? "Sim" : "—"}</td><td>${r.has_threat_model ? "✓" : "✗"}</td><td>${this.esc(r.spec_status || "—")}</td></tr>`
            )
            .join("")}</tbody></table></div>` : '<p class="pm-empty">Nenhum REQ sensível no backlog.</p>'}
        </div>
      </div>
      <div class="pm-card">
        <h3>Riscos</h3>
        ${gaps.length ? gaps.map((g) => `<p class="qh-tag hub-gap-item">${this.esc(g.req_id || "")} ${this.esc(g.gap || g.label || "")}</p>`).join("") : '<p class="pm-empty">Nenhum gap de segurança detectado.</p>'}
      </div>`;
  },
};
window.SecurityModule = SecurityModule;
