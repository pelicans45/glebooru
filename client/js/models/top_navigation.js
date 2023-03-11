"use strict";

const events = require("../events.js");
const lens = require("../lens.js");

class TopNavigationItem {
    constructor(accessKey, title, url, available, imageUrl) {
        this.accessKey = accessKey;
        this.title = title;
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
        for (let item of this._items) {
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
        new TopNavigationItem("G", "<i class='la la-th'></i>", "")
    );
    ret.add(
        "upload",
        new TopNavigationItem("U", "<i class='la la-cloud-upload'></i>", "upload")
    );
    ret.add(
        "comments",
        new TopNavigationItem("C", "<i class='la la-comments'></i>", "comments")
    );
    ret.add(
        "tags",
        new TopNavigationItem("T", "<i class='la la-tags'></i>", "tags")
    );
    ret.add(
        "pools",
        new TopNavigationItem("P", "<i class='la la-icons'></i>", "pools")
    );
    ret.add(
        "users",
        new TopNavigationItem(null, "<i class='la la-users'></i>", "users")
    );
    ret.add(
        "account",
        new TopNavigationItem("A", "<i class='la la-user'></i>", "user/{me}")
    );
    ret.add("register", new TopNavigationItem("R", "Register", "register"));
    ret.add(
        "login",
        new TopNavigationItem("L", "<i class='la la-sign-in'></i>", "login")
    );
    ret.add(
        "logout",
        new TopNavigationItem(null, "<i class='la la-sign-out'></i>", "logout")
    );
    ret.add(
        "help",
        new TopNavigationItem("H", "<i class='la la-info'></i>", "help")
    );
    ret.add(
        "settings",
        new TopNavigationItem(null, "<i class='la la-cog'></i>", "settings")
    );
    return ret;
}

module.exports = _makeTopNavigation();
