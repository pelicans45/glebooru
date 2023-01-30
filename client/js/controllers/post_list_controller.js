const PostListController = require("./post_list_controller_class.js");

module.exports = (router) => {
    router.enter([], (ctx, next) => {
        console.log("main postlistcontroller");
        ctx.controller = new PostListController(ctx);
    });
};
