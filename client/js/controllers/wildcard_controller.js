"use strict";

const topNavigation = require("../models/top_navigation.js");
const NotFoundView = require("../views/not_found_view.js");
const { PostListController } = require("./post_list_controller.js");

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
            ctx.controller = PostListController(ctx);
            console.log("wildcard postlist - ctx:", ctx);
        } else {
            ctx.controller = NotFoundController(ctx.canonicalPath);
            console.log("wildcard notfound - ctx:", ctx);
        }
    });
};
