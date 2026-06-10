/**
 * Utilitários compartilhados — Project Hub
 */
const PanelUtils = {
  LOCALE: "pt-BR",
  THEME_KEY: "modelo-panel-theme",

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

  readTheme() {
    if (window.ModeloTheme?.read) return window.ModeloTheme.read();
    return localStorage.getItem(this.THEME_KEY) || "light";
  },

  applyTheme(pageId, theme) {
    const page = document.getElementById(pageId);
    if (page) page.setAttribute("data-theme", theme);
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.style.colorScheme = theme;
    if (window.ModeloTheme?.persist) window.ModeloTheme.persist(theme);
    else {
      try {
        localStorage.setItem(this.THEME_KEY, theme);
      } catch (_) {}
    }
  },

  initTheme(pageId, _storageKey, onChange) {
    const page = document.getElementById(pageId);
    if (!page) return;
    const saved = this.readTheme();
    this.applyTheme(pageId, saved);
    const btn = document.getElementById("themeToggle");
    if (!btn) return;
    const label = () => (page.getAttribute("data-theme") === "dark" ? "Modo claro" : "Modo escuro");
    btn.textContent = label();
    btn.onclick = () => {
      const next = page.getAttribute("data-theme") === "dark" ? "light" : "dark";
      this.applyTheme(pageId, next);
      btn.textContent = label();
      if (typeof onChange === "function") onChange(next);
    };
  },

  async copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  },
};
