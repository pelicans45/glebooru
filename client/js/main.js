"use strict";

require("./util/polyfill.js");
const misc = require("./util/misc.js");
const views = require("./util/views.js");
const router = require("./router.js");

// TODO: change?
history.scrollRestoration = "manual";

router.exit(null, (ctx, next) => {
    ctx.state.scrollX = window.scrollX;
    ctx.state.scrollY = window.scrollY;
    router.replace(router.url, ctx.state);
    if (misc.confirmPageExit()) {
        next();
    }
});

const mousetrap = require("mousetrap");
router.enter(null, (ctx, next) => {
    mousetrap.reset();
    next();
});

const tags = require("./tags.js");
const pools = require("./pools.js");
const api = require("./api.js");
const settings = require("./models/settings.js");

// register controller routes
const controllers = [
    require("./controllers/post_list_controller_class.js"),
    require("./controllers/post_main_controller.js"),
    require("./controllers/post_upload_controller.js"),
    require("./controllers/post_detail_controller.js"),

    //require("./controllers/home_controller.js"),
    require("./controllers/help_controller.js"),
    require("./controllers/auth_controller.js"),

    require("./controllers/password_reset_controller.js"),
    require("./controllers/comments_controller.js"),
    require("./controllers/snapshots_controller.js"),

    require("./controllers/tag_controller.js"),
    require("./controllers/tag_list_controller.js"),

    require("./controllers/tag_categories_controller.js"),
    require("./controllers/pool_create_controller.js"),
    require("./controllers/pool_controller.js"),
    require("./controllers/pool_list_controller.js"),

    require("./controllers/pool_categories_controller.js"),
    require("./controllers/settings_controller.js"),
    require("./controllers/user_controller.js"),
    require("./controllers/user_list_controller.js"),

    require("./controllers/user_registration_controller.js"),
    require("./controllers/metric_sorter_contoller.js"),

    // Wildcard controller needs to be registered last
    require("./controllers/wildcard_controller.js"),
];

Promise.resolve()
    .then(() => {
        if (!settings.get().darkTheme) {
            document.body.classList.remove("darktheme");
        }
    })
    .then(
        () => {
            for (const controller of controllers) {
                console.log("controller", controller);
                controller(router);
            }
        },
        (error) => {
            window.alert("Unknown server error");
        }
    )
    .then(() => api.loginFromCookies())
    .then(
        () => {
            tags.refreshCategoryColorMap();
            pools.refreshCategoryColorMap();
            router.start();
        },
        (error) => {
            if (window.location.href.indexOf("login") !== -1) {
                api.forget();
                router.start();
            } else {
                const ctx = router.start("/");
                ctx.controller.showError(`Login error: ${error.message}`);
            }
        }
    );
