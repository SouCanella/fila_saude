/** @type {import('@playwright/test').PlaywrightTestConfig} */
module.exports = {
  testDir: "tests/e2e/hub",
  timeout: 60000,
  retries: 1,
  use: {
    baseURL: process.env.HUB_BASE_URL || "http://127.0.0.1:8099/project-hub/",
    headless: true,
  },
};
