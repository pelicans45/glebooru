"use strict";

const misc = require("../util/misc.js");
const tags = require("../tags.js");
const lens = require("../lens.js");
const TagList = require("../models/tag_list.js");
const AutoCompleteControl = require("./auto_complete_control.js");

function _tagListToMatches(text, tagsList, options, negated) {
    return [...tagsList]
        .sort((tag1, tag2) => {
            return tag2.usages - tag1.usages;
        })
        .map((tag) => {
            let cssName = misc.makeCssName(tag.category, "tag");
            /*
            if (options.isTaggedWith(tag.names[0])) {
                cssName += " disabled";
            }
            */
            const matchingNames = misc.matchingNames(text, tag.names);
            tag.matchingNames = negated
                ? matchingNames.map((name) => "-" + name)
                : matchingNames;
            const caption =
                '<span class="' +
                cssName +
                '">' +
                misc.escapeHtml(
                    tag.matchingNames[0] + " (" + tag.postCount + ")"
                ) +
                "</span>";
            return {
                caption: caption,
                value: tag,
            };
        });
}

class TagAutoCompleteControl extends AutoCompleteControl {
    constructor(input, options) {
        // TODO: change?
        options = Object.assign(
            {
                isTaggedWith: (tag) => input.value.split(" ").includes(tag),
                isNegationAllowed: false,
                useRemoteSearch: lens.isUniversal,
                debounceMs: lens.isUniversal ? 150 : 0,
            },
            options
        );

        const useRemoteSearch = options.useRemoteSearch;
        if (useRemoteSearch) {
            options.getMatches = (text) => {
                const negated =
                    options.isNegationAllowed && text[0] === "-";
                if (negated) {
                    text = text.substring(1);
                }
                if (!text) {
                    return Promise.resolve([]);
                }
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
                                _tagListToMatches(
                                    text,
                                    response.results,
                                    this._options,
                                    negated
                                )
                            ),
                        reject
                    );
                });
            };
        } else {
            options.getMatches = (text) => {
                const negated =
                    options.isNegationAllowed && text[0] === "-";
                if (negated) {
                    text = text.substring(1);
                }
                if (!text) {
                    return Promise.resolve([]);
                }
                if (text.includes(":")) {
                    return Promise.resolve([]);
                }

                return new Promise((resolve, reject) => {
                    TagList.getRelevant(
                        text,
                        0,
                        this._options.maxResults
                    ).then(
                        (response) =>
                            resolve(
                                _tagListToMatches(
                                    text,
                                    response,
                                    this._options,
                                    negated
                                )
                            ),
                        reject
                    );
                });
            };
        }

        super(input, options);
    }

    _getActiveSuggestion() {
        if (this._activeResult === -1) {
            return null;
        }
        const result = this._results[this._activeResult].value;
        let textToFind = this._options.getTextToFind();
        const negated =
            this._options.isNegationAllowed && textToFind[0] === "-";
        if (negated) {
            textToFind = textToFind.substring(1);
        }
        const matchingNames = misc.matchingNames(textToFind, result.names);
        result.matchingNames = negated
            ? matchingNames.map((name) => "-" + name)
            : matchingNames;
        return result;
    }
}

module.exports = TagAutoCompleteControl;
