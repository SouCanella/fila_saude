/**
 * FilaSaúde Brasil — padrões a11y para mockups (replicar no app real).
 * Skip link, focus trap modal, tabs ARIA, toast live region.
 */
(function (global) {
  const FOCUSABLE =
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

  let modalTrigger = null;
  let modalKeyHandler = null;

  function getFocusables(root) {
    return [...root.querySelectorAll(FOCUSABLE)].filter(
      (el) => !el.hasAttribute("disabled") && el.getAttribute("aria-hidden") !== "true"
    );
  }

  function setupSkipLink() {
    if (document.getElementById("skip-to-main")) return;
    const skip = document.createElement("a");
    skip.id = "skip-to-main";
    skip.className = "skip-link";
    skip.href = "#main-content";
    skip.textContent = "Ir para o conteúdo";
    document.body.insertBefore(skip, document.body.firstChild);
  }

  function ensureMainLandmark() {
    const main = document.querySelector(".main");
    if (main) main.id = "main-content";
  }

  function setupModal() {
    const backdrop = document.getElementById("hospital-modal");
    if (!backdrop) return;
    backdrop.setAttribute("role", "dialog");
    backdrop.setAttribute("aria-modal", "true");
    backdrop.setAttribute("aria-labelledby", "modal-title");
    const closeBtn = backdrop.querySelector("[data-close]");
    if (closeBtn) closeBtn.setAttribute("aria-label", "Fechar");
  }

  function openModalFocus(trigger) {
    modalTrigger = trigger || document.activeElement;
    const backdrop = document.getElementById("hospital-modal");
    if (!backdrop || !backdrop.classList.contains("open")) return;
    const modal = backdrop.querySelector(".modal");
    if (!modal) return;
    const focusables = getFocusables(modal);
    (focusables[0] || closeBtnFallback(backdrop)).focus();

    if (modalKeyHandler) document.removeEventListener("keydown", modalKeyHandler);
    modalKeyHandler = (e) => {
      if (!backdrop.classList.contains("open")) return;
      if (e.key === "Escape") {
        e.preventDefault();
        closeModal();
        return;
      }
      if (e.key !== "Tab") return;
      const items = getFocusables(modal);
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", modalKeyHandler);
  }

  function closeBtnFallback(backdrop) {
    return backdrop.querySelector("[data-close]") || backdrop;
  }

  function closeModal() {
    const backdrop = document.getElementById("hospital-modal");
    if (backdrop) backdrop.classList.remove("open");
    if (modalKeyHandler) {
      document.removeEventListener("keydown", modalKeyHandler);
      modalKeyHandler = null;
    }
    if (modalTrigger && typeof modalTrigger.focus === "function") {
      modalTrigger.focus();
    }
    modalTrigger = null;
  }

  function activateTab(tab, tabs, panels) {
    tabs.forEach((t) => {
      const selected = t === tab;
      t.classList.toggle("active", selected);
      t.setAttribute("aria-selected", selected ? "true" : "false");
      t.tabIndex = selected ? 0 : -1;
    });
    panels.forEach((p) => {
      const show = p.id === "tab-" + tab.dataset.tab;
      p.classList.toggle("active", show);
      p.hidden = !show;
    });
  }

  function setupTabs() {
    const tablist = document.querySelector('.tabs[role="tablist"]');
    if (!tablist) return;
    const tabs = [...tablist.querySelectorAll('[role="tab"]')];
    if (!tabs.length) return;
    const panels = tabs
      .map((t) => document.getElementById(t.getAttribute("aria-controls")))
      .filter(Boolean);

    tabs.forEach((tab, i) => {
      tab.tabIndex = tab.classList.contains("active") ? 0 : -1;
      tab.setAttribute("aria-selected", tab.classList.contains("active") ? "true" : "false");
      const panel = panels[i];
      if (panel) panel.hidden = !tab.classList.contains("active");

      tab.onclick = () => activateTab(tab, tabs, panels);
      tab.onkeydown = (e) => {
        let idx = tabs.indexOf(document.activeElement);
        if (idx < 0) idx = tabs.indexOf(tab);
        if (e.key === "ArrowRight") {
          e.preventDefault();
          tabs[(idx + 1) % tabs.length].focus();
        } else if (e.key === "ArrowLeft") {
          e.preventDefault();
          tabs[(idx - 1 + tabs.length) % tabs.length].focus();
        } else if (e.key === "Home") {
          e.preventDefault();
          tabs[0].focus();
        } else if (e.key === "End") {
          e.preventDefault();
          tabs[tabs.length - 1].focus();
        } else if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activateTab(tab, tabs, panels);
        }
      };
    });
  }

  function setupToast() {
    const t = document.querySelector(".toast");
    if (!t) return;
    t.setAttribute("role", "status");
    t.setAttribute("aria-live", "polite");
    t.setAttribute("aria-atomic", "true");
  }

  function enhanceChrome() {
    const nav = document.querySelector(".navbar");
    if (nav && !nav.getAttribute("aria-label")) {
      nav.setAttribute("aria-label", "Navegação principal");
    }
    const themeBtn = document.querySelector('[data-action="theme"]');
    if (themeBtn && !themeBtn.getAttribute("aria-label")) {
      themeBtn.setAttribute("aria-label", "Alternar tema claro ou escuro");
    }
  }

  function init() {
    setupSkipLink();
    ensureMainLandmark();
    enhanceChrome();
    setupModal();
    setupTabs();
    setupToast();
  }

  global.FilaSaudeA11y = { init, openModalFocus, closeModal };
})(window);

document.addEventListener("DOMContentLoaded", () => {
  if (window.FilaSaudeA11y) window.FilaSaudeA11y.init();
});
