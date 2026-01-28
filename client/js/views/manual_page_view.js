"use strict";

const settings = require("../models/settings.js");
const router = require("../router.js");
const keyboard = require("../util/keyboard.js");
const views = require("../util/views.js");
const seo = require("../util/seo.js");

const holderTemplate = views.getTemplate("manual-pager");
const navTemplate = views.getTemplate("manual-pager-nav");

function _removeConsecutiveDuplicates(a) {
    return a.filter((item, pos, ary) => {
        return !pos || item !== ary[pos - 1];
    });
}

function _getVisiblePageNumbers(currentPage, totalPages) {
    const threshold = 2;
    let pagesVisible = [];
    for (let i = 1; i <= threshold; i++) {
        pagesVisible.push(i);
    }
    for (let i = totalPages - threshold; i <= totalPages; i++) {
        pagesVisible.push(i);
    }
    for (let i = currentPage - threshold; i <= currentPage + threshold; i++) {
        pagesVisible.push(i);
    }
    pagesVisible = pagesVisible.filter((item, pos, ary) => {
        return item >= 1 && item <= totalPages;
    });
    pagesVisible = pagesVisible.sort((a, b) => {
        return a - b;
    });
    pagesVisible = _removeConsecutiveDuplicates(pagesVisible);
    return pagesVisible;
}

function _getPages(
    currentPage,
    pageNumbers,
    limit,
    defaultLimit,
    removedItems
) {
    const pages = new Map();
    let prevPage = 0;
    for (let page of pageNumbers) {
        if (page !== prevPage + 1) {
            pages.set(page - 1, { ellipsis: true });
        }
        pages.set(page, {
            number: page,
            offset:
                (page - 1) * limit - (page > currentPage ? removedItems : 0),
            limit: limit === defaultLimit ? null : limit,
            active: currentPage === page,
        });
        prevPage = page;
    }
    return pages;
}

class ManualPageView {
    constructor(ctx) {
        this._hostNode = document.getElementById("content-holder");
        views.replaceContent(this._hostNode, holderTemplate());
    }

    run(ctx) {
        this._runToken = (this._runToken || 0) + 1;
        const runToken = this._runToken;
        const offset = parseInt(ctx.parameters.offset || 0);
        const limit = parseInt(ctx.parameters.limit || ctx.defaultLimit);
        this.clearMessages();
        views.emptyContent(this._pageNavNode);

        ctx.requestPage(offset, limit).then(
            (response) => {
                if (runToken !== this._runToken) {
                    return;
                }
                ctx.pageRenderer({
                    manualPageView: true,
                    parameters: ctx.parameters,
                    response: response,
                    addFlexAlignment: settings.get().layoutType === "default",
                    hostNode: this._pageContentHolderNode,
                });

                keyboard.bind(["a", "left"], () => {
                    this._navigateToPrevNextPage("prev");
                });
                keyboard.bind(["d", "right"], () => {
                    this._navigateToPrevNextPage("next");
                });

                const hasTotal =
                    response.total !== undefined && response.total !== null;
                const hasMore =
                    response.hasMore !== undefined
                        ? response.hasMore
                        : response.results.length >= limit;
                let removedItems = 0;
                if (hasTotal) {
                    this._refreshNav(
                        offset,
                        limit,
                        response.total,
                        removedItems,
                        ctx
                    );
                } else if (offset > 0 || hasMore) {
                    this._refreshNavWithoutTotal(
                        offset,
                        limit,
                        hasMore,
                        ctx
                    );
                }

                if (!response.results.length) {
                    this.showInfo("No results");
                    // Set noindex for empty search results (soft 404)
                    seo.setNoIndex();
                }

                response.results.addEventListener("remove", (e) => {
                    removedItems++;
                    if (hasTotal) {
                        this._refreshNav(
                            offset,
                            limit,
                            response.total,
                            removedItems,
                            ctx
                        );
                    }
                });

                views.syncScrollPosition();
            },
            (response) => {
                if (runToken !== this._runToken) {
                    return;
                }
                this.showError(response.message);
            }
        );
    }

    get pageHeaderHolderNode() {
        return this._hostNode.querySelector(".page-header-holder");
    }

    get _pageContentHolderNode() {
        return this._hostNode.querySelector(".page-content-holder");
    }

    get _pageNavNode() {
        return this._hostNode.querySelector(".page-nav");
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

    _navigateToPrevNextPage(className) {
        const linkNode = this._hostNode.querySelector("a." + className);
        if (linkNode.classList.contains("disabled")) {
            return;
        }
        router.show(linkNode.getAttribute("href"));
    }

    _refreshNav(offset, limit, total, removedItems, ctx) {
        const currentPage = Math.floor((offset + limit - 1) / limit) + 1;
        const totalPages = Math.ceil((total - removedItems) / limit);
        const pageNumbers = _getVisiblePageNumbers(currentPage, totalPages);
        const pages = _getPages(
            currentPage,
            pageNumbers,
            limit,
            ctx.defaultLimit,
            removedItems
        );

        views.replaceContent(
            this._pageNavNode,
            navTemplate({
                getClientUrlForPage: ctx.getClientUrlForPage,
                prevPage: Math.min(totalPages, Math.max(1, currentPage - 1)),
                nextPage: Math.min(totalPages, Math.max(1, currentPage + 1)),
                currentPage: currentPage,
                totalPages: totalPages,
                pages: pages,
            })
        );
    }

    _refreshNavWithoutTotal(offset, limit, hasMore, ctx) {
        const currentPage = Math.floor((offset + limit - 1) / limit) + 1;
        const prevPage = currentPage > 1 ? currentPage - 1 : currentPage;
        const nextPage = hasMore ? currentPage + 1 : currentPage;
        const pages = new Map();
        const defaultLimit = ctx.defaultLimit;

        const makePage = (pageNumber, active) => {
            return {
                number: pageNumber,
                offset: (pageNumber - 1) * limit,
                limit: limit === defaultLimit ? null : limit,
                active: active,
            };
        };

        if (prevPage !== currentPage) {
            pages.set(prevPage, makePage(prevPage, false));
        }
        pages.set(currentPage, makePage(currentPage, true));
        if (nextPage !== currentPage) {
            pages.set(nextPage, makePage(nextPage, false));
        }

        views.replaceContent(
            this._pageNavNode,
            navTemplate({
                getClientUrlForPage: ctx.getClientUrlForPage,
                prevPage: prevPage,
                nextPage: nextPage,
                currentPage: currentPage,
                totalPages: nextPage,
                pages: pages,
            })
        );
    }
}

module.exports = ManualPageView;
