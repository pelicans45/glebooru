#!/usr/bin/env bun
/**
 * Build output verification tests
 * Run with: bun test build.test.js
 */

import { describe, test, expect, beforeAll } from "bun:test";
import { existsSync, readFileSync, statSync } from "fs";
import { execSync } from "child_process";
import path from "path";

const TEST_OUTPUT = "/tmp/glebooru-build-test";
const DEV_OUTPUT = "/tmp/glebooru-build-test-dev";

// Build before running tests
beforeAll(async () => {
    console.log("Building production...");
    execSync(`rm -rf ${TEST_OUTPUT}`, { stdio: "inherit" });
    execSync(`OUTPUT_PATH=${TEST_OUTPUT} bun build.js`, {
        cwd: import.meta.dir,
        stdio: "inherit",
    });

    console.log("Building development...");
    execSync(`rm -rf ${DEV_OUTPUT}`, { stdio: "inherit" });
    execSync(`OUTPUT_PATH=${DEV_OUTPUT} GLEBOORU_DEV=1 bun build.js`, {
        cwd: import.meta.dir,
        stdio: "inherit",
    });
}, 60000);

describe("Production Build", () => {
    const domain = "jej.lol"; // Use first production domain

    describe("Directory Structure", () => {
        test("creates all required directories", () => {
            expect(existsSync(`${TEST_OUTPUT}/${domain}/css`)).toBe(true);
            expect(existsSync(`${TEST_OUTPUT}/${domain}/js`)).toBe(true);
            expect(existsSync(`${TEST_OUTPUT}/${domain}/img`)).toBe(true);
            expect(existsSync(`${TEST_OUTPUT}/${domain}/fonts`)).toBe(true);
        });
    });

    describe("JavaScript Bundle", () => {
        test("app.js exists and has content", () => {
            const appJs = `${TEST_OUTPUT}/${domain}/js/app.js`;
            expect(existsSync(appJs)).toBe(true);
            const stat = statSync(appJs);
            expect(stat.size).toBeGreaterThan(100000); // Should be > 100KB
        });

        test("app.js is minified (no large whitespace blocks)", () => {
            const appJs = readFileSync(`${TEST_OUTPUT}/${domain}/js/app.js`, "utf-8");
            // Minified code shouldn't have multiple consecutive newlines
            expect(appJs).not.toMatch(/\n\s*\n\s*\n/);
        });

        test("app.js contains expected modules", () => {
            const appJs = readFileSync(`${TEST_OUTPUT}/${domain}/js/app.js`, "utf-8");
            // Check for key library markers that survive minification
            expect(appJs).toContain("Cookie"); // js-cookie
            expect(appJs).toContain("DOMPurify"); // dompurify
        });

        test("vendor.js exists (compatibility stub)", () => {
            const vendorJs = `${TEST_OUTPUT}/${domain}/js/vendor.js`;
            expect(existsSync(vendorJs)).toBe(true);
        });

        test("app.js includes vendor dependencies (bundled together)", () => {
            const appJs = readFileSync(`${TEST_OUTPUT}/${domain}/js/app.js`, "utf-8");
            // These libraries should be bundled in
            expect(appJs).toContain("DOMPurify"); // dompurify
            expect(appJs).toContain("superagent");
        });
    });

    describe("CSS Bundle", () => {
        test("app.css exists and has content", () => {
            const appCss = `${TEST_OUTPUT}/${domain}/css/app.css`;
            expect(existsSync(appCss)).toBe(true);
            const stat = statSync(appCss);
            expect(stat.size).toBeGreaterThan(10000); // Should be > 10KB
        });

        test("app.css is compressed", () => {
            const appCss = readFileSync(`${TEST_OUTPUT}/${domain}/css/app.css`, "utf-8");
            // Compressed CSS shouldn't have many newlines
            const newlineCount = (appCss.match(/\n/g) || []).length;
            expect(newlineCount).toBeLessThan(100);
        });

        test("vendor.css exists (line-awesome)", () => {
            const vendorCss = `${TEST_OUTPUT}/${domain}/css/vendor.css`;
            expect(existsSync(vendorCss)).toBe(true);
            const content = readFileSync(vendorCss, "utf-8");
            // Line Awesome uses .la class prefix
            expect(content).toContain(".la");
            expect(content).toContain("font-family");
        });
    });

    describe("HTML", () => {
        test("index.html exists", () => {
            expect(existsSync(`${TEST_OUTPUT}/${domain}/index.html`)).toBe(true);
        });

        test("index.html is minified", () => {
            const html = readFileSync(`${TEST_OUTPUT}/${domain}/index.html`, "utf-8");
            // Should be on one or few lines
            const lines = html.split("\n").filter(l => l.trim());
            expect(lines.length).toBeLessThan(5);
        });

        test("index.html contains required elements", () => {
            const html = readFileSync(`${TEST_OUTPUT}/${domain}/index.html`, "utf-8");
            expect(html).toContain("<title>");
            expect(html).toContain('charset="utf-8"');
            expect(html).toContain("app.js");
            expect(html).toContain("app.css");
            expect(html).toContain("vendor.js");
            expect(html).toContain("vendor.css");
        });
    });

    describe("Web App Files", () => {
        test("manifest.json exists and is valid JSON", () => {
            const manifestPath = `${TEST_OUTPUT}/${domain}/manifest.json`;
            expect(existsSync(manifestPath)).toBe(true);
            const manifest = JSON.parse(readFileSync(manifestPath, "utf-8"));
            expect(manifest).toHaveProperty("name");
            expect(manifest).toHaveProperty("icons");
            expect(manifest).toHaveProperty("start_url");
        });

        test("favicon.png exists", () => {
            expect(existsSync(`${TEST_OUTPUT}/${domain}/img/favicon.png`)).toBe(true);
        });

        test("webapp icons are generated", () => {
            expect(existsSync(`${TEST_OUTPUT}/${domain}/img/android-chrome-192x192.png`)).toBe(true);
            expect(existsSync(`${TEST_OUTPUT}/${domain}/img/apple-touch-icon.png`)).toBe(true);
        });
    });

    describe("Fonts", () => {
        test("open_sans.woff2 exists", () => {
            expect(existsSync(`${TEST_OUTPUT}/${domain}/fonts/open_sans.woff2`)).toBe(true);
        });

        test("line-awesome fonts are copied", () => {
            const fonts = ["la-brands-400.woff2", "la-regular-400.woff2", "la-solid-900.woff2"];
            for (const font of fonts) {
                expect(existsSync(`${TEST_OUTPUT}/${domain}/fonts/${font}`)).toBe(true);
            }
        });
    });

    describe("Multiple Domains", () => {
        test("all production domains are built", () => {
            const expectedDomains = [
                "jej.lol",
                "lole.meme",
                "glegle.gallery",
                "bury.pink",
                "flube.supply",
                "spikedog.school",
                "yosho.io",
                "politics.lol",
                "boymoders.com"
            ];
            for (const d of expectedDomains) {
                expect(existsSync(`${TEST_OUTPUT}/${d}/js/app.js`)).toBe(true);
            }
        });

        test("all domains have identical JS bundles", () => {
            const domains = ["jej.lol", "lole.meme", "glegle.gallery"];
            const firstBundle = readFileSync(`${TEST_OUTPUT}/${domains[0]}/js/app.js`, "utf-8");
            for (const d of domains.slice(1)) {
                const bundle = readFileSync(`${TEST_OUTPUT}/${d}/js/app.js`, "utf-8");
                expect(bundle).toBe(firstBundle);
            }
        });
    });
});

describe("Development Build", () => {
    const domain = "booru"; // Dev domain

    test("creates dev domain directories", () => {
        expect(existsSync(`${DEV_OUTPUT}/${domain}/js`)).toBe(true);
        expect(existsSync(`${DEV_OUTPUT}/${domain}/css`)).toBe(true);
    });

    test("app.js includes sourcemaps in dev mode", () => {
        const appJs = readFileSync(`${DEV_OUTPUT}/${domain}/js/app.js`, "utf-8");
        expect(appJs).toContain("//# sourceMappingURL=data:application/json");
    });

    test("dev bundle is larger than production (due to sourcemaps)", () => {
        const devSize = statSync(`${DEV_OUTPUT}/${domain}/js/app.js`).size;
        const prodSize = statSync(`${TEST_OUTPUT}/jej.lol/js/app.js`).size;
        expect(devSize).toBeGreaterThan(prodSize);
    });
});

describe("Generated Files", () => {
    test(".templates.autogen.js exists and contains templates", () => {
        const templatesPath = path.join(import.meta.dir, "js/.templates.autogen.js");
        expect(existsSync(templatesPath)).toBe(true);
        const content = readFileSync(templatesPath, "utf-8");
        expect(content).toContain("templates[");
        expect(content).toContain("module.exports = templates");
        // Check for some known templates
        expect(content).toContain("'login'");
        expect(content).toContain("'top-navigation'");
    });

    test(".config.autogen.json exists and is valid", () => {
        const configPath = path.join(import.meta.dir, "js/.config.autogen.json");
        expect(existsSync(configPath)).toBe(true);
        const config = JSON.parse(readFileSync(configPath, "utf-8"));
        expect(config).toHaveProperty("meta");
        expect(config).toHaveProperty("environment");
        expect(config).toHaveProperty("sites");
        expect(config).toHaveProperty("vars");
    });
});

describe("Bundle Functionality", () => {
    test("JS bundle has valid structure", () => {
        const appJs = readFileSync(`${TEST_OUTPUT}/jej.lol/js/app.js`, "utf-8");
        // Bundle should start with var/const/let or IIFE pattern
        expect(appJs).toMatch(/^(var|const|let|\()/);
        // Bundle should be reasonably sized
        expect(appJs.length).toBeGreaterThan(100000);
        // Bundle should end properly (not truncated)
        expect(appJs.trim()).toMatch(/[;})(\]]$/);
    });

    test("templates are properly compiled functions", () => {
        const templatesPath = path.join(import.meta.dir, "js/.templates.autogen.js");
        const content = readFileSync(templatesPath, "utf-8");
        // Templates should be function definitions
        expect(content).toMatch(/templates\['[\w-]+'\]\s*=\s*function/);
    });

    test("templates autogen can be required without errors", async () => {
        // This tests that the compiled templates are syntactically valid
        const templatesPath = path.join(import.meta.dir, "js/.templates.autogen.js");
        const templates = require(templatesPath);
        expect(templates).toBeDefined();
        expect(typeof templates).toBe("object");
        // Should have known templates
        expect(templates["login"]).toBeDefined();
        expect(typeof templates["login"]).toBe("function");
        expect(templates["top-navigation"]).toBeDefined();
        expect(typeof templates["top-navigation"]).toBe("function");
    });

    test("config autogen has correct structure", () => {
        const configPath = path.join(import.meta.dir, "js/.config.autogen.json");
        const config = require(configPath);
        // Environment depends on which build ran last
        expect(["production", "development"]).toContain(config.environment);
        expect(config.meta.version).toBe("latest");
        expect(config.vars).toHaveProperty("privileges");
    });
});

describe("Build Performance", () => {
    test("production build completes under 5 seconds", () => {
        const start = performance.now();
        execSync(`rm -rf /tmp/glebooru-perf-test && OUTPUT_PATH=/tmp/glebooru-perf-test bun build.js --no-web-app-files`, {
            cwd: import.meta.dir,
            stdio: "pipe",
        });
        const duration = performance.now() - start;
        expect(duration).toBeLessThan(5000);
    });

    test("dev build completes under 2 seconds", () => {
        const start = performance.now();
        execSync(`rm -rf /tmp/glebooru-perf-test-dev && OUTPUT_PATH=/tmp/glebooru-perf-test-dev GLEBOORU_DEV=1 bun build.js --no-web-app-files`, {
            cwd: import.meta.dir,
            stdio: "pipe",
        });
        const duration = performance.now() - start;
        expect(duration).toBeLessThan(2000);
    });
});
