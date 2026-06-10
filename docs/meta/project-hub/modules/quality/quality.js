/**
 * Painel saúde da qualidade — visão executiva + técnica
 */
const QualityHealth = {
  data: null,
  LOCALE: "pt-BR",
  PANEL_LAYERS: ["unit_back", "unit_front", "integration", "e2e"],
  LAYER_ORDER: ["unit_back", "unit_front", "integration", "e2e", "security"],
  filters: { req: "all", status: "all", priority: "all", kind: "all" },
  e2eView: "cards",
  COLORS: {
    pass: "#10b981",
    fail: "#ef4444",
    pending: "#94a3b8",
    missing: "#f59e0b",
    unknown: "#6366f1",
    skip: "#cbd5e1",
    accent: "#6366f1",
    track: "#e2e8f0",
  },

  async load() {
    const res = await fetch(`data/quality.data.json?t=${Date.now()}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Não foi possível carregar data/quality.data.json");
    this.data = await res.json();
    return this.data;
  },

  esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  },

  fmtDate(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return new Intl.DateTimeFormat(this.LOCALE, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(d);
  },

  bizStatus(st) {
    return (this.data?.business_status || {})[st] || this.statusLabel(st);
  },

  statusLabel(st) {
    return (this.data?.status_legend || {})[st] || st;
  },

  statusClass(st) {
    return `qh-st-${st || "unknown"}`;
  },

  pill(st) {
    const label = this.bizStatus(st);
    return `<span class="qh-pill ${this.statusClass(st)}">${this.esc(label)}</span>`;
  },

  layerLabel(layer) {
    return (this.data?.layer_labels || {})[layer] || layer;
  },

  overallBiz(overall) {
    const map = {
      pass: { label: "Suite aprovada", cls: "qh-overall-pass" },
      fail: { label: "Falhas detectadas", cls: "qh-overall-fail" },
      partial: { label: "Aprovação parcial", cls: "qh-overall-partial" },
      unknown: { label: "Sem execução recente", cls: "qh-overall-unknown" },
    };
    return map[overall] || map.unknown;
  },

  reqById() {
    const m = {};
    (this.data?.requirements || []).forEach((r) => {
      m[r.req_id] = r;
    });
    return m;
  },

  priorityMatches(priority, filter) {
    if (filter === "all") return true;
    const p = priority || "";
    if (filter === "P0") return p === "P0";
    if (filter === "P1") return p === "P1";
    if (filter === "P2+") return p !== "P0" && p !== "P1";
    return true;
  },

  matchesFilters(item) {
    const f = this.filters;
    if (f.req !== "all" && item.req_id !== f.req) return false;
    const req = this.reqById()[item.req_id] || {};
    const priority = item.priority ?? req.priority;
    const kind = item.req_kind ?? req.req_kind ?? "functional";
    if (!this.priorityMatches(priority, f.priority)) return false;
    if (f.kind === "functional" && kind !== "functional") return false;
    if (f.kind === "non_functional" && kind !== "non_functional") return false;
    if (f.status !== "all" && (item.status || "unknown") !== f.status) return false;
    return true;
  },

  allScorableCases() {
    const cases = [];
    for (const req of this.data?.requirements || []) {
      for (const [layer, linfo] of Object.entries(req.layers || {})) {
        if (!linfo?.required) continue;
        for (const c of linfo.cases || []) {
          if (c.status === "not_required") continue;
          cases.push({
            ...c,
            layer,
            req_id: req.req_id,
            req_kind: req.req_kind,
            priority: req.priority,
            title: req.title,
          });
        }
      }
    }
    return cases;
  },

  filteredCases() {
    return this.allScorableCases().filter((c) => this.matchesFilters(c));
  },

  filteredRequirements() {
    const f = this.filters;
    return (this.data?.requirements || []).filter((req) => {
      if (f.req !== "all" && req.req_id !== f.req) return false;
      if (!this.priorityMatches(req.priority, f.priority)) return false;
      const kind = req.req_kind || "functional";
      if (f.kind === "functional" && kind !== "functional") return false;
      if (f.kind === "non_functional" && kind !== "non_functional") return false;
      if (f.status !== "all") {
        const cases = this.allScorableCases().filter((c) => c.req_id === req.req_id);
        if (!cases.some((c) => (c.status || "unknown") === f.status)) return false;
      }
      return true;
    });
  },

  filteredGaps() {
    const reqIds = new Set(this.filteredRequirements().map((r) => r.req_id));
    return (this.data?.gaps || []).filter((g) => reqIds.has(g.req_id));
  },

  filteredByLayer(layer) {
    return (this.data?.by_layer?.[layer] || []).filter((it) =>
      this.matchesFilters({
        ...it,
        req_kind: it.req_kind ?? this.reqById()[it.req_id]?.req_kind,
        priority: it.priority ?? this.reqById()[it.req_id]?.priority,
      })
    );
  },

  filteredAnalytics() {
    const scorable = this.filteredCases();
    const weights = {
      pass: 100,
      skip: 95,
      unknown: 55,
      pending: 35,
      missing: 5,
      fail: 0,
    };
    const by_status = {};
    for (const st of Object.keys(weights)) {
      by_status[st] = scorable.filter((c) => c.status === st).length;
    }
    const by_layer = {};
    for (const layer of this.PANEL_LAYERS) {
      const layer_cases = scorable.filter((c) => c.layer === layer);
      if (!layer_cases.length) continue;
      const passed = layer_cases.filter((c) => c.status === "pass").length;
      by_layer[layer] = {
        label: this.layerLabel(layer),
        total: layer_cases.length,
        pass: passed,
        pct_pass: layer_cases.length ? Math.round((passed / layer_cases.length) * 100) : 0,
      };
    }
    return { by_status, by_layer, total: scorable.length, all_total: this.allScorableCases().length };
  },

  filtersActive() {
    return Object.values(this.filters).some((v) => v !== "all");
  },

  saveFilters() {
    try {
      localStorage.setItem("qh-filters", JSON.stringify(this.filters));
    } catch (_) {
      /* ignore */
    }
  },

  loadFilters() {
    try {
      const raw = localStorage.getItem("qh-filters");
      if (raw) {
        const parsed = JSON.parse(raw);
        this.filters = { ...this.filters, ...parsed };
      }
    } catch (_) {
      /* ignore */
    }
  },

  initFilters() {
    this.loadFilters();
    const reqSel = document.getElementById("filterReq");
    if (reqSel) {
      const opts = (this.data?.requirements || [])
        .map((r) => `<option value="${this.esc(r.req_id)}">${this.esc(r.req_id)}</option>`)
        .join("");
      reqSel.innerHTML = `<option value="all">Todos</option>${opts}`;
      reqSel.value = this.filters.req;
    }
    const map = {
      filterStatus: "status",
      filterPriority: "priority",
      filterKind: "kind",
    };
    Object.entries(map).forEach(([id, key]) => {
      const el = document.getElementById(id);
      if (el) el.value = this.filters[key];
    });
    const rerender = () => {
      this.saveFilters();
      this.renderFilteredSections();
      this.updateFilterCount();
    };
    reqSel?.addEventListener("change", (e) => {
      this.filters.req = e.target.value;
      rerender();
    });
    document.getElementById("filterStatus")?.addEventListener("change", (e) => {
      this.filters.status = e.target.value;
      rerender();
    });
    document.getElementById("filterPriority")?.addEventListener("change", (e) => {
      this.filters.priority = e.target.value;
      rerender();
    });
    document.getElementById("filterKind")?.addEventListener("change", (e) => {
      this.filters.kind = e.target.value;
      rerender();
    });
    document.getElementById("filterClear")?.addEventListener("click", () => {
      this.filters = { req: "all", status: "all", priority: "all", kind: "all" };
      this.initFilters();
      rerender();
    });
    this.updateFilterCount();
  },

  updateFilterCount() {
    const el = document.getElementById("filterCount");
    if (!el) return;
    const fa = this.filteredAnalytics();
    const suffix = this.filtersActive() ? " (filtrado)" : "";
    el.textContent = `Exibindo ${fa.total} de ${fa.all_total} cenários${suffix}`;
  },

  initTheme() {
    const embedded = !!document.getElementById("hubPage");
    const page = document.getElementById("qhPage");
    const saved = window.ModeloTheme?.read?.() || localStorage.getItem("modelo-panel-theme") || localStorage.getItem("qh-theme") || "light";
    page.setAttribute("data-theme", saved);
    if (embedded) {
      if (window.ModeloTheme?.apply) window.ModeloTheme.apply(saved);
      return;
    }
    document.documentElement.setAttribute("data-theme", saved);
    document.documentElement.style.colorScheme = saved;
    const btn = document.getElementById("themeToggle");
    if (!btn) return;
    const label = () => (page.getAttribute("data-theme") === "dark" ? "Modo claro" : "Modo escuro");
    btn.textContent = label();
    btn.onclick = () => {
      const next = page.getAttribute("data-theme") === "dark" ? "light" : "dark";
      if (window.ModeloTheme?.persist) window.ModeloTheme.persist(next);
      else {
        page.setAttribute("data-theme", next);
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("qh-theme", next);
        localStorage.setItem("modelo-panel-theme", next);
      }
      btn.textContent = label();
    };
  },

  initTabs() {
    document.querySelectorAll(".pm-tabs button").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".pm-tabs button").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".pm-panel").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        document.querySelector(`[data-panel="${btn.getAttribute("data-tab")}"]`)?.classList.add("active");
      });
    });
  },

  initE2eToggle() {
    document.querySelectorAll("[data-e2e-view]").forEach((btn) => {
      btn.addEventListener("click", () => {
        this.e2eView = btn.getAttribute("data-e2e-view");
        document.querySelectorAll("[data-e2e-view]").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        this.renderE2ePanel();
      });
    });
  },

  initActions() {
    const status = document.getElementById("actionStatus");
    const setStatus = (msg, ok = true) => {
      if (status) {
        status.textContent = msg;
        status.className = `qh-action-status ${ok ? "ok" : "err"}`;
      }
    };
    const post = async (path) => {
      setStatus("Processando…", true);
      try {
        const res = await fetch(path, { method: "POST" });
        const body = await res.json();
        if (!res.ok || !body.ok) throw new Error(body.message || "Falha na operação");
        await this.load();
        this.renderAll();
        setStatus(body.action === "run-tests" ? "Testes executados e painel atualizado." : "Painel atualizado.", true);
      } catch (e) {
        setStatus(e.message || "Erro — use make quality-build no terminal.", false);
      }
    };
    document.getElementById("btnRefresh")?.addEventListener("click", () => post("/api/refresh"));
    document.getElementById("btnRunTests")?.addEventListener("click", () => post("/api/run-tests"));
  },

  renderHero() {
    const lr = this.data.last_run || {};
    const rep = this.data.report || {};
    const an = this.data.analytics || {};
    const overall = lr.overall || "unknown";
    const ob = this.overallBiz(overall);
    const el = document.getElementById("runHero");
    if (!el) return;
    el.innerHTML = `
      <div class="pm-delivery-hero-inner qh-hero-grid">
        <div>
          <p class="pm-delivery-hero-label">Última validação automática</p>
          <p class="pm-delivery-hero-date qh-hero-date-sm">${this.fmtDate(lr.run_at)}</p>
          <p class="pm-delivery-hero-meta">
            <span class="qh-overall-badge ${ob.cls}">${this.esc(ob.label)}</span>
            · Fonte: ${this.esc(lr.source || "—")} · ${this.esc(lr.ci_job || "—")}
          </p>
        </div>
        <aside class="pm-delivery-hero-aside qh-hero-score">
          <p class="qh-hero-score-value">${an.health_score ?? "—"}</p>
          <p class="qh-hero-score-label">${this.esc(an.health_label || "Índice de saúde")}</p>
          <p class="pm-delivery-hero-countdown-sub">${rep.req_fully_green ?? 0} de ${rep.req_total ?? 0} requisitos 100% validados</p>
        </aside>
      </div>`;
  },

  renderKpis() {
    const rep = this.data.report || {};
    const an = this.data.analytics || {};
    const cov = this.data.coverage || {};
    const fe = cov.frontend?.lines;
    const be = cov.backend?.lines;
    document.getElementById("kpiGrid").innerHTML = `
      <div class="pm-kpi qh-kpi"><div class="pm-kpi-label">Requisitos no escopo</div><div class="pm-kpi-value">${rep.req_total ?? 0}</div><div class="pm-kpi-sub">Entregas de negócio rastreadas</div></div>
      <div class="pm-kpi qh-kpi"><div class="pm-kpi-label">Prontos para release</div><div class="pm-kpi-value">${rep.req_fully_green ?? 0} <span class="qh-kpi-pct">${rep.req_fully_green_pct ?? 0}%</span></div><div class="pm-kpi-sub">Todos os testes obrigatórios OK</div></div>
      <div class="pm-kpi qh-kpi"><div class="pm-kpi-label">Cenários aprovados</div><div class="pm-kpi-value">${an.tests_pass ?? 0}<span class="qh-kpi-dim">/${an.tests_total ?? 0}</span></div><div class="pm-kpi-sub">${an.tests_fail ?? 0} falha(s) · ${an.tests_pending ?? 0} pendente(s)</div></div>
      <div class="pm-kpi qh-kpi"><div class="pm-kpi-label">Cobertura média</div><div class="pm-kpi-value">${an.avg_coverage_pct ?? "—"}${an.avg_coverage_pct != null ? "%" : ""}</div><div class="pm-kpi-sub">Back ${be ?? "—"}% · Front ${fe ?? "—"}%</div></div>
      <div class="pm-kpi qh-kpi"><div class="pm-kpi-label">Riscos abertos</div><div class="pm-kpi-value">${rep.gap_count ?? 0}</div><div class="pm-kpi-sub">${rep.gap_functional ?? 0} func. · ${rep.gap_non_functional ?? 0} NFR</div></div>`;
  },

  renderHealthGauge() {
    const el = document.getElementById("healthGauge");
    if (!el) return;
    const score = this.data.analytics?.health_score ?? 0;
    const label = this.data.analytics?.health_label || "";
    const size = 220;
    const r = size / 2 - 16;
    const cx = size / 2;
    const cy = size / 2;
    const circ = 2 * Math.PI * r;
    const filled = (score / 100) * circ;
    const color = score >= 75 ? this.COLORS.pass : score >= 50 ? "#f59e0b" : this.COLORS.fail;
    el.innerHTML = `
      <div class="qh-gauge-wrap">
        <svg class="pm-chart-svg qh-gauge" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}">
          <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${this.COLORS.track}" stroke-width="18"/>
          <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${color}" stroke-width="18"
            stroke-dasharray="${filled} ${circ - filled}" transform="rotate(-90 ${cx} ${cy})" stroke-linecap="round"/>
          <text x="${cx}" y="${cy - 6}" text-anchor="middle" class="qh-gauge-score">${score}</text>
          <text x="${cx}" y="${cy + 14}" text-anchor="middle" class="qh-gauge-sub">${this.esc(label)}</text>
        </svg>
        <ul class="qh-gauge-legend">
          <li><span class="qh-dot" style="background:#10b981"></span> ≥75 Excelente / Bom</li>
          <li><span class="qh-dot" style="background:#f59e0b"></span> 50–74 Atenção</li>
          <li><span class="qh-dot" style="background:#ef4444"></span> &lt;50 Crítico</li>
        </ul>
      </div>`;
  },

  renderTestStatusChart() {
    const el = document.getElementById("testStatusChart");
    if (!el) return;
    const fa = this.filteredAnalytics();
    const bs = fa.by_status || {};
    const items = [
      { key: "pass", label: "Aprovados", v: bs.pass || 0, c: this.COLORS.pass },
      { key: "fail", label: "Falharam", v: bs.fail || 0, c: this.COLORS.fail },
      { key: "pending", label: "Planejados", v: bs.pending || 0, c: this.COLORS.pending },
      { key: "missing", label: "Não criados", v: bs.missing || 0, c: this.COLORS.missing },
      { key: "unknown", label: "Não executados", v: bs.unknown || 0, c: this.COLORS.unknown },
    ].filter((i) => i.v > 0);
    const total = items.reduce((s, i) => s + i.v, 0) || 1;
    const size = 200;
    const r = size / 2 - 14;
    const cx = size / 2;
    const cy = size / 2;
    const circ = 2 * Math.PI * r;
    let offset = 0;
    const arcs = items
      .map((it) => {
        const len = (it.v / total) * circ;
        const dash = `${len} ${circ - len}`;
        const rot = (offset / circ) * 360 - 90;
        offset += len;
        return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${it.c}" stroke-width="20"
          stroke-dasharray="${dash}" transform="rotate(${rot} ${cx} ${cy})"/>`;
      })
      .join("");
    const legend = items
      .map(
        (it) => `<div class="qh-legend-row"><span class="qh-dot" style="background:${it.c}"></span>
          <span>${it.label}</span><strong>${it.v} (${Math.round((it.v / total) * 100)}%)</strong></div>`
      )
      .join("");
    const filtNote = this.filtersActive() ? '<p class="qh-chart-note">Gráfico recalculado com filtros ativos.</p>' : "";
    el.innerHTML = `
      ${filtNote}
      <div class="qh-donut-row">
        <svg class="pm-chart-svg" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}">
          <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${this.COLORS.track}" stroke-width="20"/>
          ${arcs}
          <text x="${cx}" y="${cy + 4}" text-anchor="middle" class="qh-gauge-sub">${fa.total} cenários</text>
        </svg>
        <div class="qh-legend-list">${legend || '<p class="pm-empty">Sem cenários registrados.</p>'}</div>
      </div>`;
  },

  renderCoverageChart() {
    const el = document.getElementById("coverageChart");
    if (!el) return;
    const cov = this.data.coverage || {};
    const sides = [
      { key: "backend", label: "Backend (API / regras)" },
      { key: "frontend", label: "Frontend (telas)" },
    ];
    el.innerHTML = sides
      .map((s) => {
        const c = cov[s.key] || {};
        const pct = c.lines ?? 0;
        const th = c.threshold ?? 90;
        const ok = c.meets_threshold === true;
        const color = ok ? this.COLORS.pass : c.meets_threshold === false ? this.COLORS.fail : this.COLORS.unknown;
        return `
          <div class="qh-cov-row">
            <div class="qh-cov-head"><span>${s.label}</span><strong style="color:${color}">${c.lines ?? "—"}%</strong></div>
            <div class="qh-bar-track"><span class="qh-bar-fill" style="width:${pct}%;background:${color}"></span></div>
            <div class="qh-cov-meta">Meta ${th}% · ${ok ? "✓ atingida" : c.meets_threshold === false ? "✗ abaixo da meta" : "—"}</div>
          </div>`;
      })
      .join("");
  },

  renderLayerHealthChart() {
    const el = document.getElementById("layerHealthChart");
    if (!el) return;
    const byLayer = this.filteredAnalytics().by_layer || {};
    const keys = this.PANEL_LAYERS.filter((k) => byLayer[k]);
    if (!keys.length) {
      el.innerHTML = '<p class="pm-empty">Preencha specs e backlog para ver camadas.</p>';
      return;
    }
    const note = this.filtersActive() ? '<p class="qh-chart-note">Gráfico recalculado com filtros ativos.</p>' : "";
    el.innerHTML =
      note +
      keys
        .map((k) => {
          const L = byLayer[k];
          const pct = L.pct_pass ?? 0;
          const color = pct >= 80 ? this.COLORS.pass : pct >= 50 ? "#f59e0b" : this.COLORS.fail;
          return `
          <div class="pm-bar-row qh-layer-bar">
            <span>${this.esc(L.label || this.layerLabel(k))}</span>
            <div class="pm-bar-track"><span class="pm-seg-human" style="width:${pct}%;background:${color}"></span></div>
            <span class="qh-bar-pct">${L.pass}/${L.total} (${pct}%)</span>
          </div>`;
        })
        .join("");
  },

  renderExecSummary() {
    const el = document.getElementById("execSummary");
    if (!el) return;
    const gaps = this.filteredGaps();
    const e2eItems = this.filteredByLayer("e2e");
    const e2ePass = e2eItems.filter((x) => x.status === "pass").length;
    el.innerHTML = `
      <h2>Resumo para stakeholders</h2>
      <div class="qh-summary-grid">
        <div class="qh-summary-item">
          <h3>O que isso significa?</h3>
          <p>Testes automatizados simulam clientes reais usando o produto. Quanto mais cenários <strong>aprovados</strong>, menor o risco de defeitos em produção.</p>
        </div>
        <div class="qh-summary-item">
          <h3>Fluxos E2E</h3>
          <p><strong>${e2ePass}</strong> de <strong>${e2eItems.length}</strong> jornadas ponta a ponta validadas — inclui login, checkout e fluxos críticos.</p>
        </div>
        <div class="qh-summary-item">
          <h3>Atenção imediata</h3>
          <p>${gaps.length ? `<strong>${gaps.length}</strong> requisito(s) com lacunas:` : "Nenhum gap crítico."} 
          ${gaps.slice(0, 3).map((g) => `<span class="qh-tag">${this.esc(g.req_id)}</span>`).join(" ")}</p>
        </div>
      </div>`;
  },

  renderLegend() {
    const leg = this.data.status_legend || {};
    const biz = this.data.business_status || {};
    document.getElementById("legendBox").innerHTML = `
      <h2>Como ler os indicadores</h2>
      <div class="qh-legend-grid">
        ${Object.entries(leg)
          .map(
            ([k, v]) => `<div class="qh-legend-item">${this.pill(k)}<span>${this.esc(biz[k] || v)}</span></div>`
          )
          .join("")}
      </div>`;
  },

  reqProgress(req) {
    const layers = req.layers || {};
    let reqCount = 0;
    let ok = 0;
    this.PANEL_LAYERS.forEach((l) => {
      const info = layers[l];
      if (!info?.required) return;
      reqCount += 1;
      if (info.status === "pass" || info.status === "skip") ok += 1;
    });
    const pct = reqCount ? Math.round((ok / reqCount) * 100) : 0;
    return { pct, ok, reqCount };
  },

  layerCell(layerInfo) {
    if (!layerInfo || !layerInfo.required) {
      return `<td class="qh-td-center"><span class="qh-pill qh-st-not_required">N/A</span></td>`;
    }
    const st = layerInfo.status || "unknown";
    return `<td class="qh-td-center">${this.pill(st)}</td>`;
  },

  renderRequirements() {
    const reqs = this.filteredRequirements();
    const el = document.getElementById("reqTable");
    if (!reqs.length) {
      el.innerHTML = `<p class="pm-empty">Nenhum requisito corresponde aos filtros.</p>`;
      return;
    }
    const cols = this.PANEL_LAYERS;
    const head = cols.map((l) => `<th>${this.esc(this.layerLabel(l))}</th>`).join("");
    const rows = reqs
      .map((r) => {
        const kind = r.req_kind === "non_functional" ? "non_functional" : "functional";
        const prog = this.reqProgress(r);
        const barColor = prog.pct >= 80 ? this.COLORS.pass : prog.pct >= 50 ? "#f59e0b" : this.COLORS.fail;
        return `<tr>
          <td><strong>${this.esc(r.req_id)}</strong><br><span class="qh-badge ${kind}">${kind === "non_functional" ? "NFR" : "Funcional"}</span></td>
          <td><span class="qh-req-title">${this.esc(r.title)}</span><div class="qh-mini-bar"><span style="width:${prog.pct}%;background:${barColor}"></span></div><span class="qh-mini-meta">${prog.pct}% validado (${prog.ok}/${prog.reqCount})</span></td>
          <td>${this.esc(r.priority)}</td>
          ${cols.map((l) => this.layerCell((r.layers || {})[l])).join("")}
        </tr>`;
      })
      .join("");
    el.innerHTML = `
      <table class="qh-table">
        <thead><tr><th>ID</th><th>Entrega de negócio</th><th>Prior.</th>${head}</tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  },

  scenarioCard(it) {
    const st = it.status || "unknown";
    return `
      <article class="qh-scenario-card ${this.statusClass(st)}">
        <header class="qh-sc-card-head">
          <div>
            <span class="qh-sc-req">${this.esc(it.req_id)} · ${this.esc(it.title || "")}</span>
            <h3 class="qh-sc-title">${this.esc(it.business_flow || it.scenario)}</h3>
          </div>
          ${this.pill(st)}
        </header>
        <dl class="qh-sc-meta">
          ${it.persona ? `<div><dt>Persona</dt><dd>${this.esc(it.persona)}</dd></div>` : ""}
          ${it.steps_summary ? `<div><dt>Passos</dt><dd>${this.esc(it.steps_summary)}</dd></div>` : ""}
          ${it.expected_result ? `<div><dt>Resultado esperado</dt><dd>${this.esc(it.expected_result)}</dd></div>` : ""}
          ${it.file ? `<div><dt>Automação</dt><dd><code>${this.esc(it.file)}</code></dd></div>` : ""}
        </dl>
      </article>`;
  },

  renderE2ePanel() {
    const el = document.getElementById("e2ePanel");
    if (!el) return;
    const items = this.filteredByLayer("e2e");
    if (!items.length) {
      el.innerHTML = '<p class="pm-empty">Nenhum cenário E2E corresponde aos filtros.</p>';
      return;
    }
    const pass = items.filter((i) => i.status === "pass").length;
    const fail = items.filter((i) => i.status === "fail").length;
    const pending = items.length - pass - fail;
    const stats = `
      <div class="qh-e2e-stats">
        <span class="qh-stat pass">${pass} aprovados</span>
        <span class="qh-stat fail">${fail} falharam</span>
        <span class="qh-stat pending">${pending} pendentes / outros</span>
      </div>`;
    if (this.e2eView === "table") {
      const rows = items
        .map(
          (it) => `<tr>
          <td><strong>${this.esc(it.req_id)}</strong></td>
          <td>${this.esc(it.title || "—")}</td>
          <td>${this.esc(it.business_flow || it.scenario)}</td>
          <td>${it.persona ? this.esc(it.persona) : "—"}</td>
          <td>${it.file ? `<code class="qh-code">${this.esc(it.file)}</code>` : "—"}</td>
          <td>${this.pill(it.status)}</td>
        </tr>`
        )
        .join("");
      el.innerHTML = `${stats}
        <div class="pm-table-wrap qh-table-pro">
          <table class="qh-table">
            <thead><tr><th>REQ</th><th>Entrega</th><th>Fluxo</th><th>Persona</th><th>Automação</th><th>Status</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>`;
      return;
    }
    el.innerHTML = `${stats}<div class="qh-scenario-grid">${items.map((it) => this.scenarioCard(it)).join("")}</div>`;
  },

  renderLayerPanel(layer) {
    const el = document.getElementById(`layer_${layer}`);
    if (!el) return;
    const items = this.filteredByLayer(layer);
    if (!items.length) {
      el.innerHTML = `<p class="pm-empty">Nenhum cenário registrado para ${this.esc(this.layerLabel(layer))}.</p>`;
      return;
    }
    const rows = items
      .map(
        (it) => `<tr>
        <td><strong>${this.esc(it.req_id)}</strong></td>
        <td>${this.esc(it.title || "—")}</td>
        <td>${this.esc(it.business_flow || it.scenario)}</td>
        <td>${it.file ? `<code class="qh-code">${this.esc(it.file)}</code>` : "—"}</td>
        <td>${this.pill(it.status)}</td>
      </tr>`
      )
      .join("");
    el.innerHTML = `
      <h2>${this.esc(this.layerLabel(layer))}</h2>
      <div class="pm-table-wrap qh-table-pro">
        <table class="qh-table">
          <thead><tr><th>REQ</th><th>Entrega</th><th>Cenário</th><th>Automação</th><th>Status</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  },

  renderGaps() {
    const gaps = this.filteredGaps();
    const el = document.getElementById("gapsBox");
    if (!gaps.length) {
      el.innerHTML = `<p class="pm-empty">Nenhum risco aberto — todos os requisitos com cobertura adequada.</p>`;
      return;
    }
    el.innerHTML = `
      <div class="pm-table-wrap qh-table-pro">
        <table class="qh-table">
          <thead><tr><th>Requisito</th><th>Entrega</th><th>Prioridade</th><th>Lacunas</th><th>Impacto</th></tr></thead>
          <tbody>${gaps
            .map((g) => {
              const impact =
                g.priority === "P0" ? "Alto — bloqueia release" : g.priority === "P1" ? "Médio" : "Baixo";
              return `<tr>
                <td><strong>${this.esc(g.req_id)}</strong> <span class="qh-badge ${g.req_kind === "non_functional" ? "non_functional" : "functional"}">${g.req_kind === "non_functional" ? "NFR" : "Func."}</span></td>
                <td>${this.esc(g.title || "")}</td>
                <td>${this.esc(g.priority || "—")}</td>
                <td>${(g.gap_layers || []).map((x) => `<span class="qh-tag">${this.esc(x)}</span>`).join(" ")}</td>
                <td>${this.esc(impact)}</td>
              </tr>`;
            })
            .join("")}</tbody>
        </table>
      </div>`;
  },

  renderFilteredSections() {
    this.renderTestStatusChart();
    this.renderLayerHealthChart();
    this.renderExecSummary();
    this.renderRequirements();
    this.renderE2ePanel();
    this.PANEL_LAYERS.filter((l) => l !== "e2e").forEach((l) => this.renderLayerPanel(l));
    this.renderGaps();
    this.updateFilterCount();
  },

  renderAll() {
    this.renderHero();
    this.renderKpis();
    this.renderHealthGauge();
    this.renderTestStatusChart();
    this.renderCoverageChart();
    this.renderLayerHealthChart();
    this.renderExecSummary();
    this.renderLegend();
    this.renderRequirements();
    this.renderE2ePanel();
    this.PANEL_LAYERS.filter((l) => l !== "e2e").forEach((l) => this.renderLayerPanel(l));
    this.renderGaps();
    this.updateFilterCount();
    document.getElementById("builtAt").textContent = `Gerado: ${this.fmtDate(this.data.built_at)}`;
  },

  async init() {
    try {
      await this.load();
    } catch (e) {
      document.body.innerHTML = `<main class="pm-main"><p class="alert alert-error">Erro: ${this.esc(e.message)}. Rode <code>make quality-build</code>.</p></main>`;
      return;
    }
    this.initTheme();
    this.initTabs();
    this.initE2eToggle();
    this.initActions();
    this.initFilters();
    this.renderAll();
  },
};
