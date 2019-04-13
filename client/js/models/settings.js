'use strict';

const events = require('../events.js');
const api = require('../api.js');

const defaultSettings = {
    listPosts: {
        safe: true,
        sketchy: false,
        unsafe: false,
    },
    uploadSafety: 'safe',
    upscaleSmallPosts: false,
    endlessScroll: false,
    keyboardShortcuts: true,
    transparencyGrid: false,
    fitMode: 'fit-both',
    tagSuggestions: true,
    autoplayVideos: false,
    postsPerPage: 40,
};

class Settings extends events.EventTarget {
    save(newSettings, silent) {
        newSettings = Object.assign(this.get(), newSettings);
        localStorage.setItem(this._settingsKey, JSON.stringify(newSettings));
        if (silent !== true) {
            this.dispatchEvent(new CustomEvent('change', {
                detail: {
                    settings: this.get(),
                },
            }));
        }
    }

    get() {
        let ret = Object.assign({}, defaultSettings);
        try {
            Object.assign(ret, JSON.parse(localStorage.getItem(this._settingsKey)));
        } catch (e) {
        }
        return ret;
    }

    get _settingsKey() {
        return 'settings-' + api.userName
    }
};

module.exports = new Settings();
