"use strict";

// modified page.js by visionmedia
// - changed regexes to components
// - removed unused crap
// - refactored to classes
// - simplified method chains
// - added ability to call .save() in .exit() without side effects
// - page refresh recovers state from history
// - rename .save() to .replaceState()
// - offer .url

const uri = require("./util/uri.js");
const mousetrap = require("mousetrap");

const clickEvent = document.ontouchstart ? "touchstart" : "click";
const location = window.history.location || window.location;

const origin = _getOrigin();
const base = _getBaseHref();

function _getOrigin() {
    return (
        location.protocol +
        "//" +
        location.hostname +
        (location.port ? ":" + location.port : "")
    );
}

function _isSameOrigin(href) {
    return href && href.indexOf(origin) === 0;
}

function _getBaseHref() {
    const bases = document.getElementById("base");
    return bases.length > 0
        ? bases[0].href.replace(origin, "").replace(/\/+$/, "")
        : "";
}

class Context {
    constructor(path, state) {
        path = path.indexOf("/") !== 0 ? "/" + path : path;
        path = path.indexOf(base) !== 0 ? base + path : path;

        this.canonicalPath = path;
        this.path = !path.indexOf(base) ? path.slice(base.length) : path;

        this.title = document.title;
        this.state = state || {};
        this.state.path = path;
        this.parameters = {};
    }

    pushState() {
        //console.log("pushState", this.state);
        history.pushState(this.state, this.title, this.canonicalPath);
    }

    replaceState() {
        //console.log("replaceState", this.state);
        history.replaceState(this.state, this.title, this.canonicalPath);
    }
}

class Route {
    constructor(path) {
        this.method = "GET";
        this.path = path;

        this.parameterNames = [];
        if (this.path === null) {
            this.regex = /^\/(.+)/;
            this.parameterNames.push("wildcard");
        } else {
            let parts = [];
            for (let component of this.path) {
                if (component[0] === ":") {
                    parts.push("([^/]+)");
                    this.parameterNames.push(component.substr(1));
                } else if (component[0] === "#") {
                    parts.push("(\\d+)");
                    this.parameterNames.push(component.substr(1));
                } else {
                    // assert [a-z]+
                    parts.push(component);
                }
            }
            let regexString = "^/" + parts.join("/");
            if (regexString === "^/") {
                regexString += "((?:(?:[a-z]+=[^/]+);)*(?:[a-z]+=[^/]+))?$";
                //regexString += "(?:/*|/((?:(?:[a-z]+=[^/]+);)*(?:[a-z]+=[^/]+)))$";
            } else {
                regexString +=
                    "(?:/*|/((?:(?:[a-z]+=[^/]+);)*(?:[a-z]+=[^/]+)))$";
            }

            this.parameterNames.push("variable");
            this.regex = new RegExp(regexString);
        }
    }

    middleware(fn) {
        return (ctx, next) => {
            if (this.match(ctx.path, ctx.parameters)) {
                mousetrap.reset();
                return fn(ctx, next);
            }
            next();
        };
    }

    match(path, parameters) {
        const qsIndex = path.indexOf("?");
        const pathname = ~qsIndex ? path.slice(0, qsIndex) : path;
        const match = this.regex.exec(pathname);
        if (!match) {
            return false;
        }

        try {
            for (let i = 1; i < match.length; i++) {
                const name = this.parameterNames[i - 1];
                const value = match[i];
                if (value === undefined) {
                    continue;
                }

                if (name === "variable") {
                    for (let word of (value || "").split(";")) {
                        const [key, subvalue] = word.split("=", 2);
                        parameters[key] = uri.unescapeParam(subvalue);
                    }
                } else if (name === "wildcard") {
                    //console.log("wildcard match", path, value);
                    if (!value) {
                        continue;
                    }
                    const parts = value.split(";");
                    const query = parts[0];
                    if (!query || query.indexOf("=") !== -1) {
                        continue;
                    }
                    parameters["q"] = uri.unescapeParam(
                        query.replace(/\+/g, "%20").replace(/:/g, "%3A")
                    );

                    for (let word of parts.slice(1)) {
                        const [key, subvalue] = word.split("=", 2);
                        parameters[key] = uri.unescapeParam(subvalue);
                    }
                } else {
                    parameters[name] = uri.unescapeParam(value);
                }
            }
        } catch (e) {
            return false;
        }

        return true;
    }
}

class Router {
    constructor() {
        this._callbacks = [];
        this._exits = [];
    }

    enter(path) {
        const route = new Route(path);
        for (let i = 1; i < arguments.length; ++i) {
            this._callbacks.push(route.middleware(arguments[i]));
        }
    }

    exit(path, fn) {
        const route = new Route(path);
        for (let i = 1; i < arguments.length; ++i) {
            this._exits.push(route.middleware(arguments[i]));
        }
    }

    start() {
        if (this._running) {
            return;
        }
        this._running = true;
        this._onPopState = _onPopState(this);
        this._onClick = _onClick(this);
        window.addEventListener("popstate", this._onPopState, false);
        document.addEventListener(clickEvent, this._onClick, false);
        const url = location.pathname + location.search + location.hash;
        // clear cached page data, in case we are refreshing the page:
        const initialState = Object.assign({}, history.state);
        delete initialState.pageCache;
        //localStorage.removeItem("r");
        return this.replace(url, initialState, true);
    }

    stop() {
        if (!this._running) {
            return;
        }
        this._running = false;
        document.removeEventListener(clickEvent, this._onClick, false);
        window.removeEventListener("popstate", this._onPopState, false);
    }

    showNoDispatch(path, state) {
        const ctx = new Context(path, state);
        ctx.pushState();
        // replaces old ctx with the current ctx (new page + history state)
        this.ctx = ctx;
        return ctx;
    }

    show(path, state, push) {
        const ctx = new Context(path, state);
        const oldPath = this.ctx ? this.ctx.path : ctx.path;
        this.dispatch(ctx, () => {
            if (ctx.path !== oldPath && push !== false) {
                ctx.pushState();
            }
        });
        return ctx;
    }

    replace(path, state, dispatch) {
        //console.log("replace", path, state);
        var ctx = new Context(path, state);
        if (dispatch) {
            this.dispatch(ctx, () => {
                ctx.replaceState();
            });
        } else {
            ctx.replaceState();
        }
        return ctx;
    }

    dispatch(ctx, middle) {
        const swap = (_ctx, next) => {
            // replaces old ctx with the current ctx (new page + history state)
            this.ctx = ctx;
            middle();
            next();
        };
        //console.log("ctx", ctx);
        //console.log("exits", this._exits);
        const callChain = (this.ctx ? this._exits : []).concat(
            [swap],
            this._callbacks,
            [this._unhandled, (ctx, next) => {}]
            /*
            [
                () => {
                    this._unhandled();
                },
                (ctx, next) => {},
            ]
			*/
        );
        let i = 0;
        let fn = () => {
            // Passes old ctx into the callbacks
            callChain[i++](this.ctx, fn);
        };
        fn();
    }

    _unhandled(ctx, next) {
        let current = location.pathname + location.search;
        if (current === ctx.canonicalPath) {
            return;
        }
        this.stop();
        location.href = ctx.canonicalPath;
    }

    get url() {
        return location.pathname + location.search + location.hash;
    }
}

const _onPopState = (router) => {
    let loaded = false;
    if (document.readyState === "complete") {
        loaded = true;
    } else {
        window.addEventListener("load", () => {
            setTimeout(() => {
                loaded = true;
            }, 0);
        });
    }
    return (e) => {
        if (!loaded) {
            return;
        }
        if (e.state) {
            const path = e.state.path;
            router.replace(path, e.state, true);
        } else {
            router.show(location.pathname + location.hash, undefined, false);
        }
    };
};

const _onClick = (router) => {
    return (e) => {
        if (
            _which(e) !== 1 ||
            e.metaKey ||
            e.ctrlKey ||
            e.shiftKey ||
            e.defaultPrevented
        ) {
            return;
        }

        let el = e.path ? e.path[0] : e.target;
        while (el && el.nodeName !== "A") {
            el = el.parentNode;
        }
        if (!el || el.nodeName !== "A") {
            return;
        }

        if (
            el.hasAttribute("download") ||
            el.getAttribute("rel") === "external"
        ) {
            return;
        }

        const link = el.getAttribute("href");
        if (
            (el.pathname === location.pathname && (el.hash || link === "#")) ||
            el.target ||
            !_isSameOrigin(el.href)
        ) {
            return;
        }

        const orig = el.pathname + el.search + (el.hash || "");

		/*
        const path = !orig.indexOf(base) ? orig.slice(base.length) : orig;

        if (orig === path) {
            console.error("orig === path", orig, path);
            //return;
        }

        console.error(
            "TODO: remove orig check (click home page from home page?)"
        );
		*/

        e.preventDefault();
        router.show(orig);
    };
};

function _which(e) {
    e = e || window.event;
    return e.which === null ? e.button : e.which;
}

Router.prototype.Context = Context;
Router.prototype.Route = Route;
module.exports = new Router();
