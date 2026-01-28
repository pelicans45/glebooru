const { defineConfig } = require("@playwright/test");
const fs = require("fs");

const defaultBaseURL = fs.existsSync("/.dockerenv")
    ? "http://nginx:4000"
    : "http://boorudev:4000";
const baseURL = process.env.PLAYWRIGHT_BASE_URL || defaultBaseURL;
const chromiumPath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;

module.exports = defineConfig({
    testDir: "./tests/e2e",
    timeout: 60000,
    expect: { timeout: 10000 },
    reporter: [["list"], ["html", { open: "never" }]],
    use: {
        baseURL,
        headless: true,
        viewport: { width: 1280, height: 720 },
        screenshot: "only-on-failure",
        video: process.env.PLAYWRIGHT_VIDEO === "1"
            ? "retain-on-failure"
            : "off",
        trace: "retain-on-failure",
        launchOptions: chromiumPath
            ? { executablePath: chromiumPath }
            : undefined,
    },
});
