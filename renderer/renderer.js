const express = require("express");
const puppeteer = require("puppeteer");

const app = express();
const port = 3000; // Port the renderer will listen on

// Basic in-memory cache (replace with Redis or similar for production)
const cache = new Map();
const CACHE_DURATION_MS = 60 * 60 * 1000; // 1 hour cache

let browserInstance = null;

async function getBrowser() {
    if (!browserInstance || !browserInstance.isConnected()) {
        console.log("Launching new browser instance...");
        try {
            browserInstance = await puppeteer.launch({
                headless: true,
                args: [
                    "--no-sandbox", // Often required in containerized/CI environments
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage", // Avoid issues with limited /dev/shm size
                ],
            });
            browserInstance.on("disconnected", () => {
                console.log("Browser disconnected.");
                browserInstance = null; // Reset instance if it crashes or closes
            });
            console.log("Browser launched successfully.");
        } catch (error) {
            console.error("Failed to launch browser:", error);
            browserInstance = null; // Ensure it's null on failure
            throw error; // Re-throw to signal failure
        }
    }
    return browserInstance;
}

// Helper function for modern fixed delay
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

app.get("/render/*", async (req, res) => {
    // Extract the URL to render *after* '/render/'
    // req.url includes the path and query string, e.g., /render/https://example.com?query=1
    // We need to reconstruct the full URL
    const urlToRender = req.url.substring("/render/".length);

    if (!urlToRender || !urlToRender.startsWith("http")) {
        console.error(`Invalid URL received: ${urlToRender}`);
        return res.status(400).send("A valid URL starting with http(s) to render is required after /render/.");
    }

    console.log(`Rendering request for: ${urlToRender}`);

    // Check cache
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

        // --- Capture Browser Console Logs ---
        page.on("console", (msg) => console.log(`Browser Console [${msg.type()}]: ${msg.text()}`));
        page.on("pageerror", (error) => console.error(`page.on("pageerror"):`, error));
        page.on("error", (error) => console.error(`page.on("error"):`, error));
        page.on("requestfailed", (request) =>
            console.warn(`Browser Request Failed: ${request.url()} (${request.failure()?.errorText || "N/A"})`)
        ); // Added null check for failure()
        // -------------------------------------

        // Explicitly ensure JavaScript is enabled
        await page.setJavaScriptEnabled(true);

        // Set a reasonable viewport and user agent (optional, but can help)
        await page.setViewport({ width: 1280, height: 800 });
        // Mimic Googlebot's user agent (optional)
        // await page.setUserAgent('Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)');

        console.log(`Navigating to: ${urlToRender}`);
        await page.goto(urlToRender, {
            waitUntil: "networkidle0", // Wait until network is idle (good starting point)
            timeout: 30000, // 30 seconds timeout
        });

        console.log("Waiting fixed 15 seconds for JS rendering (test)...");
        await delay(5000); // Use modern delay function
        console.log("Finished fixed wait.");

        const html = await page.content(); // Gets the full HTML content

        // Add to cache
        cache.set(urlToRender, {
            html: html,
            expiry: Date.now() + CACHE_DURATION_MS,
        });
        // Clean up old cache entries periodically (simple example)
        if (cache.size > 1000) {
            // Limit cache size
            const oldestKey = cache.keys().next().value;
            cache.delete(oldestKey);
        }

        res.setHeader("X-Render-Cache", "miss");
        res.send(html);
    } catch (error) {
        console.error(`Error rendering ${urlToRender}:`, error);
        // Don't close the shared browser instance here on page errors
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

// Start browser and server
getBrowser()
    .then(() => {
        app.listen(port, "0.0.0.0", () => {
            // Listen on all interfaces so it's accessible from other containers
            console.log(`Renderer listening on http://0.0.0.0:${port}`);
        });
    })
    .catch((err) => {
        console.error("Failed to launch initial browser instance:", err);
        process.exit(1);
    });

// Graceful shutdown
process.on("SIGINT", async () => {
    console.log("Caught interrupt signal, closing browser...");
    if (browserInstance) {
        await browserInstance.close();
    }
    process.exit();
});
process.on("SIGTERM", async () => {
    // Also handle SIGTERM for systemd/pm2
    console.log("Caught termination signal, closing browser...");
    if (browserInstance) {
        await browserInstance.close();
    }
    process.exit();
});
