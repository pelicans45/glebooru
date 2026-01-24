"use strict";

const settings = require("../models/settings.js");
const router = require("../router.js");
const views = require("../util/views.js");
const seo = require("../util/seo.js");

const holderTemplate = views.getTemplate("endless-pager");
const pageTemplate = views.getTemplate("endless-pager-page");

class EndlessPageView {
    constructor(ctx) {
        this._hostNode = document.getElementById("content-holder");
        views.replaceContent(this._hostNode, holderTemplate());
    }

    run(ctx) {
        this._destroy();

        this._active = true;
        this._runningRequests = 0;
        this._initialPageLoad = true;

        this.clearMessages();
        views.emptyContent(this._pagesHolderNode);

        this.minOffsetShown = null;
        this.maxOffsetShown = null;
        this.totalRecords = null;
        this._hasMore = null;
        this.currentOffset = 0;
        this.defaultLimit = parseInt(ctx.parameters.limit || ctx.defaultLimit);

        const initialOffset = parseInt(ctx.parameters.offset || 0);
        if (this._isCacheValid(ctx)) {
            this._loadCachedPages(ctx);
        } else {
            this._clearCache(ctx);
            this._loadPage(ctx, initialOffset, this.defaultLimit, true).then(
                (pageNode) => {
                    if (initialOffset !== 0) {
                        pageNode.scrollIntoView();
                    }
                }
            );

            /*
			.then(
                (pageNode) => {
                    if (initialOffset !== 0) {
                        pageNode.scrollIntoView();
                    }
                }
            );
			*/
        }

        // TODO: replace with scroll listener?

        this._timeout = window.setInterval(() => {
            window.requestAnimationFrame(() => {
                const topPageNode = this._topPageNode;
                if (!topPageNode) {
                    //console.log("topPageNode is null");
                    return;
                }

                this._probePageLoad(ctx, topPageNode);
                this._syncUrl(ctx, topPageNode);
                if (this._shouldUseCache(ctx)) {
                    ctx.browserState.scrollY = window.scrollY;
                }
            });
        }, 250);

        views.monitorNodeRemoval(this._pagesHolderNode, () => this._destroy());
    }

    get pageHeaderHolderNode() {
        return this._hostNode.querySelector(".page-header-holder");
    }

    get topPageGuardNode() {
        return this._hostNode.querySelector(".page-guard.top");
    }

    get bottomPageGuardNode() {
        return this._hostNode.querySelector(".page-guard.bottom");
    }

    get _pagesHolderNode() {
        return this._hostNode.querySelector(".pages-holder");
    }

    get _topPageNode() {
        return document.querySelector(".page");

        let topPageNode = null;
        let element = document.elementFromPoint(
            window.innerWidth / 2,
            window.innerHeight / 2
        );
        while (element.parentNode !== null) {
            if (element.classList.contains("page")) {
                topPageNode = element;
                break;
            }
            element = element.parentNode;
        }
        return topPageNode;
    }

    _destroy() {
        window.clearInterval(this._timeout);
        this._active = false;
    }

    _syncUrl(ctx, topPageNode) {
        let topOffset = parseInt(topPageNode.getAttribute("data-offset"));
        let topLimit = parseInt(topPageNode.getAttribute("data-limit"));
        if (topOffset !== this.currentOffset) {
            const path = ctx.getClientUrlForPage(
                topOffset,
                topLimit === ctx.defaultLimit ? null : topLimit
            );
            if (this._shouldUseCache(ctx)) {
                // We only scrolled, so we should continue using the same cache entry;
                // Update the cache path so it's not invalidated:
                ctx.browserState.pageCache.path = "/" + path;
            }
            router.replace(
                path,
                // ctx here is not "real" context, it's the object from _syncPageController()
                ctx.browserState,
                false
            );
            this.currentOffset = topOffset;
        }
    }

    _probePageLoad(ctx, topPageNode) {
        if (!this._active || this._runningRequests) {
            return;
        }

        const scrollThreshold = topPageNode.scrollHeight * 0.40;

        if (this.minOffsetShown > 0 && window.scrollY < scrollThreshold) {
            this._loadPage(
                ctx,
                this.minOffsetShown - this.defaultLimit,
                this.defaultLimit,
                false
            );
        }

        const pageBottom =
            this._pagesHolderNode.getBoundingClientRect().bottom;
        const hasMore =
            this.totalRecords !== null
                ? this.maxOffsetShown < this.totalRecords
                : this._hasMore;
        if (hasMore && pageBottom < window.innerHeight + scrollThreshold) {
            this._loadPage(ctx, this.maxOffsetShown, this.defaultLimit, true);
        }
    }

    _shouldUseCache(ctx) {
        return (
            ctx.browserState !== undefined &&
            ctx.browserState !== null &&
            ctx.readPageFromCache !== undefined
        );
    }

    _isCacheValid(ctx) {
        if (!this._shouldUseCache(ctx)) return false;
        const cache = ctx.browserState.pageCache;
        return (
            cache !== null &&
            cache !== undefined &&
            cache.path === history.state.path &&
            //(!cache.r || cache.r.toString() === localStorage.r) &&
            cache.pages !== undefined &&
            cache.pages !== null
        );
    }

    _clearCache(ctx) {
        if (!this._shouldUseCache(ctx)) return;
        ctx.browserState.pageCache = { path: history.state.path, pages: {} };
    }

    _loadCachedPages(ctx) {
        if (!this._shouldUseCache(ctx)) return;
        // k-v map of page offset to raw response
        const pages = ctx.browserState.pageCache.pages || {};
        window.requestAnimationFrame(() => {
            for (const [offset, data] of Object.entries(pages)) {
                const response = {
                    offset: data.offset,
                    limit: data.limit,
                    total: data.total,
                    hasMore: data.hasMore,
                    results: ctx.readPageFromCache(data.raw_data),
                };
                this._renderPage(ctx, true, response);
            }
            window.scroll(0, ctx.browserState.scrollY || 0);
        });
    }

    _loadPage(ctx, offset, limit, append) {
        this._runningRequests++;
        return new Promise((resolve, reject) => {
            ctx.requestPage(offset, limit).then(
                (response) => {
                    if (!this._active) {
                        this._runningRequests--;
                        return Promise.reject();
                    }
                    if (this._shouldUseCache(ctx)) {
                        // Need to extract raw_data, otherwise it can't be stored in history
                        const pages = ctx.browserState.pageCache.pages || {};
                        pages[offset] = {
                            offset: response.offset,
                            limit: response.limit,
                            total: response.total,
                            hasMore: response.hasMore,
                            raw_data: response.results.raw_data,
                        };
                    }
                    window.requestAnimationFrame(() => {
                        let pageNode = this._renderPage(ctx, append, response);
                        this._runningRequests--;
                        resolve(pageNode);
                    });
                },
                (error) => {
                    this.showError(error.message);
                    this._runningRequests--;
                    reject();
                }
            );
        });
    }

    _renderPage(ctx, append, response) {
        let pageNode = null;

        const hasResults = response.results && response.results.length;
        const hasTotal =
            response.total !== undefined && response.total !== null;

        if (hasResults) {
            pageNode = pageTemplate({});
            pageNode.setAttribute("data-offset", response.offset);
            pageNode.setAttribute("data-limit", response.limit);

            let isLastPage = false;
            if (hasTotal) {
                const totalPages = Math.ceil(response.total / response.limit);
                const page = Math.ceil(
                    (response.offset + response.limit) / response.limit
                );
                isLastPage = page === totalPages;
            } else if (response.hasMore !== undefined) {
                isLastPage = !response.hasMore;
            }

            ctx.pageRenderer({
                parameters: ctx.parameters,
                response: response,
                addFlexAlignment:
                    settings.get().layoutType === "default" && isLastPage,
                hostNode: pageNode.querySelector(".page-content-holder"),
            });

            if (hasTotal) {
                this.totalRecords = response.total;
            } else if (response.hasMore !== undefined) {
                this._hasMore = response.hasMore;
            } else {
                this._hasMore = response.results.length >= response.limit;
            }

            if (
                response.offset < this.minOffsetShown ||
                this.minOffsetShown === null
            ) {
                this.minOffsetShown = response.offset;
            }
            if (
                response.offset + response.results.length >
                    this.maxOffsetShown ||
                this.maxOffsetShown === null
            ) {
                this.maxOffsetShown =
                    response.offset + response.results.length;
            }
            response.results.addEventListener("remove", (e) => {
                this.maxOffsetShown--;
                if (this.totalRecords !== null) {
                    this.totalRecords--;
                }
            });

            /*
            if (
                page === totalPages &&
                ctx.controllerType === "post_list" &&
                settings.get().layoutType === "default"
            ) {
                pageNode.innerHTML += views.makeFlexboxAlign();
            }
			*/

            if (
                !this._initialPageLoad &&
                ctx.controllerType === "post_list" &&
                settings.get().layoutType !== "column"
            ) {
                const els = pageNode.querySelectorAll(".post-list li");
                const list =
                    this._pagesHolderNode.querySelector(".post-list ul");
                if (append) {
                    list.append(...els);
                } else {
                    list.prepend(...els);
                }
            } else {
                if (append) {
                    this._pagesHolderNode.appendChild(pageNode);
                    if (this._initialPageLoad && response.offset > 0) {
                        window.scroll(0, pageNode.getBoundingClientRect().top);
                    }
                } else {
                    this._pagesHolderNode.prepend(pageNode);

                    window.scroll(
                        window.scrollX,
                        window.scrollY + pageNode.offsetHeight
                    );
                }
            }
        } else if (!hasResults) {
            this.showInfo("No results");
            // Set noindex for empty search results (soft 404)
            seo.setNoIndex();
            this._hasMore = false;
        }

        this._initialPageLoad = false;
        return pageNode;
    }

    clearMessages() {
        views.clearMessages(this._hostNode);
    }

    showSuccess(message) {
        views.showSuccess(this._hostNode, message);
    }

    showError(message) {
        views.showError(this._hostNode, message);
    }

    showInfo(message) {
        views.showInfo(this._hostNode, message);
    }
}

module.exports = EndlessPageView;
