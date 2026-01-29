"use strict";

const fs = require("fs");
const { expect } = require("@playwright/test");

const defaultBaseURL = fs.existsSync("/.dockerenv")
    ? "http://nginx:4000"
    : "http://boorudev:4000";
const baseURL = process.env.PLAYWRIGHT_BASE_URL || defaultBaseURL;
const username = process.env.E2E_USER || "admin";
const password = process.env.E2E_PASS || "admin1234";
const basicAuth = Buffer.from(`${username}:${password}`).toString("base64");
const originalHost = process.env.E2E_ORIGINAL_HOST || "boorudev";
const runNonce =
    (Date.now() ^ Math.floor(Math.random() * 0x7fffffff)) >>> 0;
let seedCounter = 0;

function makeBmpBuffer({ nonce }) {
    const width = 16;
    const height = 16;
    const headerSize = 54;
    const rowSize = Math.ceil((width * 3) / 4) * 4;
    const imageSize = rowSize * height;
    const fileSize = headerSize + imageSize;
    const buffer = Buffer.alloc(fileSize);

    buffer.write("BM", 0, 2, "ascii");
    buffer.writeUInt32LE(fileSize, 2);
    buffer.writeUInt16LE(nonce & 0xffff, 6);
    buffer.writeUInt16LE((nonce >>> 16) & 0xffff, 8);
    buffer.writeUInt32LE(headerSize, 10);

    buffer.writeUInt32LE(40, 14);
    buffer.writeInt32LE(width, 18);
    buffer.writeInt32LE(height, 22);
    buffer.writeUInt16LE(1, 26);
    buffer.writeUInt16LE(24, 28);
    buffer.writeUInt32LE(0, 30);
    buffer.writeUInt32LE(imageSize, 34);
    buffer.writeInt32LE(0, 38);
    buffer.writeInt32LE(0, 42);
    buffer.writeUInt32LE(0, 46);
    buffer.writeUInt32LE(0, 50);

    let offset = headerSize;
    let state = nonce >>> 0;
    for (let y = 0; y < height; y += 1) {
        for (let x = 0; x < width; x += 1) {
            state = (state * 1664525 + 1013904223) >>> 0;
            buffer[offset++] = (state >> 16) & 0xff;
            buffer[offset++] = (state >> 8) & 0xff;
            buffer[offset++] = state & 0xff;
        }
        const padding = rowSize - width * 3;
        if (padding) {
            buffer.fill(0, offset, offset + padding);
            offset += padding;
        }
    }

    return buffer;
}

async function login(page) {
    await page.goto(`${baseURL}/login`);
    await page.fill('input[name="name"]', username);
    await page.fill('input[name="password"]', password);
    await page.getByRole("button", { name: "Login" }).click();
    await page.waitForURL(`${baseURL}/`);
    await expect(page.locator("text=Logged in")).toBeVisible();
    await page.waitForFunction(() =>
        document.cookie.split("; ").some((entry) => entry.startsWith("auth="))
    );
}

async function createPost(page, { tags = [], seed = 0 } = {}) {
    const effectiveSeed = seed + seedCounter;
    seedCounter += 1;
    const nonce = (runNonce + effectiveSeed) >>> 0;
    const buffer = makeBmpBuffer({ nonce });
    const base64 = buffer.toString("base64");
    return page.evaluate(
        async ({ baseURL, base64, tags, seed, authHeader, originalHost }) => {
            const binary = Uint8Array.from(atob(base64), (c) =>
                c.charCodeAt(0)
            );
            const blob = new Blob([binary], { type: "image/bmp" });
            const form = new FormData();
            form.append("content", blob, `e2e-${Date.now()}-${seed}.bmp`);
            const metadata = { safety: "safe" };
            if (tags.length) {
                metadata.tags = tags;
            }
            form.append(
                "metadata",
                new Blob([JSON.stringify(metadata)], {
                    type: "application/json",
                })
            );
            const response = await fetch(`${baseURL}/api/posts`, {
                method: "POST",
                body: form,
                headers: {
                    Authorization: `Basic ${authHeader}`,
                    "X-Original-Host": originalHost,
                },
                credentials: "same-origin",
            });
            if (!response.ok) {
                const body = await response.text();
                throw new Error(
                    `createPost failed: ${response.status} ${body}`
                );
            }
            return response.json();
        },
        {
            baseURL,
            base64,
            tags,
            seed: effectiveSeed,
            authHeader: basicAuth,
            originalHost,
        }
    );
}

async function ensurePostsWithTag(page, tag, count) {
    const query = tag ? `&q=${encodeURIComponent(tag)}` : "";
    const existing = await page.evaluate(
        async ({ baseURL, query, authHeader, originalHost }) => {
            const response = await fetch(
                `${baseURL}/api/posts?limit=1${query}`,
                {
                    credentials: "same-origin",
                    headers: {
                        Authorization: `Basic ${authHeader}`,
                        "X-Original-Host": originalHost,
                    },
                }
            );
            if (!response.ok) {
                const body = await response.text();
                throw new Error(
                    `post list failed: ${response.status} ${body}`
                );
            }
            const data = await response.json();
            return Number(data.total || 0);
        },
        { baseURL, query, authHeader: basicAuth, originalHost }
    );
    for (let i = existing; i < count; i += 1) {
        await createPost(page, { tags: tag ? [tag] : [], seed: i });
    }
}

module.exports = {
    baseURL,
    login,
    createPost,
    ensurePostsWithTag,
};
