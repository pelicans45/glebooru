"use strict";

const misc = require("../util/misc.js");
//const views = require("../util/views.js");
const tags = require("../tags.js");
const lens = require("../lens.js");
const TagList = require("../models/tag_list.js");
const AutoCompleteControl = require("./auto_complete_control.js");

class TagAutoCompleteControl extends AutoCompleteControl {
    constructor(input, options) {
        // TODO: change?
        options = Object.assign(
            {
                isTaggedWith: (tag) => input.split(" ").includes(tag),
            },
            options
        );

        if (lens.isUniversal) {
            options.getMatches = (text) => {
                if (text.includes(":")) {
                    return Promise.resolve([]);
                }
                const term = misc.escapeSearchTerm(text);
                const query =
                    (text.length < tags.minLengthForPartialSearch
                        ? term + "*"
                        : "*" + term + "*") + " sort:usages";

                return new Promise((resolve, reject) => {
                    TagList.search(query, 0, this._options.maxResults, [
                        "names",
                        "category",
                        "usages",
                    ]).then(
                        (response) =>
                            resolve(
                                tags.tagListToMatches(
                                    response.results,
                                    this._options
                                )
                            ),
                        reject
                    );
                });
            };
        } else {
            options.getMatches = (text) => {
                if (text.includes(":")) {
                    return Promise.resolve([]);
                }
                const term = misc.escapeSearchTerm(text);

                return new Promise((resolve, reject) => {
                    TagList.getRelevant(
                        term,
                        0,
                        this._options.maxResults
                    ).then(
                        (response) =>
                            resolve(
                                tags.tagListToMatches(
                                    response.results,
                                    this._options
                                )
                            ),
                        reject
                    );
                });
            };
        }

        super(input, options);

        this._valueEntered = false;
        this._suggestionDiv.style.display = "none !important";

        // Pre-load default tag selections
        this._setDefaultTagMatches();
    }

    _evtFocus(e) {
        return;
    }

    _setDefaultTagMatches() {
        TagList.getTopRelevantMatches().then(results, () => {
            this._results = results;
            this._refreshList();
            this.hide();
        });
    }

    _showOrHide() {
        // Immediately show initial suggestions
        if (!this._sourceInputNode.value) {
            if (!this._valueEntered) {
                this._show();
                return;
            }

            this._activeResult = -1;
            this._setDefaultTagMatches();
            this._valueEntered = false;
            return;
        }

        this._valueEntered = true;

        const textToFind = this._options.getTextToFind();
        if (!textToFind) {
            this.hide();
        } else {
            this._updateResults(textToFind);
        }
    }
}

/*
if (!lens.isUniversal) {
    TagAutoCompleteControl.prototype._showOrHide =
        TagAutoCompleteControl.prototype._lensShowOrHide;
}
*/

module.exports = TagAutoCompleteControl;
