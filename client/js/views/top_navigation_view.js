"use strict";

const views = require("../util/views.js");
const settings = require("../models/settings.js");

const template = views.getTemplate("top-navigation");

const extraNavLinkTabs = new Set([
    "settings",
    "help",
    "account",
    "login",
    "logout",
    "register",
]);

class TopNavigationView {
    constructor() {
        this._key = null;
        this._hostNode = document.getElementById("top-navigation-holder");
        if (settings.get().navbarFollow) {
            this._hostNode.classList.add("follow-scroll");
        }
    }

    get _mobileNavigationToggleNode() {
        return this._hostNode.querySelector("#mobile-navigation-toggle");
    }

    get _topNavigation() {
        return this._hostNode.querySelector("#top-navigation");
    }

    get _navigationListNode() {
        return this._hostNode.querySelector("nav > ul");
    }

    get _navigationLinkNodes() {
        return this._navigationListNode.querySelectorAll("li > a");
    }

    render(ctx) {
        views.replaceContent(this._hostNode, template(ctx));
        this._bindMobileNavigationEvents();
    }

    activate(key) {
        if (this._key !== key) {
            console.log("activate", this._key, key);
            this._hostNode
                .querySelector("li[data-name].active")
                .classList.remove("active");

            this._hostNode
                .querySelector(`li[data-name="${key}"]`)
                .classList.add("active");

            /*
        for (let itemNode of this._hostNode.querySelectorAll("[data-name]")) {
            itemNode.classList.toggle(
                "active",
                itemNode.getAttribute("data-name") === key
            );
        }
		*/

            this._toggleExtraNavLinks(key);
        } else {
            console.log("no activate - same key", this._key, key);
        }
        this._key = key;
    }

    _bindMobileNavigationEvents() {
        this._mobileNavigationToggleNode.addEventListener("click", (e) =>
            this._mobileNavigationToggleClick(e)
        );

        for (let navigationLinkNode of this._navigationLinkNodes) {
            navigationLinkNode.addEventListener("click", (e) =>
                this._navigationLinkClick(e)
            );
        }
    }

    _mobileNavigationToggleClick(e) {
        this._navigationListNode.classList.toggle("opened");
    }

    _navigationLinkClick(e) {
        this._navigationListNode.classList.remove("opened");
    }

    _toggleExtraNavLinks(key) {
        this._topNavigation.classList.toggle(
            "show-extra-nav-links",
            extraNavLinkTabs.has(key)
        );
    }
}

module.exports = TopNavigationView;
