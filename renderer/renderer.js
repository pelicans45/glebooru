const express = require("express");
const puppeteer = require("puppeteer");

const app = express();
const port = 3000;

const cache = new Map();
const CACHE_DURATION_MS = 60 * 60 * 1000;

let browserInstance = null;

async function getBrowser() {
    if (!browserInstance || !browserInstance.isConnected()) {
        console.log("Launching new browser instance...");
        try {
            browserInstance = await puppeteer.launch({
                headless: true,
                args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            });
            browserInstance.on("disconnected", () => {
                console.log("Browser disconnected.");
                browserInstance = null;
            });
            console.log("Browser launched successfully.");
        } catch (error) {
            console.error("Failed to launch browser:", error);
            browserInstance = null;
            throw error;
        }
    }
    return browserInstance;
}

app.get("/render/*", async (req, res) => {
    const urlToRender = req.url.substring("/render/".length);

    if (!urlToRender || !urlToRender.startsWith("http")) {
        console.error(`Invalid URL received: ${urlToRender}`);
        return res.status(400).send("A valid URL starting with http(s) to render is required after /render/.");
    }

    console.log(`Rendering request for: ${urlToRender}`);

    const cachedItem = cache.get(urlToRender);
    if (cachedItem && Date.now() < cachedItem.expiry) {
        console.log(`Serving from cache: ${urlToRender}`);
        res.setHeader("X-Render-Cache", "hit");
        return res.send(cachedItem.html);
    }

    let page = null;
    try {
        const browser = await getBrowser();
        if (!browser) {
            return res.status(503).send("Renderer service unavailable (browser launch failed).");
        }
        page = await browser.newPage();

        page.on("console", (msg) => console.log(`Browser Console [${msg.type()}]: ${msg.text()}`));
        page.on("pageerror", (error) => console.error(`page.on("pageerror"):`, error));
        page.on("error", (error) => console.error(`page.on("error"):`, error));
        page.on("requestfailed", (request) =>
            console.warn(`Browser request failed: ${request.url()} (${request.failure()?.errorText || "N/A"})`)
        );

        await page.setJavaScriptEnabled(true);
        await page.setViewport({ width: 1280, height: 800 });

        console.log(`Navigating to: ${urlToRender}`);
        await page.goto(urlToRender, {
            waitUntil: "networkidle0",
            timeout: 10000,
        });
        const html = await page.content();

        cache.set(urlToRender, {
            html: html,
            expiry: Date.now() + CACHE_DURATION_MS,
        });

        // Clean up old cache entries periodically
        if (cache.size > 1000) {
            const oldestKey = cache.keys().next().value;
            cache.delete(oldestKey);
        }

        res.setHeader("X-Render-Cache", "miss");
        res.send(html);
    } catch (error) {
        console.error(`Error rendering ${urlToRender}:`, error);
        res.status(500).send(`Failed to render page. ${error.message}`);
    } finally {
        if (page) {
            try {
                await page.close();
                console.log(`Page closed for: ${urlToRender}`);
            } catch (e) {
                console.error(`Error closing page for ${urlToRender}:`, e);
            }
        }
    }
});

getBrowser()
    .then(() => {
        app.listen(port, "0.0.0.0", () => {
            console.log(`Renderer listening on http://0.0.0.0:${port}`);
        });
    })
    .catch((err) => {
        console.error("Failed to launch initial browser instance:", err);
        process.exit(1);
    });

process.on("SIGINT", async () => {
    console.log("Caught interrupt signal, closing browser...");
    if (browserInstance) {
        await browserInstance.close();
    }
    process.exit();
});
process.on("SIGTERM", async () => {
    console.log("Caught termination signal, closing browser...");
    if (browserInstance) {
        await browserInstance.close();
    }
    process.exit();
});
