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
        //api.fetchConfig().then(() => {
        document.oldTitle = null;
        document.title = lens.name + (title ? " – " + title : "");
        //});
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
    ret.add("posts", new TopNavigationItem("G", "Gallery", ""));
    ret.add("upload", new TopNavigationItem("U", "Upload", "upload"));
    ret.add("comments", new TopNavigationItem("C", "Comments", "comments"));
    ret.add("tags", new TopNavigationItem("T", "Tags", "tags"));
    ret.add("pools", new TopNavigationItem("P", "Pools", "pools"));
    ret.add("users", new TopNavigationItem(null, "Users", "users"));
    ret.add("account", new TopNavigationItem("A", "Account", "user/{me}"));
    ret.add("register", new TopNavigationItem("R", "Register", "register"));
    ret.add("login", new TopNavigationItem("L", "Login", "login"));
    ret.add("logout", new TopNavigationItem(null, "Logout", "logout"));
    ret.add("help", new TopNavigationItem("H", "Help", "help"));
    ret.add(
        "settings",
        new TopNavigationItem(null, "<i class='la la-cog'></i>", "settings")
    );
    return ret;
}

module.exports = _makeTopNavigation();
