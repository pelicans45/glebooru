const TagList = require("../models/tag_list.js");
const TagAutoCompleteControl = require("./tag_auto_complete_control.js");

class PostsListTagAutoCompleteControl extends TagAutoCompleteControl {
    constructor(input, options) {
        super(input, options);

        this._valueEntered = false;

        this._sourceInputNode.addEventListener("focus", (e) => {
            this._displayDefaultMatches();
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

    _setDefaultMatches() {
        return TagList.getTopRelevantMatches().then((results) => {
            this._suggestionDiv.style.display = "none !important";
            this._results = results;
            this._refreshList();
            this.hide();
        });
    }

    _displayDefaultMatches() {
        const val = this._sourceInputNode.value;
        //if (!val || /^ *sort:\S+ *$/.test(val)) {
        if (!val) {
            if (!this._valueEntered) {
                this._show();
                return;
            }

            this._activeResult = -1;
            this._setDefaultMatches().then(() => {
                this._valueEntered = false;
                this._show();
            });

            /*
			this._activeResult = -1;
			this._setDefaultMatches();
			this._valueEntered = false;
			this._show();
			*/

            return;
        }

        //console.log("value entered");
        this._valueEntered = true;
    }
}

module.exports = PostsListTagAutoCompleteControl;
