"use strict";

/**
 * SEO utility module for managing meta tags dynamically.
 * Helps with Google indexing issues like soft 404s and duplicate content.
 */

let robotsMetaTag = null;
let canonicalLinkTag = null;

/**
 * Get or create the robots meta tag
 */
function getRobotsMetaTag() {
    if (!robotsMetaTag) {
        robotsMetaTag = document.querySelector('meta[name="robots"]');
        if (!robotsMetaTag) {
            robotsMetaTag = document.createElement("meta");
            robotsMetaTag.setAttribute("name", "robots");
            document.head.appendChild(robotsMetaTag);
        }
    }
    return robotsMetaTag;
}

/**
 * Get or create the canonical link tag
 */
function getCanonicalLinkTag() {
    if (!canonicalLinkTag) {
        canonicalLinkTag = document.querySelector('link[rel="canonical"]');
        if (!canonicalLinkTag) {
            canonicalLinkTag = document.createElement("link");
            canonicalLinkTag.setAttribute("rel", "canonical");
            document.head.appendChild(canonicalLinkTag);
        }
    }
    return canonicalLinkTag;
}

/**
 * Set the page to noindex (for 404 pages and other non-indexable content)
 * This prevents Google from indexing soft 404s as real pages.
 */
function setNoIndex() {
    const meta = getRobotsMetaTag();
    meta.setAttribute("content", "noindex");
}

/**
 * Clear the noindex directive, allowing the page to be indexed normally.
 */
function clearNoIndex() {
    const meta = getRobotsMetaTag();
    meta.setAttribute("content", "index, follow");
}

/**
 * Set the canonical URL for the current page.
 * This helps prevent "Duplicate without user-selected canonical" issues.
 * @param {string} path - The canonical path (without query parameters for search/pagination)
 */
function setCanonical(path) {
    const link = getCanonicalLinkTag();
    // Build the full canonical URL
    const origin = window.location.origin;
    // Remove trailing slashes and query strings for cleaner canonical URLs
    let cleanPath = path || window.location.pathname;
    cleanPath = cleanPath.replace(/\/+$/, ""); // Remove trailing slashes
    if (cleanPath === "") {
        cleanPath = "/";
    }
    link.setAttribute("href", origin + cleanPath);
}

/**
 * Set canonical URL from the current location pathname.
 * Strips query parameters to avoid pagination/filter duplicates.
 */
function setCanonicalFromPath() {
    setCanonical(window.location.pathname);
}

/**
 * Initialize SEO meta tags on page load.
 * Sets default canonical and robots directives.
 */
function initialize() {
    clearNoIndex();
    setCanonicalFromPath();
}

module.exports = {
    setNoIndex: setNoIndex,
    clearNoIndex: clearNoIndex,
    setCanonical: setCanonical,
    setCanonicalFromPath: setCanonicalFromPath,
    initialize: initialize,
};
