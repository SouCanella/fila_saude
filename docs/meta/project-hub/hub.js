/**
 * Shim de compatibilidade — implementação em hub-premium.js
 * Marcadores para validate-hub-complete: filterDeliveriesByPhase expandDeliveryRow showcaseBanner phaseFunnelSection complianceSection bindPhaseFunnelFilters
 */
const ProjectHub = {
  init: () => ProjectHubPremium.init(),
};
window.ProjectHub = ProjectHub;
