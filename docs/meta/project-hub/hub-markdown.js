/**
 * Markdown leve para o guia do Project Hub (sem dependências externas).
 */
const HubMarkdown = {
  esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },

  slugify(text) {
    return String(text)
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "") || "sec";
  },

  inline(text) {
    let s = this.esc(text);
    s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
      const url = this.resolveLink(href);
      const ext = url.endsWith(".md") ? ' class="hub-md-link-doc"' : "";
      return `<a href="${this.esc(url)}"${ext}>${label}</a>`;
    });
    return s;
  },

  resolveLink(href) {
    const h = String(href || "").trim();
    if (!h || h.startsWith("http") || h.startsWith("#") || h.startsWith("/")) return h;
    if (h.startsWith("project-hub/")) return `/${h}`;
    if (h.endsWith(".yaml") || h.endsWith(".md")) return `/${h.replace(/^\//, "")}`;
    return h;
  },

  isTableRow(line) {
    return /^\|.+\|$/.test(line.trim());
  },

  isTableSep(line) {
    return /^\|[\s:|-]+\|$/.test(line.trim());
  },

  renderTable(rows) {
    if (!rows.length) return "";
    const parse = (row) =>
      row
        .trim()
        .replace(/^\|/, "")
        .replace(/\|$/, "")
        .split("|")
        .map((c) => c.trim());
    const head = parse(rows[0]);
    const body = rows.slice(1);
    const th = head.map((c) => `<th>${this.inline(c)}</th>`).join("");
    const trs = body
      .map((row) => `<tr>${parse(row).map((c) => `<td>${this.inline(c)}</td>`).join("")}</tr>`)
      .join("");
    return `<div class="table-wrap hub-md-table"><table class="table"><thead><tr>${th}</tr></thead><tbody>${trs}</tbody></table></div>`;
  },

  render(md) {
    const lines = String(md || "").replace(/\r\n/g, "\n").split("\n");
    const toc = [];
    const blocks = [];
    let i = 0;
    const ids = new Map();

    const pushBlock = (html) => {
      if (html) blocks.push(html);
    };

    while (i < lines.length) {
      const line = lines[i];

      if (/^```/.test(line)) {
        const lang = line.slice(3).trim();
        i += 1;
        const code = [];
        while (i < lines.length && !/^```/.test(lines[i])) {
          code.push(lines[i]);
          i += 1;
        }
        i += 1;
        pushBlock(
          `<pre class="hub-md-pre"${lang ? ` data-lang="${this.esc(lang)}"` : ""}><code>${this.esc(code.join("\n"))}</code></pre>`
        );
        continue;
      }

      if (this.isTableRow(line) && i + 1 < lines.length && this.isTableSep(lines[i + 1])) {
        const rows = [line];
        i += 2;
        while (i < lines.length && this.isTableRow(lines[i])) {
          rows.push(lines[i]);
          i += 1;
        }
        pushBlock(this.renderTable(rows));
        continue;
      }

      const hm = /^(#{1,3})\s+(.+)$/.exec(line);
      if (hm) {
        const level = hm[1].length;
        const text = hm[2].trim();
        let id = this.slugify(text);
        const n = (ids.get(id) || 0) + 1;
        ids.set(id, n);
        if (n > 1) id = `${id}-${n}`;
        if (level <= 2) toc.push({ id, text, level });
        pushBlock(`<h${level + 1} id="${id}">${this.inline(text)}</h${level + 1}>`);
        i += 1;
        continue;
      }

      if (/^[-*]\s+/.test(line)) {
        const items = [];
        while (i < lines.length && /^[-*]\s+/.test(lines[i])) {
          items.push(`<li>${this.inline(lines[i].replace(/^[-*]\s+/, ""))}</li>`);
          i += 1;
        }
        pushBlock(`<ul class="hub-md-list">${items.join("")}</ul>`);
        continue;
      }

      if (/^\d+\.\s+/.test(line)) {
        const items = [];
        while (i < lines.length && /^\d+\.\s+/.test(lines[i])) {
          items.push(`<li>${this.inline(lines[i].replace(/^\d+\.\s+/, ""))}</li>`);
          i += 1;
        }
        pushBlock(`<ol class="hub-md-list">${items.join("")}</ol>`);
        continue;
      }

      if (!line.trim()) {
        i += 1;
        continue;
      }

      const para = [];
      while (i < lines.length && lines[i].trim() && !/^#{1,3}\s/.test(lines[i]) && !/^```/.test(lines[i]) && !/^[-*]\s+/.test(lines[i]) && !/^\d+\.\s+/.test(lines[i]) && !(this.isTableRow(lines[i]) && i + 1 < lines.length && this.isTableSep(lines[i + 1]))) {
        para.push(lines[i]);
        i += 1;
      }
      pushBlock(`<p>${this.inline(para.join(" "))}</p>`);
    }

    return { html: blocks.join("\n"), toc };
  },
};

window.HubMarkdown = HubMarkdown;
