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
                isTaggedWith: (tag) => input.value.split(" ").includes(tag),
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
    }
}

module.exports = TagAutoCompleteControl;
