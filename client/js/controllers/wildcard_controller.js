"use strict";

const topNavigation = require("../models/top_navigation.js");
const NotFoundView = require("../views/not_found_view.js");
const PostListController = require("./post_list_controller_class.js");

const postListRegex = /^\/[\w\-%=:;+]+$/;

class NotFoundController {
    constructor(path) {
        topNavigation.activate("");
        topNavigation.setTitle("Not found");
        this._notFoundView = new NotFoundView(path);
    }
}

module.exports = (router) => {
    router.enter(null, (ctx, next) => {
        if (postListRegex.test(ctx.canonicalPath)) {
            ctx.controller = new PostListController(ctx);
        } else {
            ctx.controller = new NotFoundController(ctx.canonicalPath);
        }
    });
};
