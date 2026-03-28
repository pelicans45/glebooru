"use strict";

const settings = require("../models/settings.js");
const EndlessPageView = require("../views/endless_page_view.js");
const ManualPageView = require("../views/manual_page_view.js");

let _runToken = 0;

class PageController {
    constructor(ctx) {
        if (settings.get().endlessScroll) {
            this._view = new EndlessPageView();
        } else {
            this._view = new ManualPageView();
        }
        this._activeRequests = new Set();
    }

    get view() {
        return this._view;
    }

    run(ctx) {
        this._abort();
        _runToken++;
        const token = _runToken;

        const wrappedCtx = Object.assign({}, ctx, {
            _isStale: () => token !== _runToken,
            requestPage: (offset, limit) => {
                const promise = ctx.requestPage(offset, limit);
                if (promise && promise.abort) {
                    this._activeRequests.add(promise);
                    promise.then(
                        () => this._activeRequests.delete(promise),
                        () => this._activeRequests.delete(promise)
                    );
                }
                return promise;
            },
        });

        this._view.run(wrappedCtx);
    }

    _abort() {
        for (const request of this._activeRequests) {
            if (request && request.abort) {
                request.abort();
            }
        }
        this._activeRequests.clear();
    }

    showSuccess(message) {
        this._view.showSuccess(message);
    }

    showError(message) {
        this._view.showError(message);
    }
}

module.exports = PageController;
