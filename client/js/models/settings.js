"use strict";

const api = require("../api.js");
const events = require("../events.js");

const defaultSettings = {
    listPosts: {
        safe: true,
        sketchy: false,
        unsafe: false,
    },
    uploadSafety: "safe",
    upscaleSmallPosts: false,
    endlessScroll: false,
    keyboardShortcuts: true,
    transparencyGrid: false,
    fitMode: "fit-both",
    tagSuggestions: true,
    autoplayVideos: false,
    postsPerPage: 40,
    tagUnderscoresAsSpaces: false,
    darkTheme: false,
    postFlow: false,
};

class Settings extends events.EventTarget {
    constructor() {
        super();
        this.cache = this._getFromLocalStorage();
    }

    _getFromLocalStorage() {
        let ret = Object.assign({}, defaultSettings);
        try {
            Object.assign(ret, JSON.parse(localStorage.getItem(this._settingsKey)));
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
        return "settings-" + api.userName;
    }
}

module.exports = new Settings();
