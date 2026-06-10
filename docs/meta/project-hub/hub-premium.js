/**
 * Project Hub Premium — shell SPA + Overview/Sec/A11y/Design + legado Process/Quality
 */
const ProjectHubPremium = {
  page: "overview",
  processBooted: false,
  qualityBooted: false,

  MODULE_META: {
    overview: { label: "Overview", icon: "✦", meta: "Visão executiva do método" },
    process: { label: "Processo", icon: "⏱", meta: "Tempo, rounds e previsão" },
    quality: { label: "Qualidade", icon: "🧪", meta: "Cobertura, TDD e gaps" },
    security: { label: "Segurança", icon: "🛡", meta: "Checklist, LGPD e risco" },
    a11y: { label: "A11y", icon: "♿", meta: "WCAG e status das telas" },
    design: { label: "Design", icon: "🎨", meta: "Prontidão visual e mocks" },
  },

  d() {
    const c = HubData.cache || {};
    return {
      hub: c["hub.data.json"] || {},
      processData: c["process.data.json"] || {},
      quality: c["quality.data.json"] || {},
      security: c["security.data.json"] || {},
      a11y: c["a11y.data.json"] || {},
      design: c["design.data.json"] || {},
      journey: c["journey.data.json"] || {},
      learning: c["learning.data.json"] || {},
      openapi: c["openapi.data.json"] || {},
      delivery: c["delivery.data.json"] || {},
      techDebt: c["tech_debt.data.json"] || {},
      release: c["release.data.json"] || {},
    };
  },

  $(s, root) { return (root || document).querySelector(s); },
  $$(s, root) { return Array.from((root || document).querySelectorAll(s)); },

  esc(v) {
    return String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  },
  fmtDate(value) {
    if (!value) return '—';
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium', timeStyle: undefined }).format(d);
  },
  fmtDateTime(value) {
    if (!value) return '—';
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(d);
  },
  fmtPct(n) {
    return `${Math.round(Number(n || 0))}%`;
  },
  fmtHours(seconds) {
    const h = (Number(seconds || 0) / 3600);
    return `${h.toFixed(h >= 10 ? 0 : 1)}h`;
  },
  slug(page) { return `#${page}`; },

  phaseShortLabel(phaseId) {
    const id = String(phaseId || "");
    const phases = this.d().journey?.lifecycle?.phases || [];
    const match = phases.find((p) => p.id === id);
    if (match?.label) {
      const short = match.label.replace(/^Fase \d+ — /i, "").trim();
      if (id === "design") return "Design";
      return short.slice(0, 18);
    }
    const map = {
      discovery: "Descoberta",
      bootstrap: "Bootstrap",
      design: "Design",
      mvp_planning: "MVP",
    };
    if (map[id]) return map[id];
    if (id.startsWith("FASE-")) return id;
    return id || "—";
  },

  badgeCls(status) {
    const s = String(status || '').toLowerCase();
    if (['concluída','done','pass','approved','complete','ok','sim','valid','green','completed'].includes(s)) return 'ok';
    if (['bloqueada','fail','failed','bad','critical'].includes(s)) return 'bad';
    if (['partial','parcial','in_review','em andamento','forecast','pending','warn','warning','não'].includes(s)) return 'warn';
    return 'neutral';
  },
  statusPill(label) {
    return `<span class="pill ${this.badgeCls(label)}">${this.esc(label || '—')}</span>`;
  },
  progress(value, extra='') {
    const v = Math.max(0, Math.min(100, Number(value || 0)));
    return `<div class="progress ${extra}"><span style="width:${v}%"></span></div>`;
  },
  copyText(text) {
    navigator.clipboard.writeText(text).then(()=>this.showToast('Prompt copiado.')).catch(()=>this.showToast('Não foi possível copiar.'));
  },
  showToast(msg) {
    const toast = this.$('#copyToast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(()=> toast.classList.remove('show'), 1800);
  },
  syncThemeUI(theme) {
    const btn = this.$("#themeToggle");
    if (btn) btn.textContent = theme === "dark" ? "Modo claro" : "Modo escuro";
  },
  refreshProcessThemeViews() {
    const pm = window.ProcessMetrics;
    if (!pm) return;
    pm.renderDeliveryHighlight?.();
    pm.renderOverview?.();
    pm.renderGantt?.();
    pm.renderCalendar?.();
    const ph = document.getElementById("phaseSelect")?.value;
    if (ph) pm.renderPhaseView?.(ph);
  },
  themeToggle() {
    const current = window.ModeloTheme?.read?.() || "light";
    const next = current === "dark" ? "light" : "dark";
    if (window.ModeloTheme?.persist) window.ModeloTheme.persist(next);
    else document.documentElement.setAttribute("data-theme", next);
    this.syncThemeUI(next);
    if (this.page === "process") this.refreshProcessThemeViews();
  },
  applyTheme() {
    const theme = window.ModeloTheme?.read?.() || "light";
    if (window.ModeloTheme?.apply) window.ModeloTheme.apply(theme);
    else document.documentElement.setAttribute("data-theme", theme);
    this.syncThemeUI(theme);
  },
  bindThemeToggle() {
    const btn = this.$("#themeToggle");
    if (!btn) return;
    btn.onclick = () => this.themeToggle();
    this.applyTheme();
  },
  phaseHeaderLabel(phaseId) {
    const label = this.phaseShortLabel(phaseId);
    return label.length > 16 ? `${label.slice(0, 15)}…` : label;
  },

  parseHash(raw) {
    const h = String(raw ?? location.hash ?? "#overview").replace(/^#/, "") || "overview";
    const slash = h.indexOf("/");
    if (slash === -1) return { page: h, sub: null };
    return { page: h.slice(0, slash) || "overview", sub: h.slice(slash + 1) || null };
  },

  routeKey(page, sub) {
    return sub ? `${page}/${sub}` : page;
  },

  activateQualityTab(tab) {
    document.querySelector(`#contentRoot [data-tab="${tab}"]`)?.click();
  },

  registeredEffortLabel() {
    const p = this.d().processData?.aggregates?.project || {};
    const totalSec =
      Number(p.human_active_seconds || 0) +
      Number(p.ai_execution_seconds || 0) +
      Number(p.idle_seconds || 0);
    const h = totalSec / 3600;
    const value = totalSec ? `${h.toFixed(h >= 10 ? 0 : 1)} h` : "0 h";
    const tip = `Humano ${this.fmtHours(p.human_active_seconds)} · IA ${this.fmtHours(p.ai_execution_seconds)} · ocioso ${this.fmtHours(p.idle_seconds)}`;
    return { value, tip };
  },

  buildSidebarKpis() {
    const el = this.$("#sidebarKpis");
    if (!el) return;
    const k = this.d().hub?.kpis || {};
    const effort = this.registeredEffortLabel();
    const q = Number(k.quality_gaps || 0);
    const s = Number(k.security_gaps || 0);
    const items = [
      ["Fases concluídas", `${k.phases_complete ?? 0}/${k.phases_total ?? 0}`, "Discovery até operação do MVP"],
      ["REQs green", `${Math.round(k.req_fully_green_pct ?? 0)}%`, "Cobertura TDD saudável"],
      ["Atividade recente", String(k.activity_count ?? 0), "Eventos no histórico"],
      ["Tech-debt crítica", String(k.tech_debt_critical ?? 0), "Itens em tech-debt.md"],
      ["OpenAPI", k.openapi_valid ? "OK" : k.openapi_path_count === 0 ? "stub" : "pendente", `${k.openapi_path_count ?? 0} path(s)`],
      ["Compliance", k.compliance_ok ? "OK" : "—", "LGPD e checklists"],
      ["Gaps observáveis", String(q + s), `Qualidade ${q} · Segurança ${s}`],
      ["Esforço registrado", effort.value, effort.tip],
    ];
    el.innerHTML = `
      <p class="sidebar-kpi-heading">Indicadores</p>
      <div class="sidebar-kpi-stack">
        ${items
          .map(
            ([label, value, tip]) => `
          <div class="sidebar-kpi-item" title="${this.esc(tip)}">
            <span class="sidebar-kpi-label">${this.esc(label)}</span>
            <strong class="sidebar-kpi-value">${this.esc(value)}</strong>
          </div>`
          )
          .join("")}
      </div>`;
  },

  buildSidebar() {
    const nav = this.$("#navList");
    if (!nav) return;

    nav.innerHTML = Object.entries(this.MODULE_META).map(([key, meta]) => `
      <a class="nav-link ${this.page===key?'active':''}" href="#${key}" data-nav="${key}" title="${this.esc(meta.meta)}">
        <span class="nav-icon">${meta.icon}</span>
        <span class="nav-copy">
          <div class="nav-title">${meta.label}</div>
        </span>
      </a>
    `).join("");

    nav.querySelectorAll(".nav-link").forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        location.hash = `#${a.getAttribute("data-nav") || "overview"}`;
      });
    });
    this.buildSidebarKpis();
  },

  buildTopbar() {
    const meta = this.page === "guide"
      ? { label: "Guia", meta: "Documentação · docs/meta/project-hub.md" }
      : this.MODULE_META[this.page] || this.MODULE_META.overview;
    const hub = this.d().hub || {};
    const kpis = hub.kpis || {};
    const currentPhase = kpis.current_phase_id || 'design';
    const totalGaps = Number(kpis.quality_gaps || 0) + Number(kpis.security_gaps || 0);
    const health = Number(kpis.health_score || 0);
    const projectName = hub.project_name || 'Project Hub';

    this.$('#pageTitle').textContent = meta.label;
    this.$('#pageSubtitle').textContent = meta.meta;
    this.$('#builtAt').textContent = `Última consolidação: ${this.fmtDateTime(hub.built_at || this.d().processData?.built_at)}`;

    const nameEl = this.$('#topProjectName');
    if (nameEl) {
      nameEl.textContent = projectName;
      nameEl.title = projectName;
    }
    const phaseEl = this.$('#topPhase');
    if (phaseEl) {
      const phaseLabel = this.phaseHeaderLabel(currentPhase);
      phaseEl.textContent = phaseLabel;
      const pill = phaseEl.closest(".hub-stat-pill--current");
      if (pill) pill.title = `Fase atual: ${this.phaseShortLabel(currentPhase)} (journey.data.json → lifecycle.current_phase_id)`;
    }
    const cardsEl = this.$('#topCards');
    if (cardsEl) cardsEl.textContent = `${kpis.delivery_completed ?? 0}/${kpis.delivery_total ?? 0}`;
    const qualityGaps = Number(kpis.quality_gaps || 0);
    const securityGaps = Number(kpis.security_gaps || 0);
    const gapsEl = this.$('#topGaps');
    if (gapsEl) gapsEl.textContent = String(totalGaps);
    const gapsLink = this.$('#topGapsLink');
    if (gapsLink) {
      const tip = totalGaps
        ? `${qualityGaps} qualidade (REQs sem cobertura TDD) · ${securityGaps} segurança (threat model / checklist). Clique para ver gaps de qualidade; módulo Segurança para gaps de segurança.`
        : "Nenhum gap registrado (quality.data.json + security.data.json)";
      gapsLink.title = tip;
      if (totalGaps > 0) {
        gapsLink.href = qualityGaps > 0 ? "#quality/gaps" : "#security";
        gapsLink.classList.remove("hub-stat-pill--disabled");
        gapsLink.removeAttribute("aria-disabled");
      } else {
        gapsLink.href = "#quality";
        gapsLink.classList.add("hub-stat-pill--disabled");
        gapsLink.setAttribute("aria-disabled", "true");
      }
    }
    const ring = this.$('#topHealthRing');
    if (ring) {
      ring.style.setProperty('--p', health);
      ring.setAttribute('data-label', `${health}`);
      ring.title = `Health score: ${health}`;
    }

    const next = hub.next_step || {};
    const nextBtn = this.$('#nextModuleBtn');
    if (nextBtn) {
      if (next.hub_hash) {
        const page = String(next.hub_hash).replace('#', '') || 'design';
        nextBtn.href = this.slug(page);
        nextBtn.textContent = `Ir para ${page}`;
      } else {
        nextBtn.href = '#overview';
        nextBtn.textContent = 'Próximo passo';
      }
    }
  },

  heroSection() {
    const next = this.d().hub?.next_step || {};
    const blockers = next.blockers || [];
    return `
      <section class="hero">
        <div class="hero-main glass">
          <span class="eyebrow">Project Hub · visão premium</span>
          <h2 class="hero-title">${this.esc(this.d().hub.project_name || 'Projeto')} — monitoria unificada do método Modelo.</h2>
          <p class="hero-text">Painel executivo que consolida processo, qualidade, segurança, acessibilidade e design a partir dos artefatos do repositório. Atualize com <code>make hub-build</code> ou o botão Atualizar.</p>
          <div class="hero-chips">
            <div class="chip">Projeto <small>${this.esc(this.d().hub?.project_name || '—')}</small></div>
            <div class="chip">Fase atual <small>${this.esc(this.phaseShortLabel(next.phase || this.d().hub?.kpis?.current_phase_id))}</small></div>
            <div class="chip">OpenAPI <small>${this.d().openapi?.report?.valid ? 'válido' : 'pendente'}</small></div>
            <div class="chip">Cobertura back <small>${this.d().quality?.coverage?.backend?.lines ?? 0}%</small></div>
          </div>
          <div class="prompt-card">
            <div class="prompt-card-header">
              <h3>Próximo passo recomendado</h3>
              <button class="btn btn-soft" data-copy-prompt>Copiar prompt</button>
            </div>
            <p class="prompt-text">${this.esc(next.prompt || 'Sem prompt recomendado no momento.')}</p>
            <div class="hero-actions">
              <a class="btn btn-primary" href="${this.slug(String(next.hub_hash||'#design').replace('#','') || 'design')}">Abrir módulo sugerido</a>
              <button class="btn" data-copy-prompt>Copiar briefing do próximo passo</button>
            </div>
            ${blockers.length ? `<div class="notice bad" style="margin-top:14px;"><strong>Blockers:</strong> ${blockers.map((b) => this.esc(b)).join(' · ')}</div>` : ''}
          </div>
        </div>
      </section>
    `;
  },

  overviewGapsCard(k) {
    const q = Number(k.quality_gaps || 0);
    const s = Number(k.security_gaps || 0);
    const total = q + s;
    const href = q > 0 ? "#quality/gaps" : s > 0 ? "#security" : "#quality";
    const note = `Qualidade: ${q} · Segurança: ${s}`;
    const disabled = total === 0 ? " kpi-card-link--disabled" : "";
    return `<a class="kpi-card kpi-card-compact glass kpi-card-link${disabled}" href="${href}" title="${this.esc(note)} — clique para ver detalhes">
      <div class="kpi-card-head">
        <span class="kpi-icon">🔍</span>
        <span class="kpi-label">Gaps observáveis</span>
      </div>
      <span class="kpi-value">${total}</span>
      <div class="kpi-note">${this.esc(note)}</div>
    </a>`;
  },

  overviewKPIs() {
    const k = this.d().hub?.kpis || {};
    const items = [
      ['🧩','Fases concluídas', `${k.phases_complete ?? 0}/${k.phases_total ?? 0}`, 'Do discovery até a operação do MVP.'],
      ['✅','REQs green', `${Math.round(k.req_fully_green_pct ?? 0)}%`, 'REQUISITOS com cobertura saudável.'],
      ['📝','Atividade recente', k.activity_count ?? 0, 'Eventos no histórico.'],
      ['⚠','Tech-debt crítica', k.tech_debt_critical ?? 0, 'Itens em tech-debt.md.'],
      ['📜','OpenAPI', k.openapi_valid ? 'OK' : (k.openapi_path_count === 0 ? 'stub' : 'pendente'), `${k.openapi_path_count ?? 0} path(s)`],
      ['🛡','Compliance', k.compliance_ok ? 'OK' : '—', 'LGPD e checklists'],
    ];
    const cards = items.map(([icon, label, value, note]) => `
      <article class="kpi-card kpi-card-compact glass">
        <div class="kpi-card-head">
          <span class="kpi-icon">${icon}</span>
          <span class="kpi-label">${label}</span>
        </div>
        <span class="kpi-value">${this.esc(value)}</span>
        <div class="kpi-note">${this.esc(note)}</div>
      </article>
    `).join("");
    return `<section class="grid-kpis grid-kpis-overview">${cards}${this.overviewGapsCard(k)}</section>`;
  },

  phaseStatusBadge(status) {
    const map = { complete: "ok", in_progress: "warn", pending: "neutral", skipped: "neutral" };
    return map[status] || "neutral";
  },

  phaseFunnelLabel(p) {
    const id = String(p.id || "");
    const full = p.label || id;
    if (id.startsWith("FASE-")) {
      const tail = full.replace(/^FASE-\d+\s*—\s*/i, "").trim();
      return tail ? `${id}` : id;
    }
    const map = {
      discovery: "Descoberta",
      bootstrap: "Bootstrap",
      design: "Design",
      mvp_planning: "Planej. MVP",
    };
    return map[id] || full.replace(/^Fase \d+ — /i, "").trim().slice(0, 18);
  },

  phaseFunnelSection(journey) {
    const phases = journey?.lifecycle?.phases || [];
    const discovery = journey?.discovery || {};
    const emptyHints = journey?.report?.empty_hints || {};
    if (!phases.length) {
      return `<section class="section glass"><h2>Funil de fases</h2><p class="muted">Rode make hub-build após preencher project.config.yaml.</p></section>`;
    }
    const steps = phases.map((p, i) => {
      const sub = p.cards ? `${p.cards.done}/${p.cards.total} cards` : p.sections_total != null ? `${p.sections_done ?? 0}/${p.sections_total} blocos` : `${p.progress_pct ?? 0}%`;
      let discoverySub = "";
      if (p.id === "discovery" && (discovery.items || []).length) {
        const items = discovery.items.map((it) => `<li class="${it.ok ? "hub-check-ok" : "hub-check-pending"}">${this.esc(it.label)}</li>`).join("");
        discoverySub = `<details class="hub-discovery-fold"><summary>Checklist discovery (${discovery.items.length})</summary><ul class="hub-discovery-checklist">${items}</ul></details>`;
      }
      const clickable = String(p.id || "").startsWith("FASE-") ? ' data-phase-clickable="true"' : "";
      const blocker = (p.blockers || [])[0] || "";
      const tip = [p.label || p.id, sub, blocker].filter(Boolean).join(" · ");
      const active = p.status === "in_progress";
      const atualBadge = active ? `<span class="hub-phase-atual">atual</span>` : "";
      return `<article class="phase-card hub-phase-step-premium hub-phase-step-compact ${active ? "hub-phase-active" : ""}" data-phase-id="${this.esc(p.id)}"${clickable} role="button" tabindex="0" title="${this.esc(tip)}">
        <div class="phase-card-top">
          <span class="phase-step">${i + 1}</span>
          ${atualBadge}
          <span class="phase-badge status-${this.esc(p.status)}">${this.esc(p.status)}</span>
        </div>
        <h3>${this.esc(this.phaseFunnelLabel(p))}</h3>
        <p class="phase-sub">${this.esc(sub)}</p>
        ${discoverySub}
      </article>`;
    }).join("");
    const hintLines = Object.entries(emptyHints).map(([mod, msg]) => `<p class="hub-empty-hint"><strong>${this.esc(mod)}:</strong> ${this.esc(msg)}</p>`).join("");
    const mvpHint = !phases.some((p) => String(p.id || "").startsWith("FASE-"))
      ? `<p class="muted hub-funnel-mvp-hint">Fases de entrega (FASE-1, FASE-2…) aparecem após preencher <code>docs/planning/mvp-phases.md</code> e cards no backlog.</p>`
      : "";
    return `<section class="section glass">
      <div class="section-header"><div class="section-title"><h2>Funil de fases <span class="muted">${journey.lifecycle?.phases_complete ?? 0}/${journey.lifecycle?.phases_total ?? phases.length} concluídas</span></h2><p>Clique em uma fase FASE-* para filtrar entregas. Cards usam largura flexível conforme a quantidade de etapas.</p></div></div>
      <div class="phase-track hub-phase-track-premium" style="--phase-count:${phases.length}">${steps}</div>
      ${mvpHint}
      ${hintLines ? `<div class="hub-funnel-hints">${hintLines}</div>` : ""}
      <p class="muted hub-phase-filter-hint" id="hubPhaseFilterHint" hidden></p>
    </section>`;
  },

  moduleSummaries() {
    const items = [
      ['process','Processo', `Esforço humano ${this.fmtHours(this.d().processData?.aggregates?.project?.human_active_seconds)} · IA ${this.fmtHours(this.d().processData?.aggregates?.project?.ai_execution_seconds)}`, `Forecast ${this.d().processData?.forecasts?.cards?.length || 0} cards futuros`],
      ['quality','Qualidade', `Back ${this.d().quality?.coverage?.backend?.lines ?? 0}% · Front ${this.d().quality?.coverage?.frontend?.lines ?? 0}%`, `${this.d().quality?.gaps?.length || 0} gaps ativos`],
      ['security','Segurança', `${this.d().security?.report?.checklist_pct ?? 0}% checklist`, `${this.d().security?.gaps?.length || 0} gaps sensíveis`],
      ['a11y','A11y', `${(this.d().a11y?.screens||[]).length} telas monitoradas`, `${this.d().a11y?.gaps?.length || 0} apontamentos`],
      ['design','Design', `${(this.d().design?.screens||[]).length} mocks presentes`, `Status ${this.d().design?.design_status || '—'}`],
      ['overview','Aprendizados', `${this.d().learning?.report?.retro_pending ?? 0} retrospectiva pendente`, `${this.d().learning?.benchmarks?.snapshot_count ?? 0} benchmark`],
    ];
    return `
      <section class="section glass">
        <div class="section-header">
          <div class="section-title">
            <h2>Resumo dos módulos</h2>
            <p>Um frame de negócio para cada área. Bom para demo, comitê e aquela call em que todo mundo quer entender sem abrir dez arquivos.</p>
          </div>
        </div>
        <div class="cards-grid">
          ${items.map(([page,title,l1,l2])=>`
            <article class="page-card" style="padding:18px;border-radius:18px;">
              <div class="pill info">${this.esc(title)}</div>
              <h3 style="margin:14px 0 8px;">${this.esc(title)}</h3>
              <p class="muted" style="margin:0 0 6px;">${this.esc(l1)}</p>
              <p class="muted" style="margin:0 0 14px;">${this.esc(l2)}</p>
              <a class="btn" href="${this.slug(page==='overview'?'index':page)}">Abrir módulo</a>
            </article>
          `).join('')}
        </div>
      </section>
    `;
  },

  deliveriesJourneySection(journey) {
    const items = journey?.deliveries || [];
    if (!items.length) {
      return `<section class="section glass" id="hubDeliveries"><h2>Entregas por card</h2><p class="muted">Nenhum CARD registrado — abra cards e atualize docs/delivery-log.md.</p></section>`;
    }
    const rows = items.map((d) => {
      const reqs = (d.req_details || []).map((r) => `${r.req_id}${r.quality_gaps ? ` (${r.quality_gaps} gap)` : ""}`).join(", ");
      return `<tr class="hub-delivery-row" data-phase="${this.esc(d.phase || "")}">
        <td><strong>${this.esc(d.card_id)}</strong><div class="muted">${this.esc(d.title || "")}</div>${this.expandDeliveryRow(d)}</td>
        <td>${this.esc(d.phase || "—")}</td>
        <td>${this.statusPill(d.status || d.card_status)}</td>
        <td>${this.esc(reqs || (d.req_ids || []).join(", ") || "—")}</td>
        <td>${this.statusPill(d.tdd_red_green || "—")}</td>
        <td><div>${this.esc(this.fmtDate(d.started_at))}</div><div class="muted">até ${this.esc(this.fmtDate(d.ended_at))}</div></td>
      </tr>`;
    }).join("");
    return `<section class="section glass" id="hubDeliveries">
      <div class="section-header"><div class="section-title"><h2>Entregas por card <span class="muted">${items.length} registro(s)</span></h2></div></div>
      <div class="table-wrap"><table class="table"><thead><tr><th>Card</th><th>Fase</th><th>Status</th><th>REQs</th><th>TDD</th><th>Período</th></tr></thead><tbody>${rows}</tbody></table></div>
    </section>`;
  },

  activityAndAlerts() {
    const activities = (this.d().journey?.activity || []).slice(0, 8);
    const alerts = [];
    if (this.d().design?.design_status !== 'approved') alerts.push(`Design ainda em ${this.d().design?.design_status || 'revisão'}.`);
    if ((this.d().quality?.gaps || []).length) alerts.push(`${this.d().quality.gaps.length} gap(s) de qualidade precisam de ação.`);
    if ((this.d().security?.gaps || []).length) alerts.push(`${this.d().security.gaps.length} gap(s) de segurança exigem tratamento.`);
    if (this.d().learning?.report?.retro_pending) alerts.push(`${this.d().learning.report.retro_pending} retrospectiva(s) ainda pendente(s).`);
    return `
      <section class="subgrid-2 subgrid-2-balanced">
        <div class="section glass hub-panel-fill">
          <div class="section-header">
            <div class="section-title">
              <h2>Atividade recente</h2>
              <p>Eventos do timeline, delivery log e artefatos relevantes do repositório.</p>
            </div>
          </div>
          <div class="timeline">
            ${activities.length ? activities.map(a=>`
              <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                  <strong>${this.esc(a.summary || a.kind)}</strong>
                  <div class="meta">${this.esc(a.phase || '—')} · ${this.esc(this.fmtDateTime(a.at))}</div>
                  <div class="muted" style="margin-top:6px;">${this.esc(a.path || a.source || '')}</div>
                </div>
              </div>`).join('') : '<div class="empty">Nenhuma atividade registrada ainda. O feed aparece após a primeira rodada de métricas, entrega ou card em andamento.</div>'}
          </div>
        </div>
        <div class="section glass hub-panel-fill">
          <div class="section-header">
            <div class="section-title">
              <h2>Radar executivo</h2>
              <p>Alertas, benchmarking e leitura rápida para steering.</p>
            </div>
          </div>
          <div class="alert-list">
            ${alerts.map(msg=>`<div class="alert-item"><strong>⚠ Atenção</strong><div class="muted" style="margin-top:6px;">${this.esc(msg)}</div></div>`).join('') || '<div class="notice good">Nenhum alerta crítico aberto.</div>'}
            <div class="alert-item">
              <strong>Benchmarks observados</strong>
              <div class="muted" style="margin-top:6px;">Snapshots: ${this.d().learning?.benchmarks?.snapshot_count ?? 0} · mediana relação calendário/esforço: ${this.d().learning?.benchmarks?.medians?.calendar_ratio ?? '—'}.</div>
            </div>
            <div class="alert-item">
              <strong>OpenAPI</strong>
              <div class="muted" style="margin-top:6px;">${this.d().openapi?.info?.title || 'API'} v${this.d().openapi?.info?.version || '—'} · ${this.d().openapi?.report?.valid ? 'contrato válido' : 'revisão pendente'}.</div>
            </div>
          </div>
        </div>
      </section>
    `;
  },

  moduleSummaryCard(page, title, lines) {
    const body = lines.map((l) => `<li>${this.esc(l)}</li>`).join("");
    return `<article class="page-card" style="padding:18px;border-radius:18px;">
      <div class="pill info">${this.esc(title)}</div>
      <ul class="muted" style="margin:12px 0;">${body}</ul>
      <a class="btn" href="${this.slug(page)}">Abrir módulo</a>
    </article>`;
  },

  complianceSection(sec) {
    const comp = sec?.compliance;
    if (!comp) return "";
    const lgpd = comp.lgpd || {};
    const ct = comp.change_types || [];
    const ctLines = ct.slice(0, 4).map((s) => `<li>${this.esc(s.section)}: ${s.checked}/${s.total}</li>`).join("");
    const hint = comp.ok ? "" : `<p class="muted">Preencha bootstrap I_seguranca e N_privacidade + docs/security/*</p>`;
    return `<article class="page-card hub-compliance-card" style="padding:18px;border-radius:18px;">
      <h3>Compliance</h3>
      <ul class="muted"><li>LGPD preenchida: ${lgpd.filled ? "Sim" : "Não"}</li>${ctLines || "<li>Checklists por tipo de mudança pendentes</li>"}</ul>
      ${hint}
      <a class="btn" href="#security">Ver Security</a>
    </article>`;
  },

  renderOverview() {
    const sec = this.d().security;
    const a11y = this.d().a11y;
    const des = this.d().design;
    const secRep = sec?.report || {};
    const a11yRep = a11y?.report || {};
    const desRep = des?.report || {};
    const summaries = [
      sec ? this.moduleSummaryCard("security", "Segurança", [`Checklist: ${secRep.checklist_pct ?? 0}%`, `REQs sensíveis: ${secRep.sensitive_count ?? 0}`, `Lacunas: ${secRep.gap_count ?? 0}`]) : "",
      a11y ? this.moduleSummaryCard("a11y", "Acessibilidade", [`Checklist WCAG: ${a11yRep.checklist_pct ?? 0}%`, `Telas: ${a11yRep.screens_ready ?? 0}/${a11yRep.screens_total ?? 0}`, `Gaps: ${a11yRep.gap_count ?? 0}`]) : "",
      des ? this.moduleSummaryCard("design", "Design", [`Status: ${des.design_status || "draft"}`, `Mocks: ${desRep.screens_with_mock ?? 0}/${desRep.screens_count ?? 0}`, `Pronto p/ UI: ${desRep.ready_for_ui_impl ? "Sim" : "Não"}`]) : "",
    ].join("");
    const extraTop = this.spawnBanner(this.d().hub) + this.showcaseBanner(this.d().journey) + this.techDebtBanner(this.d().hub);
    const compliance = this.complianceSection(sec);
    const extraBottom = this.releaseSection(this.d().release) + (summaries || compliance ? `<section class="section glass"><h2>Security · A11y · Design · Compliance</h2><div class="cards-grid">${summaries}${compliance}</div></section>` : "") + this.learningSection(this.d().learning);
    return extraTop + this.heroSection() + this.phaseFunnelSection(this.d().journey) + this.moduleSummaries() + this.deliveriesJourneySection(this.d().journey) + this.activityAndAlerts() + extraBottom;
  },

  processKpis() {
    const p = this.d().processData?.aggregates?.project || {};
    const gates = this.d().processData?.gates || {};
    return `
      <section class="grid-kpis">
        <article class="kpi-card glass"><div class="kpi-icon">👤</div><span class="kpi-label">Tempo humano</span><span class="kpi-value">${this.fmtHours(p.human_active_seconds)}</span><div class="kpi-note">Execução ativa do time.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🤖</div><span class="kpi-label">Tempo IA</span><span class="kpi-value">${this.fmtHours(p.ai_execution_seconds)}</span><div class="kpi-note">Aceleração da entrega assistida.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🛌</div><span class="kpi-label">Tempo ocioso</span><span class="kpi-value">${this.fmtHours(p.idle_seconds)}</span><div class="kpi-note">Ajuda a expor gargalo escondido.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🚦</div><span class="kpi-label">Gate de design</span><span class="kpi-value">${this.esc(gates.design_status || '—')}</span><div class="kpi-note">${this.esc(gates.project_name || '')}</div></article>
      </section>
    `;
  },

  renderGantt() {
    const gantt = this.d().processData?.gantt || {};
    const tasks = gantt.tasks || [];
    if (!tasks.length) return '<div class="empty">Sem dados de Gantt.</div>';
    const start = new Date(gantt.range_start).getTime();
    const end = new Date(gantt.range_end).getTime();
    const total = end - start || 1;
    const tickCount = 7;
    const ticks = [];
    for (let i=0; i<tickCount; i++) {
      const t = start + ((total/(tickCount-1))*i);
      ticks.push(this.fmtDate(t));
    }
    const rows = tasks.map(task=>{
      const ts = new Date(task.actual_start || task.planned_start).getTime();
      const te = new Date(task.actual_end || task.planned_end || task.planned_start).getTime();
      const left = Math.max(0, ((ts - start) / total) * 100);
      const width = Math.max(2, ((Math.max(te, ts + 1) - ts) / total) * 100);
      const cls = task.status === 'done' ? 'gantt-done' : (task.kind === 'milestone' ? 'gantt-milestone' : 'gantt-forecast');
      return `
        <div class="gantt-row">
          <div>
            <div class="gantt-label">${this.esc(task.label)}</div>
            <div class="gantt-sub">${this.esc(task.group)} · ${this.esc(task.status)}</div>
          </div>
          <div class="gantt-bar-wrap">
            <div class="gantt-bar ${cls}" style="left:${left}%;width:${width}%;">${this.esc(task.kind)}</div>
          </div>
        </div>`;
    }).join('');
    return `
      <div class="section glass">
        <div class="section-header"><div class="section-title"><h2>Roadmap temporal</h2><p>Gantt simplificado, elegante e legível. Porque sofrer com tabela infinita não agrega valor ao steering.</p></div></div>
        <div class="gantt-scale" style="--ticks:${tickCount};">${ticks.map(t=>`<span>${this.esc(t)}</span>`).join('')}</div>
        <div class="gantt">${rows}</div>
      </div>`;
  },

  renderProcess() {
    const forecasts = this.d().processData?.forecasts?.cards || [];
    const rounds = (this.d().processData?.rounds || []).slice(0, 8);
    const sessions = (this.d().processData?.sessions || []).slice(0, 6);
    const events = (this.d().processData?.calendar_events || []).slice(0, 10);
    return this.heroSection() + this.processKpis() + this.renderGantt() + `
      <section class="subgrid-2">
        <div class="section glass">
          <div class="section-header"><div class="section-title"><h2>Forecast por fase</h2><p>Projeção dos próximos cards com base no histórico observado.</p></div></div>
          <div class="cards-grid">
            ${forecasts.map(f=>`<article class="page-card" style="padding:18px;border-radius:18px;">
              <div class="pill info">${this.esc(f.phase)}</div>
              <h3 style="margin:14px 0 8px;">${this.esc(f.card_id)} — ${this.esc(f.title)}</h3>
              <p class="muted">Entrega estimada: <strong>${this.esc(this.fmtDate(f.forecast_delivery_date))}</strong></p>
              <div style="margin-top:10px;">${this.progress(f.confidence === 'alta' ? 86 : 62)}</div>
              <p class="muted" style="margin-top:10px;">Esforço ativo ${f.estimated_active_days}d · calendário ${f.estimated_calendar_days}d.</p>
            </article>`).join('')}
          </div>
        </div>
        <div class="section glass">
          <div class="section-header"><div class="section-title"><h2>Calendário de marcos</h2><p>Eventos recentes e previstos da jornada.</p></div></div>
          <div class="timeline">
            ${events.map(ev=>`<div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-content"><strong>${this.esc(ev.title)}</strong><div class="meta">${this.esc(ev.phase || '—')} · ${this.esc(this.fmtDate(ev.date))}</div><div class="muted" style="margin-top:6px;">${this.esc(ev.kind)}</div></div></div>`).join('')}
          </div>
        </div>
      </section>
      <section class="subgrid-2">
        <div class="section glass">
          <div class="section-header"><div class="section-title"><h2>Rounds do agente</h2><p>Leitura de turnos, revisão e tempo ocioso.</p></div></div>
          <div class="table-wrap"><table class="table"><thead><tr><th>Round</th><th>Atividade</th><th>Fase</th><th>Humano</th><th>IA</th><th>Idle</th></tr></thead><tbody>
            ${rounds.map(r=>`<tr><td>${this.esc(this.fmtDateTime(r.at))}</td><td>${this.esc(r.activity)}</td><td>${this.esc(r.phase)}</td><td>${this.fmtHours(r.human_active_seconds)}</td><td>${this.fmtHours(r.ai_execution_seconds)}</td><td>${this.fmtHours(r.idle_before_seconds)}</td></tr>`).join('')}
          </tbody></table></div>
        </div>
        <div class="section glass">
          <div class="section-header"><div class="section-title"><h2>Sessões humanas</h2><p>Blocos de trabalho capturados pelo método.</p></div></div>
          <div class="activity-list">
            ${sessions.map(s=>`<div class="activity-item"><div class="activity-top"><strong>${this.esc(s.activity)}</strong><span class="pill info">${this.esc(s.phase)}</span></div><div class="muted">${this.esc(this.fmtDateTime(s.started_at))} → ${this.esc(this.fmtDateTime(s.ended_at))}</div><div class="muted" style="margin-top:6px;">Atividade humana: ${this.esc(s.human_active_minutes)} minutos</div></div>`).join('')}
          </div>
        </div>
      </section>`;
  },

  renderQuality() {
    const reqs = this.d().quality?.requirements || [];
    const gaps = this.d().quality?.gaps || [];
    return this.heroSection() + `
      <section class="grid-kpis">
        <article class="kpi-card glass"><div class="kpi-icon">🧪</div><span class="kpi-label">Última execução</span><span class="kpi-value">${this.esc(this.d().quality?.last_run?.overall || '—')}</span><div class="kpi-note">${this.esc(this.fmtDateTime(this.d().quality?.last_run?.run_at))}</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🧱</div><span class="kpi-label">Cobertura back</span><span class="kpi-value">${this.d().quality?.coverage?.backend?.lines ?? 0}%</span><div class="kpi-note">Threshold ${this.d().quality?.coverage?.backend?.threshold ?? 0}%</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🖥</div><span class="kpi-label">Cobertura front</span><span class="kpi-value">${this.d().quality?.coverage?.frontend?.lines ?? 0}%</span><div class="kpi-note">Threshold ${this.d().quality?.coverage?.frontend?.threshold ?? 0}%</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🧷</div><span class="kpi-label">Gaps ativos</span><span class="kpi-value">${gaps.length}</span><div class="kpi-note">Spec → Teste → Matriz</div></article>
      </section>
      <section class="subgrid-2">
        <div class="section glass">
          <div class="section-header"><div class="section-title"><h2>Saúde da cobertura</h2><p>Visual limpo para mostrar se os thresholds estão protegidos.</p></div></div>
          <div class="metric-row">
            <div class="item"><strong>Backend — lines ${this.d().quality?.coverage?.backend?.lines ?? 0}%</strong>${this.progress(this.d().quality?.coverage?.backend?.lines, this.d().quality?.coverage?.backend?.meets_threshold ? 'success' : 'warn')}<div class="muted" style="margin-top:8px;">Branches ${this.d().quality?.coverage?.backend?.branches ?? 0}% · threshold ${this.d().quality?.coverage?.backend?.threshold ?? 0}%.</div></div>
            <div class="item"><strong>Frontend — lines ${this.d().quality?.coverage?.frontend?.lines ?? 0}%</strong>${this.progress(this.d().quality?.coverage?.frontend?.lines, this.d().quality?.coverage?.frontend?.meets_threshold ? 'success' : 'warn')}<div class="muted" style="margin-top:8px;">Branches ${this.d().quality?.coverage?.frontend?.branches ?? 0}% · threshold ${this.d().quality?.coverage?.frontend?.threshold ?? 0}%.</div></div>
          </div>
        </div>
        <div class="section glass">
          <div class="section-header"><div class="section-title"><h2>Resumo por camada</h2><p>Visão rápida do status unitário, integração e E2E.</p></div></div>
          <div class="cards-grid">
            ${Object.entries(this.d().quality?.last_run?.layers_summary || {}).map(([key, item])=>`<article class="page-card" style="padding:16px;border-radius:16px;">
              <div class="pill ${this.badgeCls(item.status)}">${this.esc(key)}</div>
              <h3 style="margin:12px 0 8px;">${this.esc(item.status)}</h3>
              <p class="muted">Passou: ${item.passed ?? 0} · Falhou: ${item.failed ?? 0}</p>
            </article>`).join('')}
          </div>
        </div>
      </section>
      <section class="section glass">
        <div class="section-header"><div class="section-title"><h2>Requisitos e TDD</h2><p>Pronto para leitura operacional e apresentação para liderança técnica.</p></div></div>
        <div class="table-wrap"><table class="table"><thead><tr><th>REQ</th><th>Título</th><th>Prioridade</th><th>Spec</th><th>Camadas</th><th>Resultado</th><th>Gaps</th></tr></thead><tbody>
          ${reqs.map(r=>`<tr>
            <td><strong>${this.esc(r.req_id)}</strong></td>
            <td>${this.esc(r.title)}</td>
            <td>${this.esc(r.priority || '—')}</td>
            <td>${this.statusPill(r.spec_status || '—')}</td>
            <td>${Object.entries(r.layers || {}).filter(([,v])=>v.required).map(([k,v])=>`${this.esc(k)}: ${this.esc(v.status)}`).join('<br>')}</td>
            <td>${r.all_layers_green ? '<span class="pill ok">Green</span>' : '<span class="pill warn">Parcial</span>'}</td>
            <td>${r.gap_layers?.length ? r.gap_layers.map(esc).join(', ') : '—'}</td>
          </tr>`).join('')}
        </tbody></table></div>
      </section>
      <section class="section glass">
        <div class="section-header"><div class="section-title"><h2>Lacunas que merecem carinho</h2><p>Ou, traduzindo para o mundo real: o que pode sabotar a sua demo se você ignorar.</p></div></div>
        <div class="alert-list">${gaps.map(g=>`<div class="alert-item"><strong>${this.esc(g.req_id)} — ${this.esc(g.title)}</strong><div class="muted" style="margin-top:6px;">${this.esc((g.gap_layers||[]).join(' · '))}</div></div>`).join('') || '<div class="notice good">Nenhum gap encontrado.</div>'}</div>
      </section>`;
  },

  renderSecurity() {
    const checklist = this.d().security?.checklist || [];
    const reqs = this.d().security?.requirements || [];
    const gaps = this.d().security?.gaps || [];
    return this.heroSection() + `
      <section class="grid-kpis">
        <article class="kpi-card glass"><div class="kpi-icon">🛡</div><span class="kpi-label">Checklist</span><span class="kpi-value">${this.d().security?.report?.checklist_pct ?? 0}%</span><div class="kpi-note">${this.d().security?.report?.checklist_ok ?? 0}/${this.d().security?.report?.checklist_total ?? 0} itens concluídos.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🔐</div><span class="kpi-label">REQs sensíveis</span><span class="kpi-value">${this.d().security?.report?.sensitive_count ?? 0}</span><div class="kpi-note">Escopo que toca dados e superfícies críticas.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">📉</div><span class="kpi-label">Sensitive gaps</span><span class="kpi-value">${this.d().security?.report?.sensitive_gaps ?? 0}</span><div class="kpi-note">Ponto que merece priorização.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">⚖</div><span class="kpi-label">LGPD</span><span class="kpi-value">${this.d().security?.compliance?.lgpd?.filled ? 'OK' : 'Pendente'}</span><div class="kpi-note">Compliance sem maquiagem.</div></article>
      </section>
      <section class="subgrid-2">
        <div class="section glass"><div class="section-header"><div class="section-title"><h2>Checklist de postura</h2><p>Transparência visual do que já foi verificado.</p></div></div>
          <div class="check-list">${checklist.map(it=>`<div class="check-item"><div class="activity-top"><strong>${this.esc(it.label)}</strong>${it.checked ? '<span class="pill ok">feito</span>' : '<span class="pill warn">pendente</span>'}</div></div>`).join('')}</div>
        </div>
        <div class="section glass"><div class="section-header"><div class="section-title"><h2>Compliance</h2><p>Recorte executivo para aprovações mais sensíveis.</p></div></div>
          <div class="metric-row">
            <div class="item"><strong>LGPD</strong>${this.progress(this.d().security?.compliance?.lgpd?.filled ? 100 : 32, this.d().security?.compliance?.lgpd?.filled ? 'success' : 'warn')}<div class="muted" style="margin-top:8px;">Matriz de dados pessoais ainda ${this.d().security?.compliance?.lgpd?.filled ? 'preenchida' : 'pendente'}.</div></div>
            <div class="item"><strong>Compliance geral</strong>${this.progress(this.d().security?.report?.compliance_ok ? 100 : 48, this.d().security?.report?.compliance_ok ? 'success' : 'warn')}<div class="muted" style="margin-top:8px;">Change types preenchidos: ${(this.d().security?.compliance?.change_types || []).length}.</div></div>
          </div>
          ${gaps.length ? `<div class="notice bad" style="margin-top:14px;"><strong>Gap prioritário:</strong> ${this.esc(gaps[0].gap)}</div>` : '<div class="notice good" style="margin-top:14px;">Sem gaps sensíveis em aberto.</div>'}
        </div>
      </section>
      <section class="section glass">
        <div class="section-header"><div class="section-title"><h2>REQs sob olhar de segurança</h2><p>Excelente para merge sensível e conversa com arquitetura.</p></div></div>
        <div class="table-wrap"><table class="table"><thead><tr><th>REQ</th><th>Título</th><th>Sensível</th><th>Threat model</th><th>Spec</th><th>Status</th></tr></thead><tbody>
          ${reqs.map(r=>`<tr><td><strong>${this.esc(r.req_id)}</strong></td><td>${this.esc(r.title)}</td><td>${r.sensitive ? '<span class="pill warn">Sim</span>' : '<span class="pill neutral">Não</span>'}</td><td>${r.has_threat_model ? '<span class="pill ok">Presente</span>' : '<span class="pill bad">Ausente</span>'}</td><td>${this.statusPill(r.spec_status)}</td><td>${gaps.find(g=>g.req_id===r.req_id) ? '<span class="pill bad">Com gap</span>' : '<span class="pill ok">OK</span>'}</td></tr>`).join('')}
        </tbody></table></div>
      </section>`;
  },

  renderA11y() {
    const checklist = this.d().a11y?.checklist || [];
    const screens = this.d().a11y?.screens || [];
    const gaps = this.d().a11y?.gaps || [];
    const checkedPct = checklist.length ? Math.round((checklist.filter(i=>i.checked).length / checklist.length) * 100) : 0;
    return this.heroSection() + `
      <section class="grid-kpis">
        <article class="kpi-card glass"><div class="kpi-icon">♿</div><span class="kpi-label">Checklist</span><span class="kpi-value">${checkedPct}%</span><div class="kpi-note">${checklist.filter(i=>i.checked).length}/${checklist.length} itens concluídos.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🖼</div><span class="kpi-label">Telas</span><span class="kpi-value">${screens.length}</span><div class="kpi-note">Mocks cobertos pela monitoria.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🧭</div><span class="kpi-label">Fluxos críticos</span><span class="kpi-value">${checklist.filter(i=>/teclado/i.test(i.label) && i.checked).length ? 'OK' : 'Pendente'}</span><div class="kpi-note">Navegação por teclado precisa fechar o ciclo.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">📌</div><span class="kpi-label">Apontamentos</span><span class="kpi-value">${gaps.length}</span><div class="kpi-note">Itens com ação recomendada.</div></article>
      </section>
      <section class="subgrid-2">
        <div class="section glass"><div class="section-header"><div class="section-title"><h2>Checklist WCAG</h2><p>Painel simples, útil e convincente.</p></div></div>
          <div class="check-list">${checklist.map(it=>`<div class="check-item"><div class="activity-top"><strong>${this.esc(it.label)}</strong>${it.checked ? '<span class="pill ok">conforme</span>' : '<span class="pill warn">pendente</span>'}</div></div>`).join('')}</div>
        </div>
        <div class="section glass"><div class="section-header"><div class="section-title"><h2>Lacunas</h2><p>O que falta para a aprovação ficar redondinha.</p></div></div>
          <div class="alert-list">${gaps.map(g=>`<div class="alert-item"><strong>${this.esc(g.label)}</strong><div class="muted" style="margin-top:6px;">${this.esc(g.type)}</div></div>`).join('')}</div>
        </div>
      </section>
      <section class="section glass"><div class="section-header"><div class="section-title"><h2>Telas com status de acessibilidade</h2><p>Com preview funcional para facilitar review conjunto.</p></div></div>
        <div class="screen-grid">${screens.map(s=>`<article class="screen-card"><div><div class="pill ${this.badgeCls(s.a11y_status)}">${this.esc(s.a11y_label || s.a11y_status)}</div><h3 style="margin:12px 0 6px;">${this.esc(s.title)}</h3><p class="muted" style="margin:0;">REQs: ${this.esc((s.linked_reqs||[]).join(', '))}</p></div><div class="screen-preview"><iframe src="../${this.esc(s.html)}" title="${this.esc(s.title)}"></iframe></div><div class="screen-actions"><a class="btn btn-primary" href="../${this.esc(s.html)}" target="_blank">Abrir tela</a></div></article>`).join('')}</div>
      </section>`;
  },

  renderDesign() {
    const screens = this.d().design?.screens || [];
    const gaps = this.d().design?.gaps || [];
    return this.heroSection() + `
      <section class="grid-kpis">
        <article class="kpi-card glass"><div class="kpi-icon">🎨</div><span class="kpi-label">Status do design</span><span class="kpi-value">${this.esc(this.d().design?.design_status || '—')}</span><div class="kpi-note">Gate visual antes do framework UI.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🗂</div><span class="kpi-label">Mocks presentes</span><span class="kpi-value">${screens.length}</span><div class="kpi-note">Telas prontas para review funcional.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">🔗</div><span class="kpi-label">Pattern version</span><span class="kpi-value">${this.esc(this.d().design?.pattern_version || 'v1')}</span><div class="kpi-note">Linguagem visual rastreável.</div></article>
        <article class="kpi-card glass"><div class="kpi-icon">⚠</div><span class="kpi-label">Gaps</span><span class="kpi-value">${gaps.length}</span><div class="kpi-note">Itens que impedem o “approved”.</div></article>
      </section>
      <section class="subgrid-2">
        <div class="section glass"><div class="section-header"><div class="section-title"><h2>Readiness do design</h2><p>Resumo claro para aprovação de produto e engenharia.</p></div></div>
          <div class="metric-row">
            <div class="item"><strong>Status geral</strong>${this.progress(this.d().design?.design_status === 'approved' ? 100 : 72, this.d().design?.design_status === 'approved' ? 'success' : 'warn')}<div class="muted" style="margin-top:8px;">Aprovação atual: ${this.esc(this.d().design?.design_status || '—')}.</div></div>
            <div class="item"><strong>Matriz de telas</strong>${this.progress(screens.length ? 100 : 0, screens.length ? 'success' : 'bad')}<div class="muted" style="margin-top:8px;">${screens.length} mock(s) com preview navegável.</div></div>
          </div>
          ${gaps.length ? `<div class="notice" style="margin-top:14px;">${this.esc(gaps.map(g=>g.label).join(' · '))}</div>` : '<div class="notice good" style="margin-top:14px;">Design aprovado sem gaps.</div>'}
        </div>
        <div class="section glass"><div class="section-header"><div class="section-title"><h2>Checklist visual</h2><p>Leitura dos itens de aprovação geral.</p></div></div>
          <div class="check-list">${(this.d().design?.general_checklist || []).map(it=>`<div class="check-item"><div class="activity-top"><strong>${this.esc(it.label || it.item || 'Checklist')}</strong>${it.checked ? '<span class="pill ok">feito</span>' : '<span class="pill warn">pendente</span>'}</div></div>`).join('') || '<div class="empty">Checklist geral não informado no dataset demo.</div>'}</div>
        </div>
      </section>
      <section class="section glass"><div class="section-header"><div class="section-title"><h2>Telas monitoradas</h2><p>Cards visuais prontos para demo e navegação local.</p></div></div>
        <div class="screen-grid">${screens.map(s=>`<article class="screen-card"><div><div class="pill info">${this.esc((s.linked_reqs||[]).join(', '))}</div><h3 style="margin:12px 0 6px;">${this.esc(s.title)}</h3><p class="muted" style="margin:0;">${this.esc(s.html)}</p></div><div class="screen-preview"><iframe src="../${this.esc(s.html)}" title="${this.esc(s.title)}"></iframe></div><div class="screen-actions"><a class="btn btn-primary" href="../${this.esc(s.html)}" target="_blank">Ver HTML</a></div></article>`).join('')}</div>
      </section>`;
  },

  async loadScript(src) {
    if (document.querySelector(`script[src="${src}"]`)) return;
    await new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error(`Falha ao carregar ${src}`));
      document.head.appendChild(s);
    });
  },

  loadLegacyCss(href, id) {
    if (document.getElementById(id)) return;
    const l = document.createElement("link");
    l.id = id;
    l.rel = "stylesheet";
    l.href = href;
    document.head.appendChild(l);
  },

  async mountProcess(root) {
    this.loadLegacyCss("../process-metrics/process-metrics.css", "hub-process-css");
    root.innerHTML = `<div class="hub-legacy-wrap pm-page" id="pmPage">${LegacyTemplates.processMain}</div>`;
    await this.loadScript("../process-metrics/process-metrics.js");
    ProcessMetrics.load = async () => { ProcessMetrics.data = HubData.get("process.data.json"); return ProcessMetrics.data; };
    await ProcessMetrics.boot();
    this.processBooted = true;
  },

  async mountGuide(root) {
    const sources = ["../project-hub.md", "/project-hub.md"];
    let text = null;
    for (const src of sources) {
      try {
        const res = await fetch(src);
        if (res.ok) {
          text = await res.text();
          break;
        }
      } catch (_) {}
    }
    if (!text) throw new Error("Não foi possível carregar docs/meta/project-hub.md");
    const { html, toc } = HubMarkdown.render(text);
    const tocItems = toc
      .map((t) => `<a class="hub-guide-toc-link hub-guide-toc-l${t.level}" href="#${this.esc(t.id)}">${this.esc(t.text)}</a>`)
      .join("");
    root.innerHTML = `
      <section class="hub-guide-shell">
        <aside class="section glass hub-guide-toc" aria-label="Índice">
          <p class="hub-guide-toc-title">Neste guia</p>
          <nav class="hub-guide-toc-nav">${tocItems || '<span class="muted">—</span>'}</nav>
          <p class="hub-guide-source muted">Fonte: <code>docs/meta/project-hub.md</code></p>
        </aside>
        <article class="section glass hub-guide-prose hub-md-body">${html}</article>
      </section>`;
    root.querySelectorAll("a.hub-md-link-doc").forEach((a) => {
      a.addEventListener("click", async (e) => {
        e.preventDefault();
        const url = a.getAttribute("href");
        try {
          const res = await fetch(url);
          if (!res.ok) throw new Error("404");
          const doc = HubMarkdown.render(await res.text());
          const article = root.querySelector(".hub-guide-prose");
          if (article) {
            article.innerHTML = `<p class="hub-guide-back"><a href="#guide">← Guia principal</a></p>${doc.html}`;
            article.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        } catch {
          window.open(url, "_blank");
        }
      });
    });
  },

  async mountQuality(root) {
    this.loadLegacyCss("../quality-health/quality-health.css", "hub-quality-css");
    root.innerHTML = `<div class="hub-legacy-wrap pm-page qh-page" id="qhPage">${LegacyTemplates.qualityMain}</div>`;
    await this.loadScript("../quality-health/quality-health.js");
    QualityHealth.load = async () => { QualityHealth.data = HubData.get("quality.data.json"); return QualityHealth.data; };
    await QualityHealth.load();
    QualityHealth.initTheme();
    QualityHealth.initTabs();
    QualityHealth.initE2eToggle();
    QualityHealth.initActions();
    QualityHealth.initFilters();
    QualityHealth.renderAll();
    this.qualityBooted = true;
  },

  spawnBanner(hub) {
    const t = hub?.template || {};
    if (!t.is_upstream || !t.upstream_dev_mode) return "";
    return `<div class="hub-spawn-banner" role="status"><strong>Modelo upstream (evolução do template)</strong> — produto novo? <code>make create-project NAME="..."</code> e abra a pasta irmã no Cursor. <a href="../../operations/spawn-project.md">spawn-project.md</a></div>`;
  },

  showcaseBanner(journey) {
    const mode = journey?.data_mode || "real";
    if (mode === "real" || !journey?.report?.showcase_banner) return "";
    return `<div class="hub-showcase-banner" role="status"><strong>Dados parciais de exemplo</strong> — preencha discovery e planejamento MVP para o hub refletir o projeto real. <span class="muted">modo: ${this.esc(mode)}</span></div>`;
  },

  techDebtBanner(hub) {
    const count = hub?.kpis?.tech_debt_critical ?? hub?.tech_debt?.report?.critical_open_count ?? 0;
    if (!count) return "";
    return `<div class="hub-tech-debt-banner" role="alert"><strong>Dívida técnica crítica aberta:</strong> ${count} item(ns) — revise docs/tech-debt.md.</div>`;
  },

  releaseSection(release) {
    const rep = release?.report || {};
    if (!rep.last_tag && !rep.changelog_preview && !rep.last_version) return "";
    return `<section class="section glass hub-release-card"><h2>Release</h2><p><strong>${this.esc(rep.last_tag || rep.last_version || "—")}</strong>${rep.last_tag_date ? ` · ${this.esc(this.fmtDate(rep.last_tag_date))}` : ""}</p>${rep.changelog_preview ? `<pre class="hub-changelog-preview">${this.esc(rep.changelog_preview.slice(0, 280))}</pre>` : ""}</section>`;
  },

  learningSection(learning) {
    const retros = learning?.retrospectives || [];
    const rep = learning?.report || {};
    const bench = learning?.benchmarks || {};
    const pending = rep.pending_phases || [];
    const retroHtml = retros.length
      ? retros.map((r) => `<li><strong>${this.esc(r.phase)}</strong> ${this.statusPill(r.status)}${r.file ? ` · ${this.esc(r.file)}` : ""}</li>`).join("")
      : "<li class='muted'>Nenhuma fase em docs/meta/retrospectives/index.md</li>";
    const medianLines = Object.entries(bench.medians || {}).slice(0, 4).map(([k, v]) => `<li><code>${this.esc(k)}</code>: ${this.esc(v)}</li>`).join("");
    return `<section class="section glass hub-learning-card"><h2>Aprendizado entre projetos</h2>
      ${pending.length ? `<p class="notice warn">Retro pendente: ${pending.map((p) => this.esc(p)).join(", ")}</p>` : ""}
      <div class="subgrid-2"><div><h3>Retrospectivas</h3><ul>${retroHtml}</ul></div>
      <div><h3>Benchmarks</h3><p class="muted">${bench.snapshot_count ?? 0} snapshot(s)</p>${medianLines ? `<ul>${medianLines}</ul>` : "<p class='muted'>Sem medians — rode aggregate-process-benchmarks.sh</p>"}</div></div></section>`;
  },

  expandDeliveryRow(d) {
    const details = d.req_details || [];
    if (!details.length && !d.card_path && !d.branch) return "";
    const reqRows = details.map((r) => `<tr><td>${this.esc(r.req_id)}</td><td>${this.esc(r.spec_status || "—")}</td><td>${r.quality_gaps ?? 0}</td><td>${this.esc(r.matrix_status || "—")}</td><td class="muted">${this.esc(r.test_unit || "—")} / ${this.esc(r.test_integ || "—")}</td></tr>`).join("");
    const effort = d.effort ? `<p class="muted">Esforço: humano ${Math.round((d.effort.human_active_seconds || 0) / 60)} min · IA ${Math.round((d.effort.ai_execution_seconds || 0) / 60)} min</p>` : "";
    return `<details class="hub-delivery-details"><summary>Detalhes</summary>${effort}${d.card_path ? `<p class="muted"><code>${this.esc(d.card_path)}</code>${d.branch ? ` · ${this.esc(d.branch)}` : ""}</p>` : ""}${reqRows ? `<div class="table-wrap"><table class="table"><thead><tr><th>REQ</th><th>Spec</th><th>Gaps</th><th>Matriz</th><th>Testes</th></tr></thead><tbody>${reqRows}</tbody></table></div>` : ""}</details>`;
  },

  filterDeliveriesByPhase(phaseId) {
    const tbody = document.querySelector("#hubDeliveries tbody");
    const hint = document.getElementById("hubPhaseFilterHint");
    if (!tbody) return;
    let visible = 0;
    tbody.querySelectorAll(".hub-delivery-row").forEach((row) => {
      const rowPhase = row.getAttribute("data-phase") || "";
      const match = !phaseId || rowPhase === phaseId || (phaseId.startsWith("FASE-") && rowPhase === phaseId);
      const show = !phaseId || match;
      row.hidden = !show;
      if (show) visible += 1;
    });
    document.querySelectorAll(".hub-phase-step-premium").forEach((el) => {
      el.classList.toggle("hub-phase-filter-active", el.getAttribute("data-phase-id") === phaseId);
    });
    if (hint) {
      if (phaseId) {
        hint.hidden = false;
        hint.textContent = `Filtro: ${phaseId} (${visible} entrega(s)) — clique novamente na fase para limpar`;
      } else {
        hint.hidden = true;
        hint.textContent = "";
      }
    }
  },

  bindPhaseFunnelFilters() {
    let activePhase = null;
    document.querySelectorAll(".hub-phase-step-premium[data-phase-clickable='true']").forEach((step) => {
      const handler = () => {
        const pid = step.getAttribute("data-phase-id");
        if (!pid?.startsWith("FASE-")) return;
        activePhase = activePhase === pid ? null : pid;
        this.filterDeliveriesByPhase(activePhase);
      };
      step.addEventListener("click", handler);
      step.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          handler();
        }
      });
    });
  },

  async navigate(page, sub = null) {
    if (typeof page === "string" && page.includes("/")) {
      const parsed = this.parseHash(`#${page}`);
      page = parsed.page;
      sub = parsed.sub;
    }
    if (!this.MODULE_META[page] && page !== "guide") page = "overview";
    this.page = page;
    this.pageSub = sub;
    this.$$(".nav-link").forEach(a => a.classList.toggle("active", a.getAttribute("data-nav") === page));
    const root = this.$("#contentRoot");
    root.innerHTML = "<p class='muted'>Carregando…</p>";
    try {
      if (page === "guide") await this.mountGuide(root);
      else if (page === "process") await this.mountProcess(root);
      else if (page === "quality") {
        await this.mountQuality(root);
        if (sub === "gaps") this.activateQualityTab("gaps");
      } else {
        const html = { overview: () => this.renderOverview(), security: () => this.renderSecurity(), a11y: () => this.renderA11y(), design: () => this.renderDesign() }[page] || (() => this.renderOverview());
        root.innerHTML = html();
        this.$$("[data-copy-prompt]", root).forEach(btn => btn.addEventListener("click", () => this.copyText(this.d().hub?.next_step?.prompt || "")));
        if (page === "overview") this.bindPhaseFunnelFilters();
      }
    } catch (e) {
      root.innerHTML = `<div class="notice bad">${this.esc(e.message)}</div>`;
    } finally {
      this.buildSidebar();
      this.buildTopbar();
      this.bindThemeToggle();
    }
  },

  initNav() {
    this.$$(".nav-link").forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        location.hash = `#${a.getAttribute("data-nav") || "overview"}`;
      });
    });
    window.addEventListener("hashchange", () => {
      const { page, sub } = this.parseHash();
      if (this.routeKey(page, sub) !== this.routeKey(this.page, this.pageSub)) this.navigate(page, sub);
    });
  },

  async refresh() {
    const btn = this.$("#refreshBtn");
    if (btn) btn.disabled = true;
    try {
      const res = await fetch("/api/refresh", { method: "POST" });
      const body = await res.json();
      if (!res.ok || !body.ok) throw new Error(body.message || "Falha");
      await HubData.load(true);
      this.processBooted = false;
      this.qualityBooted = false;
      await this.navigate(this.page);
    } catch (e) { this.showToast(e.message || "Erro"); }
    finally { if (btn) btn.disabled = false; }
  },

  syncMobileSidebar() {
    const el = document.getElementById("hubMobileSidebar");
    if (!el) return;
    if (window.matchMedia("(min-width: 761px)").matches) {
      el.setAttribute("open", "");
    }
  },

  bindMobileSidebar() {
    this.syncMobileSidebar();
    window.addEventListener("resize", () => this.syncMobileSidebar(), { passive: true });
  },

  async init() {
    this.initNav();
    this.bindThemeToggle();
    this.bindMobileSidebar();
    this.$("#refreshBtn")?.addEventListener("click", () => this.refresh());
    await HubData.load();
    const { page, sub } = this.parseHash();
    await this.navigate(page, sub);
  },
};

window.ProjectHubPremium = ProjectHubPremium;
const ProjectHub = { init: () => ProjectHubPremium.init() };
