#!/usr/bin/env node
/**
 * Smoke: monta Security/A11y/Design com dados JSON reais (sem browser).
 * Uso: node scripts/smoke-hub-modules.mjs [hub-dir]
 */
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const hubDir = path.resolve(process.argv[2] || path.join(root, "docs/meta/project-hub"));

const modules = [
  { name: "SecurityModule", file: "modules/security/security.js", data: "data/security.data.json", needle: "Checklist global" },
  { name: "A11yModule", file: "modules/a11y/a11y.js", data: "data/a11y.data.json", needle: "Acessibilidade" },
  { name: "DesignModule", file: "modules/design/design.js", data: "data/design.data.json", needle: "Design" },
];

function loadJson(rel) {
  const p = path.join(hubDir, rel);
  if (!fs.existsSync(p)) throw new Error(`JSON ausente: ${p}`);
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function runScript(rel) {
  const code = fs.readFileSync(path.join(hubDir, rel), "utf8");
  const sandbox = {
    window: {},
    PanelUtils: {
      esc(s) {
        return String(s ?? "")
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/"/g, "&quot;");
      },
    },
    fetch: async (url) => {
      const rel = String(url).split("?")[0].replace(/^.*\/data\//, "data/");
      return { ok: true, json: async () => loadJson(rel) };
    },
    console,
  };
  sandbox.window = sandbox;
  vm.runInNewContext(code, sandbox, { filename: rel });
  return sandbox.window;
}

function smokePremiumOverview(hubDir) {
  const files = [
    "hub.data.json",
    "journey.data.json",
    "security.data.json",
    "a11y.data.json",
    "design.data.json",
    "process.data.json",
    "quality.data.json",
    "learning.data.json",
    "release.data.json",
    "openapi.data.json",
  ];
  const cache = Object.fromEntries(files.map((f) => [f, loadJson(`data/${f}`)]));
  const premiumCode = fs.readFileSync(path.join(hubDir, "hub-premium.js"), "utf8");
  const sandbox = {
    window: {},
    HubData: { cache },
    document: {
      querySelector: () => null,
      querySelectorAll: () => [],
      getElementById: () => null,
      documentElement: { setAttribute: () => {} },
      head: { appendChild: () => {} },
    },
    localStorage: { getItem: () => null, setItem: () => {} },
    location: { hash: "#overview" },
    navigator: { clipboard: { writeText: async () => {} } },
    console,
    clearTimeout: () => {},
    setTimeout: (fn) => fn(),
  };
  sandbox.window = sandbox;
  vm.runInNewContext(premiumCode, sandbox, { filename: "hub-premium.js" });
  const html = sandbox.ProjectHubPremium.renderOverview();
  if (!html.includes("Funil de fases")) throw new Error("renderOverview sem funil");
  if (!html.includes("Entregas por card")) throw new Error("renderOverview sem entregas");
  const hub = cache["hub.data.json"];
  if (hub?.template?.is_upstream && hub?.template?.upstream_dev_mode && !html.includes("hub-spawn-banner")) {
    throw new Error("renderOverview sem hub-spawn-banner (upstream_dev_mode)");
  }
}

async function smokeProcessBoot(hubDir) {
  const legacyCode = fs.readFileSync(path.join(hubDir, "legacy-templates.js"), "utf8");
  const pmPath = path.join(path.dirname(hubDir), "process-metrics/process-metrics.js");
  const pmCode = fs.readFileSync(pmPath, "utf8");
  const data = loadJson("data/process.data.json");
  const stub = () => ({
    textContent: "",
    innerHTML: "",
    classList: { remove: () => {}, add: () => {}, toggle: () => {} },
    appendChild: () => {},
    addEventListener: () => {},
  });
  const sandbox = {
    window: {},
    document: {
      getElementById(id) {
        return sandbox._els[id] || null;
      },
      querySelector() {
        return null;
      },
      querySelectorAll() {
        return [];
      },
      documentElement: { setAttribute: () => {}, style: {} },
      head: { appendChild: () => {} },
      createElement: () => stub(),
    },
    localStorage: { getItem: () => null, setItem: () => {} },
    location: { hash: "#process" },
    console,
    clearTimeout: () => {},
    setTimeout: (fn) => fn(),
    _els: {},
  };
  sandbox.window = sandbox;
  const ctx = vm.createContext(sandbox);
  vm.runInContext(legacyCode, ctx, { filename: "legacy-templates.js" });
  for (const m of ctx.LegacyTemplates.processMain.matchAll(/id="([^"]+)"/g)) {
    sandbox._els[m[1]] = stub();
  }
  sandbox._els.pmPage = { setAttribute: () => {}, getAttribute: () => "light" };
  vm.runInContext(`${pmCode}\n;globalThis.ProcessMetrics = ProcessMetrics;`, ctx, { filename: "process-metrics.js" });
  ctx.ProcessMetrics.load = async () => {
    ctx.ProcessMetrics.data = data;
    return data;
  };
  await ctx.ProcessMetrics.boot();
}

let failed = 0;
try {
  smokePremiumOverview(hubDir);
  console.log("OK: ProjectHubPremium.renderOverview");
} catch (e) {
  console.error(`ERRO: ProjectHubPremium: ${e.message}`);
  failed += 1;
}

try {
  await smokeProcessBoot(hubDir);
  console.log("OK: ProcessMetrics.boot (hub embed)");
} catch (e) {
  console.error(`ERRO: ProcessMetrics.boot: ${e.message}`);
  failed += 1;
}

for (const mod of modules) {
  try {
    const win = runScript(mod.file);
    const M = win[mod.name];
    if (!M || typeof M.mount !== "function") {
      throw new Error(`${mod.name} ou mount ausente`);
    }
    const rootEl = { innerHTML: "" };
    await M.mount(rootEl);
    if (!rootEl.innerHTML.includes("pm-card")) {
      throw new Error(`${mod.name}: mount não gerou pm-card`);
    }
    if (!rootEl.innerHTML.includes(mod.needle)) {
      throw new Error(`${mod.name}: conteúdo esperado "${mod.needle}" ausente`);
    }
    console.log(`OK: ${mod.name}`);
  } catch (e) {
    console.error(`ERRO: ${mod.name}: ${e.message}`);
    failed += 1;
  }
}
process.exit(failed ? 1 : 0);
