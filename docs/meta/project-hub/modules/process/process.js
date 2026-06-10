/**
 * Dashboard de métricas — process-metrics.data.json
 */
const ProcessMetrics = {
  data: null,
  calendarView: { year: new Date().getFullYear(), month: new Date().getMonth() },

  ACTIVITY_LABELS: {
    ideation: "Idealização",
    discovery: "Descoberta",
    planning_review: "Planejamento",
    bootstrap: "Bootstrap",
    design_mock: "Mocks HTML",
    design_approved: "Aprovação visual",
    architecture_baseline: "Arquitetura acordada",
    spec_refinement: "Refino specs",
    implementation: "Implementação",
    phase_retro: "Retro",
    refinement: "Refinamento",
    phase_delivery_start: "Início fase",
    phase_delivery_end: "Fim fase",
    mvp_planning_start: "Início planejamento MVP",
    mvp_planning_end: "Fim planejamento MVP",
    unknown: "A revisar",
  },

  COLORS: { human: "#3b82f6", ai: "#10b981", idle: "#cbd5e1", accent: "#6366f1" },
  LOCALE: "pt-BR",

  async load() {
    const res = await fetch("data/process.data.json");
    if (!res.ok) throw new Error("Não foi possível carregar process-metrics.data.json");
    this.data = await res.json();
    return this.data;
  },

  fmtSeconds(sec) {
    const s = Math.max(0, Number(sec) || 0);
    if (s < 60) return `${s}s`;
    const m = Math.floor(s / 60);
    if (m < 60) return `${m} min`;
    const h = Math.floor(m / 60);
    const rm = m % 60;
    return rm ? `${h}h ${rm}min` : `${h}h`;
  },

  fmtHours(sec) {
    const h = Number(sec) / 3600;
    return `${new Intl.NumberFormat(this.LOCALE, { maximumFractionDigits: 1 }).format(h)} h`;
  },

  parseDate(iso) {
    if (!iso) return null;
    const d = new Date(iso);
    return Number.isNaN(d.getTime()) ? null : d;
  },

  /** dd/mm/aaaa */
  fmtDate(iso) {
    const d = this.parseDate(iso);
    if (!d) return typeof iso === "string" ? iso : "—";
    return new Intl.DateTimeFormat(this.LOCALE, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }).format(d);
  },

  /** dd/mm/aaaa, HH:mm */
  fmtDateTime(iso) {
    const d = this.parseDate(iso);
    if (!d) return typeof iso === "string" ? iso : "—";
    return new Intl.DateTimeFormat(this.LOCALE, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(d);
  },

  /** yyyy-mm-dd → dd/mm/aaaa */
  fmtDayKey(isoDate) {
    if (!isoDate || !/^\d{4}-\d{2}-\d{2}/.test(isoDate)) return isoDate || "—";
    const [y, m, d] = isoDate.split("T")[0].split("-");
    return `${d}/${m}/${y}`;
  },

  /** Intervalo de entrega prevista (estatística) */
  fmtForecastDeliveryRange(startAt, endAt) {
    if (!endAt) return "—";
    const end = this.fmtDate(endAt);
    if (!startAt) return `${end} (est.)`;
    const start = this.fmtDate(startAt);
    const sk = String(startAt).slice(0, 10);
    const ek = String(endAt).slice(0, 10);
    if (sk === ek) return `${end} (est.)`;
    return `${start} → ${end} (est.)`;
  },

  secToDays(sec) {
    return Number(sec) / 86400;
  },

  fmtDays(sec, opts = {}) {
    const days = this.secToDays(sec);
    const n = new Intl.NumberFormat(this.LOCALE, {
      maximumFractionDigits: opts.maxFractionDigits ?? 1,
    }).format(days);
    const unit = days === 1 || days === 1.0 ? "dia" : "dias";
    return `${n} ${unit}`;
  },

  /** Exibe horas/min e dias quando ≥ 1 dia de esforço acumulado */
  fmtDuration(sec) {
    const s = Math.max(0, Number(sec) || 0);
    const timePart = this.fmtSeconds(s);
    if (this.secToDays(s) >= 1) {
      return `${timePart} (${this.fmtDays(s)})`;
    }
    return timePart;
  },

  fmtDurationPair(sec) {
    return `<span class="pm-dur-main">${this.fmtSeconds(sec)}</span>
      <span class="pm-dur-sub">${this.fmtDays(sec, { maxFractionDigits: 2 })}</span>`;
  },

  totals(block) {
    const human = block?.human_active_seconds || 0;
    const ai = block?.ai_execution_seconds || 0;
    const idle = block?.idle_seconds || 0;
    const total = human + ai + idle || 1;
    return { human, ai, idle, total };
  },

  effort(block) {
    const t = this.totals(block);
    return t.total;
  },

  badgeConfidence(c) {
    const map = {
      alta: "pm-badge-conf-alta",
      media: "pm-badge-conf-media",
      baixa: "pm-badge-conf-baixa",
    };
    return `<span class="pm-badge ${map[c] || ""}">${c || "—"}</span>`;
  },

  renderDonut(container, block, size = 200) {
    const { human, ai, idle, total } = this.totals(block);
    const r = size / 2 - 12;
    const cx = size / 2;
    const cy = size / 2;
    const circ = 2 * Math.PI * r;
    const slices = [
      { v: human, c: this.COLORS.human },
      { v: ai, c: this.COLORS.ai },
      { v: idle, c: this.COLORS.idle },
    ];
    let offset = 0;
    const paths = slices
      .map((s) => {
        const len = (s.v / total) * circ;
        const dash = `${len} ${circ - len}`;
        const rot = (offset / circ) * 360 - 90;
        offset += len;
        return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${s.c}" stroke-width="22"
          stroke-dasharray="${dash}" transform="rotate(${rot} ${cx} ${cy})"/>`;
      })
      .join("");
    container.innerHTML = `
      <svg class="pm-chart-svg" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}">
        <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#f1f5f9" stroke-width="22"/>
        ${paths}
        <text x="${cx}" y="${cy - 8}" text-anchor="middle" class="pm-donut-center">${this.fmtHours(total)}</text>
        <text x="${cx}" y="${cy + 8}" text-anchor="middle" fill="#64748b" font-size="10">${this.fmtDays(total)}</text>
        <text x="${cx}" y="${cy + 22}" text-anchor="middle" fill="#64748b" font-size="10">esforço</text>
      </svg>`;
  },

  renderLegend(el, block) {
    if (!el) return;
    const { human, ai, idle, total } = this.totals(block);
    const pct = (v) => ((v / total) * 100).toFixed(0);
    el.innerHTML = `
      <li><span class="pm-dot pm-seg-human"></span> Humano ${this.fmtSeconds(human)} (${pct(human)}%)</li>
      <li><span class="pm-dot pm-seg-ai"></span> IA ${this.fmtSeconds(ai)} (${pct(ai)}%)</li>
      <li><span class="pm-dot pm-seg-idle"></span> Ausente ${this.fmtSeconds(idle)} (${pct(idle)}%)</li>`;
  },

  renderEffortLegendKeysHtml() {
    return `<div class="pm-effort-legend-keys">
      <span><span class="pm-dot pm-seg-human"></span> Humano ativo</span>
      <span><span class="pm-dot pm-seg-ai"></span> IA (estimada)</span>
      <span><span class="pm-dot pm-seg-idle"></span> Ausente (gap entre rodadas)</span>
    </div>`;
  },

  renderGlobalEffortLegend(containerId, block, title) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `
      <h3>${title || "Legenda — esforço nas barras e donuts"}</h3>
      ${this.renderEffortLegendKeysHtml()}
      <ul class="pm-legend" id="${containerId}-list"></ul>`;
    this.renderLegend(document.getElementById(`${containerId}-list`), block || this.data.aggregates?.project || {});
  },

  renderHorizontalBars(container, items, maxVal) {
    if (!items.length) {
      container.innerHTML = '<p class="pm-empty">Sem dados.</p>';
      return;
    }
    const max = maxVal || Math.max(...items.map((i) => i.value), 1);
    container.innerHTML = items
      .map((item) => {
        const inner = item.segments
          ? item.segments
              .map(
                (s) =>
                  `<span class="pm-seg-${s.type}" style="width:${item.value ? ((s.v / item.value) * 100).toFixed(0) : 0}%"></span>`
              )
              .join("")
          : `<span class="pm-seg-human" style="width:100%"></span>`;
        return `
          <div class="pm-bar-row">
            <span>${item.label}</span>
            <div class="pm-bar-track pm-stacked">${inner}</div>
            <span class="pm-dur-cell">${this.fmtDurationPair(item.value)}</span>
          </div>`;
      })
      .join("");
  },

  renderByDayChart(container) {
    const days = this.data.aggregates?.by_day || [];
    if (!days.length) {
      container.innerHTML = '<p class="pm-empty">Sem rodadas com data.</p>';
      return;
    }
    const items = days.map((d) => ({
      label: this.fmtDayKey(d.date),
      value: d.total_seconds || 0,
      segments: [
        { type: "human", v: d.human_active_seconds || 0 },
        { type: "ai", v: d.ai_execution_seconds || 0 },
        { type: "idle", v: d.idle_seconds || 0 },
      ],
      sub: `${d.rounds_count || 0} rodada(s)`,
    }));
    const html = this.renderHorizontalBarsHtml(items);
    const calDays = this.data.aggregates?.calendar_project_span_days;
    const sub =
      calDays != null
        ? `<p class="pm-empty">Calendário do projeto: <strong>${calDays} ${calDays === 1 ? "dia" : "dias"}</strong> (primeira → última atividade registrada)</p>`
        : "";
    container.innerHTML = sub + html;
  },

  renderHorizontalBarsHtml(items) {
    const max = Math.max(...items.map((i) => i.value), 1);
    return items
      .map((item) => {
        const inner = item.segments
          ? item.segments
              .map(
                (s) =>
                  `<span class="pm-seg-${s.type}" style="width:${item.value ? ((s.v / item.value) * 100).toFixed(0) : 0}%"></span>`
              )
              .join("")
          : `<span class="pm-seg-human" style="width:100%"></span>`;
        return `
          <div class="pm-bar-row">
            <span>${item.label}<br><small class="pm-empty">${item.sub || ""}</small></span>
            <div class="pm-bar-track pm-stacked">${inner}</div>
            <span class="pm-dur-cell">${this.fmtDurationPair(item.value)}</span>
          </div>`;
      })
      .join("");
  },

  renderTimeline(container) {
    const ms = (this.data.milestones || []).filter((m) => m.started_at);
    if (!ms.length) {
      container.innerHTML = '<p class="pm-empty">Nenhum marco com data.</p>';
      return;
    }
    const dates = ms.flatMap((m) => [m.started_at, m.ended_at].filter(Boolean));
    const t0 = Math.min(...dates.map((d) => new Date(d).getTime()));
    const t1 = Math.max(...dates.map((d) => new Date(d).getTime()));
    const span = t1 - t0 || 1;
    const w = 640;
    const h = 24 + ms.length * 36;
    const rows = ms
      .map((m, i) => {
        const label = this.ACTIVITY_LABELS[m.activity] || m.activity;
        const x0 = ((new Date(m.started_at).getTime() - t0) / span) * (w - 120);
        const x1 = m.ended_at
          ? ((new Date(m.ended_at).getTime() - t0) / span) * (w - 120)
          : x0 + 20;
        const width = Math.max(8, x1 - x0);
        const y = 20 + i * 36;
        return `
          <text x="0" y="${y + 12}" font-size="11" fill="#64748b">${m.phase || ""} · ${label}</text>
          <rect x="110" y="${y}" width="${width}" height="18" rx="4" fill="${this.COLORS.accent}" opacity="0.85"/>
        `;
      })
      .join("");
    const labelStart = this.fmtDate(new Date(t0).toISOString());
    const labelEnd = this.fmtDate(new Date(t1).toISOString());
    const spanDays = this.fmtDays((span / 1000));
    container.innerHTML = `
      <svg class="pm-chart-svg" viewBox="0 0 ${w} ${h + 28}" width="100%">${rows}
        <text x="110" y="${h + 16}" font-size="10" fill="#64748b">${labelStart}</text>
        <text x="${w - 80}" y="${h + 16}" font-size="10" fill="#64748b" text-anchor="end">${labelEnd}</text>
        <text x="${w / 2}" y="${h + 28}" font-size="10" fill="#64748b" text-anchor="middle">Extensão: ${spanDays}</text>
      </svg>`;
  },

  renderContextBanners() {
    const el = document.getElementById("contextBanners");
    if (!el) return;
    const gates = this.data.gates || {};
    const fc = this.data.forecasts || {};
    const parts = [];
    if (gates.has_frontend === false) {
      parts.push(
        '<div class="pm-banner pm-banner-info">Projeto <strong>sem front</strong> — gate de design aprovado não se aplica; mocks HTML são opcionais.</div>'
      );
    }
    if (fc.enabled === false) {
      const reason = fc.disabled_reason || "mvp_planning_incomplete";
      const hint =
        reason === "mvp_planning_incomplete"
          ? "Previsões <strong>(est.)</strong> ficam desabilitadas até <code>mvp_planning.status: complete</code> e backlog com cards."
          : `Previsões <strong>(est.)</strong> indisponíveis (<code>${this.esc(reason)}</code>).`;
      parts.push(`<div class="pm-banner pm-banner-muted">${hint}</div>`);
    }
    el.innerHTML = parts.join("");
  },

  renderDeliveryHighlight() {
    const el = document.getElementById("deliveryHighlight");
    if (!el) return;
    const fc = this.data.forecasts || {};
    const at = fc.enabled !== false ? fc.project_delivery_forecast_at : null;
    if (!at) {
      el.innerHTML = `
        <p class="pm-delivery-hero-empty">
          <strong>Conclusão prevista do backlog</strong> — indisponível até haver planejamento MVP
          (<code>mvp_planning</code> completo) e itens pendentes no backlog para o modelo estatístico.
        </p>`;
      el.classList.add("pm-delivery-hero--muted");
      return;
    }
    el.classList.remove("pm-delivery-hero--muted");
    const end = this.parseDate(at);
    const schedule = fc.delivery_schedule || [];
    const pendingCards = (fc.cards || []).length;
    const pendingPhases = (fc.phases || []).length;
    let countdownHtml = "";
    if (end) {
      const now = new Date();
      now.setHours(0, 0, 0, 0);
      const endDay = new Date(end);
      endDay.setHours(0, 0, 0, 0);
      const diffDays = Math.round((endDay - now) / 86400000);
      if (diffDays > 0) {
        countdownHtml = `
          <p class="pm-delivery-hero-countdown">≈ ${diffDays} ${diffDays === 1 ? "dia" : "dias"}</p>
          <p class="pm-delivery-hero-countdown-sub">até a última entrega prevista (est.)</p>`;
      } else if (diffDays === 0) {
        countdownHtml = `
          <p class="pm-delivery-hero-countdown">Hoje (est.)</p>
          <p class="pm-delivery-hero-countdown-sub">data prevista para encerrar o backlog</p>`;
      } else {
        countdownHtml = `
          <p class="pm-delivery-hero-countdown">${Math.abs(diffDays)} d atrás (est.)</p>
          <p class="pm-delivery-hero-countdown-sub">previsão já passou — recalibre o modelo</p>`;
      }
    }
    el.innerHTML = `
      <div class="pm-delivery-hero-inner">
        <div>
          <p class="pm-delivery-hero-label">Conclusão prevista do backlog</p>
          <p class="pm-delivery-hero-date">${this.fmtDate(at)}<span class="pm-delivery-hero-badge">est.</span></p>
          <p class="pm-delivery-hero-meta">
            ${this.fmtDateTime(at)} · ${schedule.length} item(ns) no encadeamento
            · ${pendingCards} card(s) · ${pendingPhases} fase(s) pendentes
          </p>
          <p class="pm-empty" style="margin-top:0.75rem;font-size:0.8rem">
            Projeção estatística do método Modelo — não é data de negócio, SLA nem promessa ao cliente.
          </p>
        </div>
        <div class="pm-delivery-hero-aside">${countdownHtml}</div>
      </div>`;
  },

  renderKpis() {
    const agg = this.data.aggregates || {};
    const proj = this.totals(agg.project || {});
    const fc = this.data.forecasts || {};
    const nextPhases = (fc.phases || []).length;
    const nextCards = (fc.cards || []).length;
    const estTotal = (fc.phases || []).reduce((s, p) => s + (p.estimated_active_seconds || 0), 0);

    const calDays = agg.calendar_project_span_days;
    const milestoneDays = agg.calendar_from_milestones_days;

    document.getElementById("kpiGrid").innerHTML = `
      <div class="pm-kpi">
        <div class="pm-kpi-label">Início do projeto</div>
        <div class="pm-kpi-value" style="font-size:1.1rem">${this.fmtDate(this.data.project_started_at)}</div>
        <div class="pm-kpi-sub">${this.fmtDateTime(this.data.project_started_at)}</div>
      </div>
      <div class="pm-kpi">
        <div class="pm-kpi-label">Calendário (projeto)</div>
        <div class="pm-kpi-value">${calDays != null ? `${calDays} d` : "—"}</div>
        <div class="pm-kpi-sub">dias com atividade registrada</div>
      </div>
      <div class="pm-kpi">
        <div class="pm-kpi-label">Esforço registrado</div>
        <div class="pm-kpi-value">${this.fmtHours(proj.total)}</div>
        <div class="pm-kpi-sub">${this.fmtDays(proj.total)} · humano + IA + gaps</div>
      </div>
      <div class="pm-kpi">
        <div class="pm-kpi-label">Humano ativo</div>
        <div class="pm-kpi-value" style="color:var(--pm-human)">${this.fmtHours(proj.human)}</div>
      </div>
      <div class="pm-kpi">
        <div class="pm-kpi-label">IA (estimada)</div>
        <div class="pm-kpi-value" style="color:var(--pm-ai)">${this.fmtHours(proj.ai)}</div>
      </div>
      <div class="pm-kpi">
        <div class="pm-kpi-label">Marcos (calendário)</div>
        <div class="pm-kpi-value">${milestoneDays != null ? `${milestoneDays} d` : "—"}</div>
        <div class="pm-kpi-sub">${this.fmtDuration(agg.calendar_from_milestones_seconds || 0)}</div>
      </div>
      <div class="pm-kpi pm-kpi--linked-delivery">
        <div class="pm-kpi-label">Entrega MVP (est.)</div>
        <div class="pm-kpi-value" style="font-size:1.1rem;color:var(--pm-planned)">${
          fc.project_delivery_forecast_at ? this.fmtDate(fc.project_delivery_forecast_at) : "—"
        }</div>
        <div class="pm-kpi-sub">ver destaque acima · não é SLA</div>
      </div>
      <div class="pm-kpi">
        <div class="pm-kpi-label">Esforço pendente (est.)</div>
        <div class="pm-kpi-value">${this.fmtHours(estTotal)}</div>
        <div class="pm-kpi-sub">${this.fmtDays(estTotal)} · ${nextPhases} fase(s) · ${nextCards} card(s)</div>
      </div>
      <div class="pm-kpi">
        <div class="pm-kpi-label">Revisão pendente</div>
        <div class="pm-kpi-value">${agg.rounds_needing_review || 0}</div>
        <div class="pm-kpi-sub">rodadas needs_review</div>
      </div>`;
  },

  renderOverview() {
    const agg = this.data.aggregates || {};
    this.renderGlobalEffortLegend(
      "globalEffortLegend",
      agg.project,
      "Legenda — barras empilhadas, donut e médias por atividade"
    );
    this.renderDonut(document.getElementById("overviewDonut"), agg.project, 220);
    this.renderLegend(document.getElementById("overviewLegend"), agg.project);

    const byPhase = agg.by_phase || {};
    const phaseItems = Object.keys(byPhase)
      .sort()
      .map((p) => {
        const t = this.totals(byPhase[p]);
        return {
          label: p,
          value: t.total,
          segments: [
            { type: "human", v: t.human },
            { type: "ai", v: t.ai },
            { type: "idle", v: t.idle },
          ],
        };
      });
    this.renderHorizontalBars(document.getElementById("phaseBarsChart"), phaseItems);

    const byAct = agg.by_activity || {};
    const actItems = Object.entries(byAct)
      .map(([a, b]) => ({
        label: this.ACTIVITY_LABELS[a] || a,
        value: this.effort(b),
      }))
      .sort((a, b) => b.value - a.value);
    this.renderHorizontalBars(document.getElementById("activityBarsChart"), actItems);

    this.renderByDayChart(document.getElementById("byDayChart"));
    this.renderMilestones(document.getElementById("milestonesTable"));
  },

  renderMilestones(container) {
    const list = this.data.milestones || [];
    if (!list.length) {
      container.innerHTML = '<p class="pm-empty">Nenhum marco.</p>';
      return;
    }
    const rows = list
      .map((m) => {
        const label = this.ACTIVITY_LABELS[m.activity] || m.activity;
        const dur =
          m.started_at && m.ended_at
            ? this.fmtDuration(
                Math.max(0, (new Date(m.ended_at) - new Date(m.started_at)) / 1000)
              )
            : "—";
        return `<tr>
          <td><strong>${m.phase || "—"}</strong></td>
          <td>${label}</td>
          <td>${this.fmtDateTime(m.started_at)}</td>
          <td>${m.ended_at ? this.fmtDateTime(m.ended_at) : "—"}</td>
          <td>${dur}</td>
          <td>${m.notes || ""}</td>
        </tr>`;
      })
      .join("");
    container.innerHTML = `<table class="table"><thead><tr>
      <th>Fase</th><th>Atividade</th><th>Início</th><th>Fim</th><th>Duração</th><th>Notas</th>
    </tr></thead><tbody>${rows}</tbody></table>`;
  },

  renderPhaseView(phase) {
    const agg = this.data.aggregates?.by_phase?.[phase] || {
      human_active_seconds: 0,
      ai_execution_seconds: 0,
      idle_seconds: 0,
    };
    this.renderGlobalEffortLegend("phaseEffortLegend", agg, `Legenda — esforço na fase ${phase}`);
    document.getElementById("phaseTitle").textContent = `Fase ${phase}`;
    this.renderDonut(document.getElementById("phaseDonut"), agg, 200);
    this.renderLegend(document.getElementById("phaseLegend"), agg);

    const rounds = (this.data.rounds || []).filter((r) => r.phase === phase);
    const byCard = {};
    rounds.forEach((r) => {
      const c = r.card_id || "(sem card)";
      if (!byCard[c]) byCard[c] = { human: 0, ai: 0, idle: 0 };
      byCard[c].human += r.human_active_seconds || 0;
      byCard[c].ai += r.ai_execution_seconds || 0;
      byCard[c].idle += r.idle_before_seconds || 0;
    });
    const cardItems = Object.entries(byCard).map(([id, t]) => ({
      label: id,
      value: t.human + t.ai + t.idle,
      segments: [
        { type: "human", v: t.human },
        { type: "ai", v: t.ai },
        { type: "idle", v: t.idle },
      ],
    }));
    this.renderHorizontalBars(document.getElementById("phaseCardsChart"), cardItems);

    const cardRows = Object.entries(byCard)
      .map(
        ([id, t]) =>
          `<tr><td><strong>${id}</strong></td><td>${this.fmtDuration(t.human)}</td>
          <td>${this.fmtDuration(t.ai)}</td><td>${this.fmtDuration(t.idle)}</td></tr>`
      )
      .join("");
    document.getElementById("phaseCardsTable").innerHTML = cardRows
      ? `<table class="table"><thead><tr><th>Card</th><th>Humano</th><th>IA</th><th>Gap</th></tr></thead><tbody>${cardRows}</tbody></table>`
      : '<p class="pm-empty">Sem rodadas.</p>';

    const ms = (this.data.milestones || []).filter((m) => m.phase === phase);
    let cal = 0;
    ms.forEach((m) => {
      if (m.started_at && m.ended_at) {
        cal += Math.max(0, new Date(m.ended_at) - new Date(m.started_at)) / 1000;
      }
    });
    const sum = this.effort(agg);
    document.getElementById("phaseCompare").innerHTML = `
      <h2>Calendário vs esforço registrado</h2>
      <div class="pm-grid-2" style="margin-top:1rem">
        <div><span class="pm-kpi-label">Calendário (marcos)</span>
          <div class="pm-kpi-value" style="font-size:1.25rem">${this.fmtDays(cal)}</div>
          <div class="pm-kpi-sub">${this.fmtDuration(cal)}</div></div>
        <div><span class="pm-kpi-label">Soma rodadas</span>
          <div class="pm-kpi-value" style="font-size:1.25rem">${this.fmtDays(sum)}</div>
          <div class="pm-kpi-sub">${this.fmtDuration(sum)}</div></div>
      </div>`;
  },

  renderReportMeta() {
    const rep = this.data.report || {};
    const fc = this.data.forecasts || {};
    const name = rep.project_name || "Projeto";
    const nameEl = document.getElementById("reportProjectName");
    const subEl = document.getElementById("reportSubtitle");
    if (nameEl) {
      nameEl.textContent = rep.title ? `${rep.title} — ${name}` : `Relatório — ${name}`;
    }
    if (subEl && rep.subtitle) {
      subEl.textContent = rep.subtitle;
    }
    const longText =
      rep.forecast_disclaimer_long ||
      fc.disclaimer_long ||
      document.getElementById("disclaimerLongText")?.textContent;
    const shortText =
      rep.forecast_disclaimer_short || fc.disclaimer_short || "";
    const longEl = document.getElementById("disclaimerLongText");
    if (longEl && longText) longEl.textContent = longText;
    const sched = document.getElementById("scheduleDisclaimer");
    const fore = document.getElementById("forecastDisclaimer");
    if (sched && shortText) sched.textContent = shortText;
    if (fore && shortText) fore.textContent = shortText;
  },

  initTheme() {
    const embedded = !!document.getElementById("hubPage");
    const page = document.getElementById("pmPage");
    const saved = window.ModeloTheme?.read?.() || localStorage.getItem("modelo-panel-theme") || localStorage.getItem("pm-theme") || "light";
    page?.setAttribute("data-theme", saved);
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
    btn.addEventListener("click", () => {
      const next = page.getAttribute("data-theme") === "dark" ? "light" : "dark";
      if (window.ModeloTheme?.persist) window.ModeloTheme.persist(next);
      else {
        page.setAttribute("data-theme", next);
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("pm-theme", next);
        localStorage.setItem("modelo-panel-theme", next);
      }
      btn.textContent = label();
      this.renderDeliveryHighlight();
      this.renderOverview();
      this.renderGantt();
      this.renderCalendar();
      const ph = document.getElementById("phaseSelect")?.value;
      if (ph) this.renderPhaseView(ph);
    });
  },

  getThemeColors() {
    const dark = document.getElementById("pmPage")?.getAttribute("data-theme") === "dark";
    return {
      muted: dark ? "#94a3b8" : "#64748b",
      strong: dark ? "#e2e8f0" : "#0f172a",
      grid: dark ? "#334155" : "#e2e8f0",
      track: dark ? "#1e293b" : "#f1f5f9",
    };
  },

  esc(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  },

  renderActivityAverages() {
    const list = this.data.aggregates?.activity_averages || [];
    const el = document.getElementById("activityAverages");
    if (!el) return;
    if (!list.length) {
      el.innerHTML = '<p class="pm-empty">Sem rodadas para calcular médias.</p>';
      return;
    }
    el.innerHTML = list
      .map((a) => {
        const pct = (v, t) => (t ? (100 * v) / t : 0);
        const t = a.avg_total_seconds || 1;
        return `
      <div class="pm-avg-card">
        <h4>${this.esc(a.label || a.activity)}</h4>
        <div class="pm-avg-meta">${a.rounds_count} rodada(s)</div>
        <div class="pm-stacked pm-stacked-lg">
          <span class="pm-seg-human" style="width:${pct(a.avg_human_seconds, t)}%"></span>
          <span class="pm-seg-ai" style="width:${pct(a.avg_ai_seconds, t)}%"></span>
          <span class="pm-seg-idle" style="width:${pct(a.avg_idle_seconds, t)}%"></span>
        </div>
        <p><strong>Média/rodada:</strong> ${this.fmtDuration(a.avg_total_seconds)}</p>
        <p class="pm-empty">Humano ${this.fmtDuration(a.avg_human_seconds)} · IA ${this.fmtDuration(a.avg_ai_seconds)}</p>
      </div>`;
      })
      .join("");
  },

  ganttLabelText(task, maxLen = 44) {
    const raw = String(task?.label || "").trim();
    if (raw.length <= maxLen) return raw;
    return `${raw.slice(0, maxLen - 1)}…`;
  },

  renderGantt() {
    const g = this.data.gantt || {};
    const tasks = g.tasks || [];
    const container = document.getElementById("ganttChart");
    if (!container) return;
    if (!tasks.length) {
      container.innerHTML = '<p class="pm-empty">Sem tarefas no cronograma.</p>';
      return;
    }
    const t0 = new Date(g.range_start).getTime();
    const t1 = new Date(g.range_end).getTime();
    const span = t1 - t0 || 1;
    const colors = this.getThemeColors();
    const longest = Math.max(...tasks.map((t) => String(t.label || "").length), 24);
    const labelW = Math.min(340, Math.max(200, Math.round(longest * 6.4)));
    const chartW = 760;
    const rowH = 40;
    const w = labelW + chartW + 48;
    const h = 52 + tasks.length * rowH;
    const x0 = labelW;
    const weekTicks = 8;
    const ticks = Array.from({ length: weekTicks + 1 }, (_, i) => {
      const x = x0 + (i / weekTicks) * chartW;
      const t = new Date(t0 + (span * i) / weekTicks);
      return `<text x="${x}" y="32" font-size="10" fill="${colors.muted}" text-anchor="middle">${this.fmtDate(t.toISOString())}</text>
        <line x1="${x}" y1="40" x2="${x}" y2="${h - 12}" stroke="${colors.grid}" stroke-width="1"/>`;
    }).join("");
    let labelRows = "";
    let chartRows = "";
    tasks.forEach((task, i) => {
      const y = 48 + i * rowH;
      const py = y + 10;
      const barH = 14;
      const toX = (iso) => {
        if (!iso) return null;
        return x0 + ((new Date(iso).getTime() - t0) / span) * chartW;
      };
      let bars = "";
      const ps = toX(task.planned_start);
      const pe = toX(task.planned_end);
      const isStat = task.planned_date_kind === "statistical_projection" || task.status === "forecast";
      if (ps != null && pe != null && isStat) {
        bars += `<rect x="${ps}" y="${py}" width="${Math.max(8, pe - ps)}" height="${barH}" rx="5" fill="url(#patPlanned)" stroke="#a78bfa" stroke-width="1"/>`;
      } else if (ps != null && pe != null) {
        bars += `<rect x="${ps}" y="${py + barH + 4}" width="${Math.max(4, pe - ps)}" height="5" rx="2" fill="${colors.muted}" opacity="0.3"/>`;
      }
      const as = toX(task.actual_start);
      const ae = toX(task.actual_end);
      if (as != null && ae != null) {
        bars += `<rect x="${as}" y="${py}" width="${Math.max(8, ae - as)}" height="${barH}" rx="5" fill="url(#gradActual)"/>`;
      }
      const icon = task.status === "done" ? "✓" : task.status === "forecast" ? "◎ est." : "▶";
      const sub =
        task.date_source === "card_dates"
          ? "card opened/done"
          : task.date_source === "statistical_projection"
            ? "projeção estatística"
            : task.date_source || "";
      const label = this.ganttLabelText(task);
      const fullLabel = `${icon} ${task.label || ""}`;
      labelRows += `
        <g>
          <title>${this.esc(fullLabel)}</title>
          <text x="8" y="${y + 18}" font-size="11" fill="${colors.strong}" font-weight="600">${this.esc(`${icon} ${label}`)}</text>
          <text x="8" y="${y + 32}" font-size="9" fill="${colors.muted}">${this.esc(task.group)} · ${this.esc(sub)}</text>
        </g>`;
      chartRows += `${bars}<line x1="${x0}" y1="${y + rowH - 4}" x2="${w - 24}" y2="${y + rowH - 4}" stroke="${colors.grid}" stroke-width="1"/>`;
    });
    container.innerHTML = `
      <svg class="pm-gantt-svg pm-chart-svg" viewBox="0 0 ${w} ${h}" width="100%">
        <defs>
          <linearGradient id="gradActual" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#10b981"/>
          </linearGradient>
          <pattern id="patPlanned" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="8" stroke="#a78bfa" stroke-width="4"/>
          </pattern>
          <clipPath id="ganttLabelClip"><rect x="0" y="36" width="${labelW - 10}" height="${h - 36}"/></clipPath>
        </defs>
        <line x1="${x0}" y1="40" x2="${x0}" y2="${h - 12}" stroke="${colors.grid}" stroke-width="1.5"/>
        <g clip-path="url(#ganttLabelClip)">${labelRows}</g>
        <g>${chartRows}</g>
        <g>${ticks}</g>
      </svg>`;
  },

  initCalendarMonth() {
    const ev = this.data.calendar_events || [];
    const gantt = this.data.gantt;
    const start = this.data.project_started_at || ev[0]?.date || gantt?.range_start;
    if (start) {
      const d = this.parseDate(start.includes("T") ? start : `${start}T12:00:00`);
      if (d) this.calendarView = { year: d.getFullYear(), month: d.getMonth() };
    }
  },

  renderCalendar() {
    const el = document.getElementById("deliveryCalendar");
    if (!el) return;
    const { year, month } = this.calendarView;
    const label = new Intl.DateTimeFormat(this.LOCALE, { month: "long", year: "numeric" }).format(
      new Date(year, month, 1)
    );
    document.getElementById("calMonthLabel").textContent =
      label.charAt(0).toUpperCase() + label.slice(1);
    const events = this.data.calendar_events || [];
    const byDate = {};
    events.forEach((e) => {
      if (e.date) {
        if (!byDate[e.date]) byDate[e.date] = [];
        byDate[e.date].push(e);
      }
    });
    const first = new Date(year, month, 1);
    const startPad = first.getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const prevDays = new Date(year, month, 0).getDate();
    const todayKey = new Date().toISOString().slice(0, 10);
    const weekdays = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
    let html = weekdays.map((d) => `<div class="pm-cal-head">${d}</div>`).join("");
    const totalCells = Math.ceil((startPad + daysInMonth) / 7) * 7;
    for (let cell = 0; cell < totalCells; cell++) {
      let dayNum;
      let dateKey;
      let other = false;
      if (cell < startPad) {
        dayNum = prevDays - startPad + cell + 1;
        const pm = month === 0 ? 11 : month - 1;
        const py = month === 0 ? year - 1 : year;
        dateKey = `${py}-${String(pm + 1).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
        other = true;
      } else if (cell >= startPad + daysInMonth) {
        dayNum = cell - startPad - daysInMonth + 1;
        const nm = month === 11 ? 0 : month + 1;
        const ny = month === 11 ? year + 1 : year;
        dateKey = `${ny}-${String(nm + 1).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
        other = true;
      } else {
        dayNum = cell - startPad + 1;
        dateKey = `${year}-${String(month + 1).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
      }
      const evs = byDate[dateKey] || [];
      const eventsHtml = evs
        .slice(0, 3)
        .map((e) => {
          const stat = e.date_kind === "statistical_projection" || e.kind === "delivery_forecast";
          const cls = stat ? "pm-ev-forecast" : "pm-ev-actual";
          const tip = stat
            ? "Projeção estatística — não é data de negócio"
            : "Entrega rastreada no processo";
          return `<span class="pm-cal-event ${cls}" title="${this.esc(tip)}">${this.esc(e.title)}</span>`;
        })
        .join("");
      const more = evs.length > 3 ? `<span class="pm-cal-event">+${evs.length - 3}</span>` : "";
      html += `<div class="pm-cal-day${other ? " other-month" : ""}${dateKey === todayKey ? " today" : ""}">
        <div class="pm-cal-num">${dayNum}</div>${eventsHtml}${more}</div>`;
    }
    el.innerHTML =
      `<div class="pm-cal-scroll" role="region" aria-label="Calendário — deslize horizontalmente no celular">` +
      `<div class="pm-cal-grid">${html}</div></div>`;
  },

  bindCalendarNav() {
    document.getElementById("calPrev")?.addEventListener("click", () => {
      if (this.calendarView.month === 0) {
        this.calendarView.month = 11;
        this.calendarView.year -= 1;
      } else this.calendarView.month -= 1;
      this.renderCalendar();
    });
    document.getElementById("calNext")?.addEventListener("click", () => {
      if (this.calendarView.month === 11) {
        this.calendarView.month = 0;
        this.calendarView.year += 1;
      } else this.calendarView.month += 1;
      this.renderCalendar();
    });
  },

  renderForecastDeliverySchedule() {
    const el = document.getElementById("forecastDeliverySchedule");
    const mvpEl = document.getElementById("forecastMvpDate");
    if (!el) return;
    const fc = this.data.forecasts || {};
    const schedule = fc.delivery_schedule || [];

    if (mvpEl) {
      if (fc.project_delivery_forecast_at) {
        mvpEl.innerHTML = `Mesma data do <strong>destaque no topo do relatório</strong>: ${this.fmtDate(
          fc.project_delivery_forecast_at
        )} (est.) · ${this.fmtDateTime(fc.project_delivery_forecast_at)}`;
      } else {
        mvpEl.innerHTML =
          '<span class="pm-empty">Sem datas previstas — conclua o planejamento MVP ou registre histórico para o modelo estatístico.</span>';
      }
    }

    if (!schedule.length) {
      el.innerHTML = '<p class="pm-empty">Nenhuma entrega pendente com data projetada.</p>';
      return;
    }
    const rows = schedule
      .map(
        (row) => `<tr>
          <td><strong>${this.esc(row.label)}</strong><br><small class="pm-empty">${this.esc(row.id)}</small></td>
          <td>${this.esc(row.phase || "—")}</td>
          <td>${row.kind === "card" ? "Card" : row.kind === "phase" ? "Fase" : this.esc(row.kind)}</td>
          <td>${this.fmtForecastDeliveryRange(row.forecast_start_at, row.forecast_end_at)}</td>
          <td>${row.forecast_delivery_date ? this.fmtDayKey(row.forecast_delivery_date) : "—"}</td>
        </tr>`
      )
      .join("");
    el.innerHTML = `<table>
      <thead><tr>
        <th>Item</th><th>Fase</th><th>Tipo</th><th>Período previsto (est.)</th><th>Data fim (est.)</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
  },

  renderForecast() {
    const fc = this.data.forecasts || {};
    const method =
      (fc.methodology || "Sem histórico suficiente para previsão.") +
      (fc.disclaimer_short ? ` ${fc.disclaimer_short}` : "");
    document.getElementById("forecastMethod").textContent = method;
    const phasesEl = document.getElementById("forecastPhases");
    const cardsEl = document.getElementById("forecastCards");
    const compareEl = document.getElementById("forecastCompareChart");

    if (fc.enabled === false) {
      this.renderForecastDeliverySchedule();
      const msg =
        fc.disabled_reason === "mvp_planning_incomplete"
          ? "Complete o planejamento MVP e registre cards no backlog para habilitar projeções estatísticas."
          : "Não há itens pendentes ou histórico suficiente para projeção.";
      phasesEl.innerHTML = `<p class="pm-empty">${this.esc(msg)}</p>`;
      cardsEl.innerHTML = "";
      if (compareEl) compareEl.innerHTML = "";
      return;
    }

    this.renderForecastDeliverySchedule();

    if (!(fc.phases || []).length) {
      phasesEl.innerHTML = '<p class="pm-empty">Nenhuma fase pendente no planejamento.</p>';
    } else {
      phasesEl.innerHTML = fc.phases
        .map(
          (p) => `
        <div class="pm-forecast-card">
          <h4>${p.phase} ${this.badgeConfidence(p.confidence)}</h4>
          <p>${p.pending_cards_count} card(s) pendente(s)</p>
          <div class="pm-stacked pm-stacked-lg" style="margin:0.75rem 0">
            <span class="pm-seg-human" style="width:55%"></span>
            <span class="pm-seg-ai" style="width:30%"></span>
            <span class="pm-seg-idle" style="width:15%"></span>
          </div>
          <p class="pm-forecast-date-line"><strong>Entrega prevista (est.):</strong> ${this.fmtForecastDeliveryRange(
            p.forecast_delivery_start_at,
            p.forecast_delivery_end_at
          )}</p>
          <p><strong>Esforço ativo est.:</strong> ${this.fmtDuration(p.estimated_active_seconds)}</p>
          <p><strong>Duração calendário (est.):</strong> ${this.fmtDuration(p.estimated_calendar_seconds)}
            (${p.estimated_calendar_days != null ? this.fmtDays(p.estimated_calendar_seconds) : "—"})</p>
          <p class="pm-empty">Não é data de negócio · base: ${p.based_on_completed_phases} fase(s) concluída(s)</p>
        </div>`
        )
        .join("");
    }

    if (!(fc.cards || []).length) {
      cardsEl.innerHTML = '<p class="pm-empty">Nenhum card pendente no backlog.</p>';
    } else {
      cardsEl.innerHTML = fc.cards
        .map(
          (c) => `
        <div class="pm-forecast-card">
          <h4>${c.card_id} — ${c.title || ""} ${this.badgeConfidence(c.confidence)}</h4>
          <p>${c.phase} · status <strong>${c.status}</strong></p>
          <div class="pm-bar-row" style="margin-top:0.5rem">
            <span>Estimativa</span>
            <div class="pm-bar-track"><span class="pm-seg-ai" style="width:70%"></span></div>
            <span class="pm-dur-cell">${this.fmtDurationPair(c.estimated_active_seconds)}</span>
          </div>
          <p class="pm-forecast-date-line"><strong>Entrega prevista (est.):</strong> ${this.fmtForecastDeliveryRange(
            c.forecast_delivery_start_at,
            c.forecast_delivery_end_at
          )}</p>
          <p class="pm-empty">Duração calendário (est.): ${this.fmtDuration(c.estimated_calendar_seconds)} · não é SLA</p>
        </div>`
        )
        .join("");
    }

    const compare = [];
    const byPhase = this.data.aggregates?.by_phase || {};
    Object.keys(byPhase)
      .filter((p) => p.startsWith("FASE-"))
      .forEach((p) => {
        compare.push({
          label: `${p} (real)`,
          value: this.effort(byPhase[p]),
          kind: "real",
        });
      });
    (fc.phases || []).forEach((p) => {
      compare.push({
        label: `${p.phase} (prev.)`,
        value: p.estimated_active_seconds || 0,
        kind: "forecast",
      });
    });
    if (!compare.length) {
      compareEl.innerHTML = '<p class="pm-empty">Sem fases para comparar.</p>';
    } else {
      this.renderHorizontalBars(compareEl, compare);
    }
  },

  renderLedger(filterPhase) {
    let rounds = [...(this.data.rounds || [])].reverse();
    if (filterPhase && filterPhase !== "all") {
      rounds = rounds.filter((r) => r.phase === filterPhase);
    }
    const tbody = document.getElementById("ledgerBody");
    if (!rounds.length) {
      tbody.innerHTML = '<tr><td colspan="8">Nenhuma rodada.</td></tr>';
      return;
    }
    tbody.innerHTML = rounds
      .map((r) => {
        const cls = r.needs_review ? "metrics-review" : "";
        const label = this.ACTIVITY_LABELS[r.activity] || r.activity;
        return `<tr class="${cls}">
          <td><code>${r.id || "—"}</code></td>
          <td>${this.fmtDateTime(r.at)}</td>
          <td>${r.phase || "—"}</td>
          <td>${label}</td>
          <td>${r.card_id || "—"}</td>
          <td>${this.fmtDuration(r.human_active_seconds)}</td>
          <td>${this.fmtDuration(r.ai_execution_seconds)}</td>
          <td>${this.fmtDuration(r.idle_before_seconds)}</td>
        </tr>`;
      })
      .join("");
  },

  initTabs() {
    document.querySelectorAll(".pm-tabs [data-tab]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const tab = btn.getAttribute("data-tab");
        document.querySelectorAll(".pm-tabs [data-tab]").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".pm-panel").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        document.querySelector(`.pm-panel[data-panel="${tab}"]`)?.classList.add("active");
      });
    });
  },

  async boot() {
    await this.load();
    const agg = this.data.aggregates || {};
    const alertEl = document.getElementById("metricsAlert");
    const reviewRounds = (this.data.rounds || []).filter((r) => r.needs_review);
    if (alertEl && reviewRounds.length) {
      const ids = reviewRounds.map((r) => r.id || "?").join(", ");
      alertEl.innerHTML = `<strong>Revisão pendente no registro de tempo</strong> — ${reviewRounds.length} rodada(s) com <code>needs_review: true</code> em <code>docs/meta/process-timeline.yaml</code> (${this.esc(ids)}). Corrija os campos e defina <code>needs_review: false</code>. Ver módulo <a href="../project-hub/guide.html">Processo no Project Hub</a> (Ledger).`;
      alertEl.classList.remove("hidden");
    }

    this.initTheme();
    this.renderReportMeta();
    this.renderContextBanners();
    this.initCalendarMonth();
    this.renderDeliveryHighlight();
    this.renderKpis();
    this.renderOverview();
    this.renderActivityAverages();
    this.renderGantt();
    this.renderCalendar();
    this.bindCalendarNav();
    this.renderForecast();

    const phaseSelect = document.getElementById("phaseSelect");
    const phases = Object.keys(agg.by_phase || {}).sort();
    if (!phases.includes("SETUP")) phases.unshift("SETUP");
    phaseSelect.innerHTML = [...new Set(phases)]
      .map((p) => `<option value="${p}">${p}</option>`)
      .join("");

    const ledgerFilter = document.getElementById("ledgerPhaseFilter");
    phases.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p;
      opt.textContent = p;
      ledgerFilter.appendChild(opt);
    });

    const refreshPhase = () => this.renderPhaseView(phaseSelect.value);
    phaseSelect.addEventListener("change", refreshPhase);
    refreshPhase();

    const refreshLedger = () => this.renderLedger(ledgerFilter.value);
    ledgerFilter.addEventListener("change", refreshLedger);
    refreshLedger();

    document.getElementById("builtAt").textContent = this.fmtDateTime(this.data.built_at);
    this.initTabs();
  },
};
