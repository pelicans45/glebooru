"use strict";

const events = require("../events.js");
const lens = require("../lens.js");

class TopNavigationItem {
    constructor(accessKey, title, text, url, available, imageUrl) {
        this.accessKey = accessKey;
        this.title = title;
        this.text = text;
        this.url = url;
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
            "<i class='la la-th left'></i>",
            ""
        )
    );
    ret.add(
        "upload",
        new TopNavigationItem(
            "U",
            "Upload",
            "<i class='la la-cloud-upload left'></i>",
            "upload"
        )
    );
    ret.add(
        "tags",
        new TopNavigationItem(
            "T",
            "Tags",
            "<i class='la la-tags right'></i>",
            "tags"
        )
    );
    ret.add(
        "comments",
        new TopNavigationItem(
            "C",
            "Comments",
            "<i class='la la-comments right'></i>",
            "comments"
        )
    );

    ret.add(
        "pools",
        new TopNavigationItem(
            "P",
            "Pools",
            "<i class='la la-icons right'></i>",
            "pools"
        )
    );
    ret.add(
        "users",
        new TopNavigationItem(
            null,
            "Users",
            "<i class='la la-users right'></i>",
            "users"
        )
    );
    ret.add(
        "register",
        new TopNavigationItem(
            "R",
            "Register",
            "<i class='la la-user-plus right'></i>",
            "register"
        )
    );
    ret.add(
        "login",
        new TopNavigationItem(
            "L",
            "Login",
            "<i class='la la-sign-in right'></i>",
            "login"
        )
    );
    ret.add(
        "logout",
        new TopNavigationItem(
            null,
            "Logout",
            "<i class='la la-sign-out right'></i>",
            "logout"
        )
    );
    ret.add(
        "help",
        new TopNavigationItem(
            "H",
            "Help",
            "<i class='la la-info right'></i>",
            "help"
        )
    );
    ret.add(
        "account",
        new TopNavigationItem("A", "Account", "right", "user/{me}")
    );
    ret.add(
        "settings",
        new TopNavigationItem(
            null,
            "Settings",
            "<i class='la la-cog right'></i>",
            "settings"
        )
    );
    return ret;
}

module.exports = _makeTopNavigation();
