"use strict";

const views = require("../util/views.js");
const settings = require("../models/settings.js");

const template = views.getTemplate("top-navigation");

const extraNavLinkTabs = new Set([
    "settings",
    "help",
    "account",
    "login",
    //"logout",
    "register",
    "comments",
    "users",
    "pools",
    "discord",
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

    get _siteNameNode() {
        return this._mobileNavigationToggleNode.querySelector(".site-name");
    }

    get _topNavigation() {
        return this._hostNode.querySelector("#top-navigation");
    }

    get _navigationListNodes() {
        return this._hostNode.querySelectorAll("nav > ul");
    }

    get _navigationLinkNodes() {
        let nodes = [];
        this._navigationListNodes.forEach((element) => {
            nodes.push(element.querySelectorAll("li > a"));
        });

        return nodes;
    }

    render(ctx) {
        views.replaceContent(this._hostNode, template(ctx));
        this._bindMobileNavigationEvents();
    }

    activate(key) {
        if (this._key !== key) {
            const active = this._hostNode.querySelector(
                "li[data-name].active"
            );

            if (active) {
                active.classList.remove("active");
            }

            const current = this._hostNode.querySelector(
                `li[data-name="${key}"]`
            );
            if (current) {
                current.classList.add("active");
            }

            /*
        for (let itemNode of this._hostNode.querySelectorAll("[data-name]")) {
            itemNode.classList.toggle(
                "active",
                itemNode.getAttribute("data-name") === key
            );
        }
		*/

            this._toggleExtraNavLinks(key);
        }
        this._key = key;
    }

    _bindMobileNavigationEvents() {
        this._mobileNavigationToggleNode.addEventListener("click", (e) =>
            this._mobileNavigationToggleClick()
        );

        this._siteNameNode.addEventListener("click", (e) =>
            this._siteNameNodeClick(e)
        );

        for (const navigationLinkNode of this._navigationLinkNodes) {
            navigationLinkNode.forEach((element) => {
                element.addEventListener("click", (e) =>
                    this._navigationLinkClick()
                );
            });
        }
    }

    _mobileNavigationToggleClick() {
        this._navigationListNodes.forEach((nav) => {
            nav.classList.toggle("opened");
        });
    }
    _siteNameNodeClick(e) {
        e.stopPropagation();
        this._topNavigation.querySelector(`[title="Gallery"]`).click();
    }
    _navigationLinkClick() {
        this._navigationListNodes.forEach((nav) => {
            nav.classList.remove("opened");
        });
    }

    _toggleExtraNavLinks(key) {
        this._topNavigation.classList.toggle(
            "show-extra-nav-links",
            extraNavLinkTabs.has(key)
        );
    }
}

module.exports = TopNavigationView;
