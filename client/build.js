#!/usr/bin/env bun
"use strict";

import { Glob } from "bun";
import { readFileSync, writeFileSync, existsSync, mkdirSync, copyFileSync, statSync } from "fs";
import { basename, join } from "path";
import yaml from "js-yaml";
import _ from "underscore";
import { minify as htmlMinify } from "html-minifier";

const DEV = process.env.GLEBOORU_DEV === "1";
const WATCH_POLL = process.env.GLEBOORU_WATCH_POLL === "1";

// Allow overriding output path for local testing
const outputPath = process.env.OUTPUT_PATH || "/var/www";

function baseUrl() {
    return process.env.BASE_URL ? process.env.BASE_URL : "/";
}

function readTextFile(path) {
    return readFileSync(path, "utf-8");
}

const sharedKeys = [
    "tag_name_regex",
    "tag_category_name_regex",
    "pool_name_regex",
    "pool_category_name_regex",
    "password_regex",
    "user_name_regex",
    "enable_safety",
    "contact_email",
    "can_send_mails",
    "privileges",
    "main_domain",
    "max_suggested_results",
];

const configName = DEV ? "config.dev.yaml" : "config.yaml";
const sitesName = DEV ? "sites.dev.yaml" : "sites.yaml";
const namesName = DEV ? "names.dev.yaml" : "names.yaml";

const serverConf = yaml.load(readTextFile(configName));
const sitesConf = yaml.load(readTextFile(sitesName));
const namesConf = yaml.load(readTextFile(namesName));

serverConf.main_domain = sitesConf.main_domain;
delete sitesConf.main_domain;
serverConf.sites = sitesConf;
serverConf.names = namesConf;

const vars = {};

for (const key of sharedKeys) {
    const camelKey = key.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
    vars[camelKey] = serverConf[key];
}

vars["newPostVisibilityThresholdMilliseconds"] =
    serverConf["new_post_visibility_threshold_minutes"] * 60 * 1000;

const webapp_icons = [
    { name: "android-chrome-192x192.png", size: 192 },
    { name: "apple-touch-icon.png", size: 180 },
    { name: "mstile-150x150.png", size: 150 },
];

const baseManifest = {
    icons: [
        {
            src: baseUrl() + "img/android-chrome-192x192.png",
            type: "image/png",
            sizes: "192x192",
        },
    ],
    start_url: baseUrl(),
    background_color: "#1a1a1a",
    display: "standalone",
};

// -------------------------------------------------

function minifyHtml(html) {
    return htmlMinify(html, {
        removeComments: true,
        collapseWhitespace: true,
    }).trim();
}

function bundleHtml(domain, data) {
    const siteUrl = `https://${domain}`;
    const metaDescription = data.meta_description || "";
    const metaKeywords = Array.isArray(data.meta_keywords) ? data.meta_keywords.join(", ") : (data.meta_keywords || "");

    let baseHtml = readTextFile("./html/index.html").replace(
        "<!-- Base HTML Placeholder -->",
        `<title>${data.name}</title><base id="base" href="${baseUrl()}"/><meta name="description" content="${metaDescription}"/>`
    );

    // Build SEO meta tags
    let seoTags = [];

    // Meta keywords (if provided)
    if (metaKeywords) {
        seoTags.push(`<meta name="keywords" content="${metaKeywords}"/>`);
    }

    // Open Graph tags for social sharing
    seoTags.push(`<meta property="og:title" content="${data.name}"/>`);
    seoTags.push(`<meta property="og:description" content="${metaDescription}"/>`);
    seoTags.push(`<meta property="og:type" content="website"/>`);
    seoTags.push(`<meta property="og:url" content="${siteUrl}/"/>`);
    seoTags.push(`<meta property="og:site_name" content="${data.name}"/>`);
    seoTags.push(`<meta property="og:image" content="${siteUrl}/img/android-chrome-192x192.png"/>`);

    // Twitter Card tags
    seoTags.push(`<meta name="twitter:card" content="summary"/>`);
    seoTags.push(`<meta name="twitter:title" content="${data.name}"/>`);
    seoTags.push(`<meta name="twitter:description" content="${metaDescription}"/>`);
    seoTags.push(`<meta name="twitter:image" content="${siteUrl}/img/android-chrome-192x192.png"/>`);

    baseHtml = baseHtml.replace("<!-- SEO Placeholder -->", seoTags.join(""));

    baseHtml = baseHtml.replaceAll(
        "$RAND$",
        Math.random().toString(36).substring(7)
    );

    baseHtml = baseHtml.replaceAll("$THEME_COLOR$", data.color);
    writeFileSync(
        `${outputPath}/${domain}/index.html`,
        minifyHtml(baseHtml)
    );
}

function bundleTemplates() {
    const glob = new Glob("./html/**/*.tpl");
    const files = [...glob.scanSync(".")];

    let compiledTemplateJs = [
        `'use strict';`,
        `let _ = require('underscore');`,
        `let templates = {};`,
    ];

    for (const file of files) {
        const name = basename(file, ".tpl").replace(/_/g, "-");
        const placeholders = [];
        let templateText = readTextFile(file);
        templateText = templateText.replace(/<%.*?%>/gi, (match) => {
            const ret = "%%%TEMPLATE" + placeholders.length;
            placeholders.push(match);
            return ret;
        });
        templateText = minifyHtml(templateText);
        templateText = templateText.replace(
            /%%%TEMPLATE(\d+)/g,
            (match, number) => {
                return placeholders[number];
            }
        );

        const functionText = _.template(templateText, {
            variable: "ctx",
        }).source;

        compiledTemplateJs.push(`templates['${name}'] = ${functionText};`);
    }
    compiledTemplateJs.push("module.exports = templates;");

    writeFileSync(
        "./js/.templates.autogen.js",
        compiledTemplateJs.join("\n")
    );
}

async function bundleCss(domain, data) {
    const stylus = (await import("stylus")).default;

    function readFile(file) {
        return readTextFile(file)
            .replace("$THEME_COLOR", data.color)
            .replace("$SITE", domain);
    }

    const mainStylesheet = "./main.styl";
    const outputDir = `${outputPath}/${domain}/css`;
    const appStylesheet = `${outputDir}/app.css`;

    let sourcemap = DEV ? { inline: true } : false;

    const css = stylus.render(readFile(mainStylesheet), {
        filename: mainStylesheet,
        sourcemap: sourcemap,
        compress: true,
    });

    writeFileSync(appStylesheet, css);

    const vendorStylesheet = `${outputDir}/vendor.css`;
    copyFileSync(
        "./node_modules/line-awesome/dist/line-awesome/css/line-awesome.min.css",
        vendorStylesheet
    );
}

// Cache for the built JS bundle
let cachedJsBundle = null;

async function buildJsBundle() {
    if (cachedJsBundle) {
        return cachedJsBundle;
    }

    const minify = !DEV;

    // Bundle app.js - Bun.build handles CommonJS and bundles all dependencies
    const appResult = await Bun.build({
        entrypoints: ["./js/main.js"],
        minify: minify,
        sourcemap: DEV ? "inline" : "none",
        target: "browser",
        format: "esm",
        define: {
            "process.env.NODE_ENV": minify ? '"production"' : '"development"',
        },
    });

    if (!appResult.success) {
        console.error("App JS build failed:");
        for (const log of appResult.logs) {
            console.error(log);
        }
        return null;
    }

    // Get the bundle content
    const output = appResult.outputs[0];
    cachedJsBundle = await output.text();
    return cachedJsBundle;
}

async function bundleJs(domain) {
    const outdir = `${outputPath}/${domain}/js`;

    const bundleContent = await buildJsBundle();
    if (!bundleContent) {
        return false;
    }

    // Write the cached bundle to this domain's output
    writeFileSync(`${outdir}/app.js`, bundleContent);

    // Create an empty vendor.js for backward compatibility (everything is now in app.js)
    writeFileSync(`${outdir}/vendor.js`, "/* Bundled into app.js */");

    return true;
}

function clearJsCache() {
    cachedJsBundle = null;
}

const environment = DEV ? "development" : "production";

function bundleConfig() {
    const config = {
        meta: {
            version: "latest",
            buildDate: new Date().toUTCString(),
        },
        environment: environment,
        sites: serverConf.sites,
        vars: vars,
    };

    writeFileSync("./js/.config.autogen.json", JSON.stringify(config));
}

function bundleBinaryAssets(domain) {
    const outputDir = `${outputPath}/${domain}`;
    const imgDir = `./sites/${domain}/img`;

    copyFileSync(`${imgDir}/favicon.png`, `${outputDir}/img/favicon.png`);

    copyFileSync(
        "./fonts/open_sans.woff2",
        `${outputDir}/fonts/open_sans.woff2`
    );

    const fontGlob = new Glob("./node_modules/line-awesome/dist/line-awesome/fonts/*.*");
    for (const file of fontGlob.scanSync(".")) {
        if (statSync(file).isDirectory()) {
            continue;
        }
        copyFileSync(file, join(`${outputDir}/fonts/`, basename(file)));
    }
}

function bundleRobotsTxt(domain) {
    const outputDir = `${outputPath}/${domain}`;
    const siteUrl = `https://${domain}`;

    const robotsTxt = `User-agent: *
Allow: /

# Block AI crawlers
User-agent: GPTBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: Google-Extended
Disallow: /

# Sitemap location
Sitemap: ${siteUrl}/sitemap.xml
`;

    writeFileSync(`${outputDir}/robots.txt`, robotsTxt);
}

async function bundleWebAppFiles(domain, data) {
    const outputDir = `${outputPath}/${domain}`;
    const imgDir = `./sites/${domain}/img`;

    const manifest = {
        ...baseManifest,
        name: data.name,
        theme_color: data.color,
    };

    writeFileSync(`${outputDir}/manifest.json`, JSON.stringify(manifest));

    // Try sharp first (much faster), fall back to jimp
    let sharp;
    try {
        sharp = (await import("sharp")).default;

        // Process all icons in parallel with sharp
        await Promise.all(
            webapp_icons.map(async (icon) => {
                await sharp(`${imgDir}/favicon.png`)
                    .resize(icon.size, icon.size, { fit: "contain" })
                    .toFile(join(`${outputDir}/img/`, icon.name));
            })
        );
    } catch (e) {
        // Fall back to jimp
        const Jimp = (await import("jimp")).default;

        await Promise.all(
            webapp_icons.map(async (icon) => {
                const file = await Jimp.read(`${imgDir}/favicon.png`);
                file.resize(icon.size, Jimp.AUTO, Jimp.RESIZE_BEZIER)
                    .write(join(`${outputDir}/img/`, icon.name));
            })
        );
    }
}

function makeOutputDirs(domain) {
    const dirs = [
        `${outputPath}/${domain}/css`,
        `${outputPath}/${domain}/fonts`,
        `${outputPath}/${domain}/img`,
        `${outputPath}/${domain}/js`,
    ];
    for (let dir of dirs) {
        if (!existsSync(dir)) {
            mkdirSync(dir, { mode: 0o755, recursive: true });
            console.info("Created directory: " + dir);
        }
    }
}

async function buildDomain(domain, data) {
    makeOutputDirs(domain);

    const tasks = [];

    if (!process.argv.includes("--no-css")) {
        tasks.push(bundleCss(domain, data));
    }
    if (!process.argv.includes("--no-html")) {
        tasks.push(Promise.resolve(bundleHtml(domain, data)));
        tasks.push(Promise.resolve(bundleRobotsTxt(domain)));
    }
    if (!process.argv.includes("--no-web-app-files")) {
        tasks.push(bundleWebAppFiles(domain, data));
    }
    if (!process.argv.includes("--no-binary-assets")) {
        tasks.push(Promise.resolve(bundleBinaryAssets(domain)));
    }
    if (!process.argv.includes("--no-js")) {
        tasks.push(bundleJs(domain));
    }

    await Promise.all(tasks);
    console.log(`Built ${domain}`);
}

async function watch() {
    const skipInit = process.argv.includes("--skip-init");

    // Initial build
    if (!skipInit) {
        const buildPromises = [];
        for (const [domain, data] of Object.entries(serverConf.sites)) {
            console.log(`Building ${domain}`);
            buildPromises.push(buildDomain(domain, data));
        }
        await Promise.all(buildPromises);
    }

    console.log("\nWatching for changes...");

    // Use Bun's native file watcher
    const { watch: fsWatch } = await import("fs");

    let debounceTimers = {};

    function debounce(key, fn, delay = 100) {
        if (debounceTimers[key]) {
            clearTimeout(debounceTimers[key]);
        }
        debounceTimers[key] = setTimeout(fn, delay);
    }

    // Watch templates
    fsWatch("./html", { recursive: true }, (eventType, filename) => {
        if (filename?.endsWith(".tpl")) {
            debounce("templates", async () => {
                try {
                    bundleTemplates();
                    clearJsCache(); // Clear cache to rebuild with new templates
                    for (const [domain, data] of Object.entries(serverConf.sites)) {
                        await bundleJs(domain);
                    }
                    console.log("Rebuilt templates and JS");
                } catch (e) {
                    console.error("Template build error:", e);
                }
            });
        }
    });

    // Watch CSS
    fsWatch("./css", { recursive: true }, (eventType, filename) => {
        if (filename?.endsWith(".styl")) {
            debounce("css", async () => {
                try {
                    for (const [domain, data] of Object.entries(serverConf.sites)) {
                        await bundleCss(domain, data);
                    }
                    console.log("Rebuilt CSS");
                } catch (e) {
                    console.error("CSS build error:", e);
                }
            });
        }
    });

    // Watch JS
    fsWatch("./js", { recursive: true }, (eventType, filename) => {
        if (filename?.endsWith(".js") && !filename?.includes(".autogen.")) {
            debounce("js", async () => {
                try {
                    clearJsCache(); // Clear cache to rebuild with changes
                    for (const [domain, data] of Object.entries(serverConf.sites)) {
                        await bundleJs(domain);
                    }
                    console.log("Rebuilt JS");
                } catch (e) {
                    console.error("JS build error:", e);
                }
            });
        }
    });
}

// -------------------------------------------------

async function main() {
    const startTime = performance.now();

    if (process.argv.includes("--watch")) {
        console.log(`Building for ${environment} environment and watching for changes\n`);
        bundleConfig();
        bundleTemplates();
        await watch();
    } else {
        console.log(`Building for "${environment}" environment\n`);
        bundleConfig();
        bundleTemplates();

        // Build all domains in parallel
        const buildPromises = [];
        for (const [domain, data] of Object.entries(serverConf.sites)) {
            console.log(`Building ${domain}`);
            buildPromises.push(buildDomain(domain, data));
        }

        await Promise.all(buildPromises);

        const endTime = performance.now();
        console.log(`\nBuild completed in ${((endTime - startTime) / 1000).toFixed(2)}s`);
    }
}

main().catch(console.error);
