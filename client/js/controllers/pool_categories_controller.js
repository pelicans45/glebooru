"use strict";

const api = require("../api.js");
const pools = require("../pools.js");
const PoolCategoryList = require("../models/pool_category_list.js");
const topNavigation = require("../models/top_navigation.js");
const PoolCategoriesView = require("../views/pool_categories_view.js");
const EmptyView = require("../views/empty_view.js");

class PoolCategoriesController {
    constructor() {
        topNavigation.activate("pools");
        topNavigation.setTitle("Pool Categories");

        if (!api.hasPrivilege("pool_categories:list")) {
            this._view = new EmptyView();
            this._view.showError(
                "You don't have privileges to view pool categories"
            );
            return;
        }

        PoolCategoryList.get().then(
            (response) => {
                this._poolCategories = response.results;
                this._view = new PoolCategoriesView({
                    poolCategories: this._poolCategories,
                    canEditName: api.hasPrivilege("pool_categories:edit:name"),
                    canEditColor: api.hasPrivilege(
                        "pool_categories:edit:color"
                    ),
                    canDelete: api.hasPrivilege("pool_categories:delete"),
                    canCreate: api.hasPrivilege("pool_categories:create"),
                    canSetDefault: api.hasPrivilege(
                        "pool_categories:setDefault"
                    ),
                });
                this._view.addEventListener("submit", (e) =>
                    this._evtSubmit(e)
                );
            },
            (error) => {
                this._view = new EmptyView();
                this._view.showError(error.message);
            }
        );
    }

    _evtSubmit(e) {
        this._view.clearMessages();
        this._view.disableForm();
        this._poolCategories.save().then(
            () => {
                pools.refreshCategoryColorMap();
                this._view.enableForm();
                this._view.showSuccess("Changes saved");
            },
            (error) => {
                this._view.enableForm();
                this._view.showError(error.message);
            }
        );
    }
}

module.exports = (router) => {
    router.enter(["pool-categories"], (ctx, next) => {
        ctx.controller = new PoolCategoriesController(ctx, next);
    });
};
