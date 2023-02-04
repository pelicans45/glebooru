const TagList = require("../models/tag_list.js");
const TagAutoCompleteControl = require("./tag_auto_complete_control.js");

class PostsListTagAutoCompleteControl extends TagAutoCompleteControl {
    constructor(input, options) {
		console.log("postslisttagautocompletecontrol")
        super(input, options);

		console.log("options", options);
        this._valueEntered = false;

        this._sourceInputNode.addEventListener("focus", (e) => {
            this._displayDefaultMatches();
        });

        this._sourceInputNode.addEventListener("input", (e) => {
            this._displayDefaultMatches();
        });

        this._setDefaultMatches();
    }

    _setDefaultMatches() {
        TagList.getTopRelevantMatches().then((results) => {
            this._suggestionDiv.style.display = "none !important";
            this._results = results;
            this._refreshList();
            this.hide();
        });
    }

    _displayDefaultMatches() {
		const val = this._sourceInputNode.value;
        if (!val || /^sort:\S+ +$/.test(val)) {
            if (!this._valueEntered) {
                this._show();
                console.log("no value, no prev value");
                return;
            }

            console.log("no value, yes prev value");

            this._activeResult = -1;
            this._setDefaultMatches();
            this._valueEntered = false;
            return;
        }

        this._valueEntered = true;
    }
}

module.exports = PostsListTagAutoCompleteControl;
