"use strict";

const api = require("../api.js");
const events = require("../events.js");
const misc = require("../util/misc.js");

const defaultSettings = {
    listPosts: {
        safe: true,
        sketchy: false,
        unsafe: false,
    },
    uploadSafety: "safe",
    upscaleSmallPosts: false,
    endlessScroll: true,
    keyboardShortcuts: true,
    transparencyGrid: false,
    fitMode: "fit-both",
    tagSuggestions: true,
    autoplayVideos: false,
    postsPerPage: 48,
    similarPosts: 4,
    tagUnderscoresAsSpaces: true,
    darkTheme: true,
    postFlow: false,
    navbarFollow: false,
    layoutType: "default",
};

if (misc.isMobile) {
    defaultSettings.navbarFollow = true;
}

if (window.innerWidth <= window.innerHeight || window.innerWidth <= 1000) {
    defaultSettings.layoutType = "column";
}

class Settings extends events.EventTarget {
    constructor() {
        super();
        this.cache = this._getFromLocalStorage();
    }

    _getFromLocalStorage() {
        let ret = Object.assign({}, defaultSettings);
        try {
            Object.assign(
                ret,
                JSON.parse(localStorage.getItem(this._settingsKey))
            );
        } catch (e) {
            // continue regardless of error
        }
        return ret;
    }

    save(newSettings, silent) {
        newSettings = Object.assign(this.cache, newSettings);
        localStorage.setItem(this._settingsKey, JSON.stringify(newSettings));
        this.cache = this._getFromLocalStorage();
        if (silent !== true) {
            this.dispatchEvent(
                new CustomEvent("change", {
                    detail: {
                        settings: this.cache,
                    },
                })
            );
        }
    }

    get() {
        return this.cache;
    }

    get _settingsKey() {
        //FIXME(hunternif): username is null if settings are accessed before api.loginFromCookies()
        return "settings"; //-" + api.userName;
    }
}

module.exports = new Settings();
