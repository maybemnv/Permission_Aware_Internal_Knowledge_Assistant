import { defineConfig, devices } from "@playwright/test";
import path from "path";

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  use: { baseURL: "http://127.0.0.1:3102", trace: "retain-on-failure" },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 900 } } },
    { name: "mobile", use: { ...devices["Desktop Chrome"], viewport: { width: 390, height: 844 }, isMobile: true } },
  ],
  webServer: [
    {
      command: "python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8102",
      cwd: path.resolve(__dirname, "../.."),
      url: "http://127.0.0.1:8102/health/ready",
      reuseExistingServer: true,
    },
    {
      command: "npm run start -- --hostname 127.0.0.1 --port 3102",
      cwd: __dirname,
      url: "http://127.0.0.1:3102",
      reuseExistingServer: true,
    },
  ],
});
