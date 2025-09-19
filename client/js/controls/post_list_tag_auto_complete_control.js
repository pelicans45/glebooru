const TagList = require("../models/tag_list.js");
const TagAutoCompleteControl = require("./tag_auto_complete_control.js");

let reloadDefaultTagMatches = false;

class PostListTagAutoCompleteControl extends TagAutoCompleteControl {
    constructor(input, options) {
        super(input, options);

        this._setDefaultMatchesPromise = null;
        this._valueEntered = false;

        this._sourceInputNode.addEventListener("focus", (e) => {
            if (this._sourceInputNode.value) {
                return;
            }
            if (this._results.length) {
                this._displayDefaultMatches();
            } else if (this._setDefaultMatchesPromise) {
                this._setDefaultMatchesPromise.then(() => {
                    if (document.activeElement === this._sourceInputNode) {
                        this._displayDefaultMatches();
                    }
                });
            }
        });

        this._sourceInputNode.addEventListener("input", (e) => {
            this._displayDefaultMatches();
        });

        this._sourceInputNode.addEventListener("keydown", (e) => {
            if (e.keyCode !== 8) {
                return;
            }
            this._backspaced = true;
            if (this._activeResult === -1 && !this._valueEntered) {
                this._setDefaultMatches().then(() => {
                    this._show();
                });
            }
        });

        this._setDefaultMatches();
    }

    static setReloadDefaultTagMatches() {
        reloadDefaultTagMatches = true;
    }

    static unsetReloadDefaultTagMatches() {
        reloadDefaultTagMatches = false;
    }

    _setDefaultMatches() {
        this._setDefaultMatchesPromise = TagList.getTopRelevantMatches().then(
            (results) => {
                this._suggestionDiv.style.display = "none !important";
                this._results = results;
                this._refreshList();
                this.hide();
            }
        );
        return this._setDefaultMatchesPromise;
    }

    _displayDefaultMatches() {
        const val = this._sourceInputNode.value;
        //if (!val || /^ *sort:\S+ *$/.test(val)) {
        if (!val) {
            if (!(this._valueEntered || reloadDefaultTagMatches)) {
                this._show();
                return;
            }

            this._activeResult = -1;
            this._setDefaultMatches().then(() => {
                this._show();
                this._valueEntered = false;
                reloadDefaultTagMatches = false;
            });
            return;
        }

        //console.log("value entered");
        this._valueEntered = true;
    }
}

module.exports = PostListTagAutoCompleteControl;
