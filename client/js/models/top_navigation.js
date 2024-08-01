"use strict";

const events = require("../events.js");
const lens = require("../lens.js");

class TopNavigationItem {
    constructor(accessKey, title, text, url, direction, available, imageUrl) {
        this.accessKey = accessKey;
        this.title = title;
        this.text = text;
        this.url = url;
        this.direction = direction;
        this.available = available === undefined ? true : available;
        this.imageUrl = imageUrl === undefined ? null : imageUrl;
        this.key = null;
    }
}

class TopNavigation extends events.EventTarget {
    constructor() {
        super();
        this.activeItem = null;
        this._keyToItem = new Map();
        this._items = [];
    }

    getAll() {
        return this._items;
    }

    get(key) {
        if (!this._keyToItem.has(key)) {
            throw `An item with key ${key} does not exist.`;
        }
        return this._keyToItem.get(key);
    }

    add(key, item) {
        item.key = key;
        if (this._keyToItem.has(key)) {
            throw `An item with key ${key} was already added.`;
        }
        this._keyToItem.set(key, item);
        this._items.push(item);
    }

    activate(key) {
        this.activeItem = null;
        this.dispatchEvent(
            new CustomEvent("activate", {
                detail: {
                    key: key,
                    item: key ? this.get(key) : null,
                },
            })
        );
    }

    setTitle(title) {
        document.title = lens.name + (title ? " – " + title : "");
        document.oldTitle = null;
    }

    showAll() {
        for (const item of this._items) {
            item.available = true;
        }
    }

    show(key) {
        this.get(key).available = true;
    }

    hide(key) {
        this.get(key).available = false;
    }
}

function _makeTopNavigation() {
    const ret = new TopNavigation();
    //ret.add("home", new TopNavigationItem("M", "Home", "home"));
    ret.add(
        "posts",
        new TopNavigationItem(
            "G",
            "Gallery",
            "<i class='la la-th'></i>",
            null,
            "left"
        )
    );
    ret.add(
        "upload",
        new TopNavigationItem(
            "U",
            "Upload",
            "<i class='la la-cloud-upload'></i>",
            "upload",
            "left"
        )
    );
    ret.add(
        "tags",
        new TopNavigationItem(
            "T",
            "Tags",
            "<i class='la la-tags'></i>",
            "tags",
            "right"
        )
    );
    ret.add(
        "comments",
        new TopNavigationItem(
            "C",
            "Comments",
            "<i class='la la-comments'></i>",
            "comments",
            "right"
        )
    );

    ret.add(
        "pools",
        new TopNavigationItem(
            "P",
            "Pools",
            "<i class='la la-icons'></i>",
            "pools",
            "right"
        )
    );
    ret.add(
        "users",
        new TopNavigationItem(
            null,
            "Users",
            "<i class='la la-users'></i>",
            "users",
            "right"
        )
    );
    ret.add(
        "register",
        new TopNavigationItem(
            "R",
            "Register",
            "<i class='la la-user-plus'></i>",
            "register",
            "right"
        )
    );
    ret.add(
        "login",
        new TopNavigationItem(
            "L",
            "Login",
            "<i class='la la-sign-in'></i>",
            "login",
            "right"
        )
    );
    ret.add(
        "logout",
        new TopNavigationItem(
            null,
            "Logout",
            "<i class='la la-sign-out'></i>",
            "logout",
            "right"
        )
    );
    ret.add(
        "discord",
        new TopNavigationItem(
            null,
            "Join Discord server",
            "<i class='lab la-discord'></i>",
            "discord/",
            "right"
        )
    );
    ret.add(
        "help",
        new TopNavigationItem(
            "H",
            "Help",
            "<i class='la la-info'></i>",
            "help",
            "right"
        )
    );
    ret.add(
        "account",
        new TopNavigationItem("A", "Account", "", "user/{me}", "right")
    );
    ret.add(
        "settings",
        new TopNavigationItem(
            null,
            "Settings",
            "<i class='la la-cog'></i>",
            "settings",
            "right"
        )
    );
    return ret;
}

module.exports = _makeTopNavigation();
