/**
 * Tema unificado — aplicar antes do paint (incluir no <head>).
 * Chave canônica: modelo-panel-theme
 */
(function () {
  const KEY = "modelo-panel-theme";
  const LEGACY = ["hub-theme", "pm-theme", "qh-theme"];

  function readTheme() {
    const params = new URLSearchParams(location.search);
    if (params.get("embed") === "1") {
      const urlTheme = params.get("theme");
      if (urlTheme === "dark" || urlTheme === "light") return urlTheme;
      try {
        const parentTheme = window.parent.document.getElementById("hubPage")?.getAttribute("data-theme");
        if (parentTheme === "dark" || parentTheme === "light") return parentTheme;
      } catch (_) {}
    }
    let v = localStorage.getItem(KEY);
    if (v === "dark" || v === "light") return v;
    for (let i = 0; i < LEGACY.length; i += 1) {
      v = localStorage.getItem(LEGACY[i]);
      if (v === "dark" || v === "light") {
        try {
          localStorage.setItem(KEY, v);
        } catch (_) {}
        return v;
      }
    }
    const urlTheme = params.get("theme");
    if (urlTheme === "dark" || urlTheme === "light") return urlTheme;
    return "light";
  }

  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.style.colorScheme = theme;
    const pageIds = ["hubPage", "pmPage", "qhPage"];
    for (let i = 0; i < pageIds.length; i += 1) {
      const el = document.getElementById(pageIds[i]);
      if (el) el.setAttribute("data-theme", theme);
    }
  }

  const theme = readTheme();
  apply(theme);

  window.ModeloTheme = {
    KEY,
    read: readTheme,
    apply,
    persist(theme) {
      if (theme !== "dark" && theme !== "light") return;
      try {
        localStorage.setItem(KEY, theme);
        for (let i = 0; i < LEGACY.length; i += 1) {
          localStorage.setItem(LEGACY[i], theme);
        }
      } catch (_) {}
      apply(theme);
    },
    parentTheme() {
      try {
        return window.parent.document.getElementById("hubPage")?.getAttribute("data-theme") || null;
      } catch (_) {
        return null;
      }
    },
  };

  document.addEventListener("DOMContentLoaded", function () {
    apply(readTheme());
  });
})();
