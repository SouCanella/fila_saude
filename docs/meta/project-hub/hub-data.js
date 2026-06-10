/**
 * Carrega os 12 JSON do Project Hub via fetch (make hub-build).
 */
const HubData = {
  FILES: [
    "hub.data.json",
    "process.data.json",
    "quality.data.json",
    "security.data.json",
    "a11y.data.json",
    "design.data.json",
    "delivery.data.json",
    "learning.data.json",
    "journey.data.json",
    "tech_debt.data.json",
    "openapi.data.json",
    "release.data.json",
  ],
  cache: null,

  async load(force) {
    if (this.cache && !force) return this.cache;
    const entries = await Promise.all(
      this.FILES.map(async (file) => {
        const res = await fetch(`data/${file}?t=${Date.now()}`, { cache: "no-store" });
        if (!res.ok) throw new Error(`Não foi possível carregar data/${file} — rode make hub-build`);
        return [file, await res.json()];
      })
    );
    this.cache = Object.fromEntries(entries);
    return this.cache;
  },

  get(file) {
    return this.cache?.[file] ?? null;
  },

  hub() {
    return this.get("hub.data.json") || {};
  },
};
window.HubData = HubData;
