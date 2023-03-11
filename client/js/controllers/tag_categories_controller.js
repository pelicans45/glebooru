"use strict";

const api = require("../api.js");
const tags = require("../tags.js");
const TagCategoryList = require("../models/tag_category_list.js");
const topNavigation = require("../models/top_navigation.js");
const TagCategoriesView = require("../views/tag_categories_view.js");
const EmptyView = require("../views/empty_view.js");

class TagCategoriesController {
    constructor() {
        topNavigation.activate("tags");
        topNavigation.setTitle("Tag Categories");

        if (!api.hasPrivilege("tag_categories:list")) {
            this._view = new EmptyView();
            this._view.showError(
                "You don't have privileges to view tag categories."
            );
            return;
        }

        TagCategoryList.get().then(
            (response) => {
                this._tagCategories = response.results;
                this._view = new TagCategoriesView({
                    tagCategories: this._tagCategories,
                    canEditName: api.hasPrivilege("tag_categories:edit:name"),
                    canEditColor: api.hasPrivilege(
                        "tag_categories:edit:color"
                    ),
                    canEditOrder: api.hasPrivilege(
                        "tag_categories:edit:order"
                    ),
                    canDelete: api.hasPrivilege("tag_categories:delete"),
                    canCreate: api.hasPrivilege("tag_categories:create"),
                    canSetDefault: api.hasPrivilege(
                        "tag_categories:set_default"
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
        this._tagCategories.save().then(
            () => {
                tags.refreshCategoryColorMap();
                this._view.enableForm();
                this._view.showSuccess("Changes saved.");
            },
            (error) => {
                this._view.enableForm();
                this._view.showError(error.message);
            }
        );
    }
}

module.exports = (router) => {
    router.enter(["tag-categories"], (ctx, next) => {
        ctx.controller = new TagCategoriesController(ctx, next);
    });
};
