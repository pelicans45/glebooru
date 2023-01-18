"use strict";

const api = require("../api.js");
const config = require("../config.js");
const tags = require("../tags.js");
const uri = require("../util/uri.js");
const lens = require("../lens.js");
const AbstractList = require("./abstract_list.js");
const Tag = require("./tag.js");

let allRelevantTags = null;
let topRelevantMatches = null;

class TagList extends AbstractList {
    static search(text, offset, limit, fields) {
        return api
            .get(
                uri.formatApiLink("tags", {
                    query: text,
                    offset: offset,
                    limit: limit,
                    fields: fields.join(","),
                }),
                { noProgress: true },
                (response) => {
                    response.results = lens.hostnameFilterTags(
                        response.results
                    );
                }
            )
            .then((response) => {
                return Promise.resolve(
                    Object.assign({}, response, {
                        results: TagList.fromResponse(response.results),
                    })
                );
            });
    }

    static getAllRelevant() {
        if (allRelevantTags) {
            return Promise.resolve(allRelevantTags);
        }

        if (lens.isUniversal) {
            return TagList.search("sort:usages", 0, config.maxSuggestedResults, [
                "names",
                "category",
                "usages",
            ]).then((response) => {
                allRelevantTags = response;
                return Promise.resolve(allRelevantTags);
            });
        }

        return api
            .get(
                uri.formatApiLink(`tag-siblings/${lens.hostnameFilter}`),
                { noProgress: true }
                /*
                (response) => {
                    response.results = lens.hostnameFilterTags(
                        response.results
                    );

                }
				*/
            )
            .then((response) => {
                for (const result of response.results) {
                    result.tag.usages = result.occurrences;
                }

                allRelevantTags = Object.assign({}, response, {
                    results: TagList.fromResponse(response.results),
                });

                return Promise.resolve(allRelevantTags);
            });
    }

    static getRelevant(query, offset, limit) {
        return TagList.getAllRelevant().then((_tags) => {
            let matchFunc;
            if (query.length < tags.minLengthForPartialSearch) {
                matchFunc = (name) => {
                    return name.startsWith(query);
                };
            } else {
                matchFunc = (name) => {
                    return name.includes(query);
                };
            }

            return Promise.resolve(
                _tags
                    .filter((tag) => matchFunc(tag.names[0]))
                    .slice(offset, offset + limit)
            );
        });
    }

    static getTopRelevantMatches() {
        if (topRelevantMatches) {
            return Promise.resolve(topRelevantMatches);
        }

        return TagList.getAllRelevant().then((response) => {
            topRelevantMatches = tags.tagListToMatches(
                response.results.slice(0, config.maxSuggestedResults),
                {
                    isTaggedWith: () => false,
                }
            );
            return Promise.resolve(topRelevantMatches);
        });
    }

    findByName(testName) {
        testName = testName.toLowerCase();
        for (let tag of this._list) {
            for (let tagName of tag.names) {
                if (tagName.toLowerCase() === testName) {
                    return tag;
                }
            }
        }
        return null;
    }

    isTaggedWith(testName) {
        return !!this.findByName(testName);
    }

    addByName(tagName, addImplications) {
        const tag = new Tag();
        tag.names = [tagName];
        return this.addByTag(tag, addImplications);
    }

    addByTag(tag, addImplications) {
        if (this.isTaggedWith(tag.names[0])) {
            return Promise.resolve();
        }

        this.add(tag);

        if (addImplications !== false) {
            return Tag.get(tag.names[0]).then((actualTag) => {
                return Promise.all(
                    actualTag.implications.map((relation) =>
                        this.addByName(relation.names[0], true)
                    )
                );
            });
        }

        return Promise.resolve();
    }

    removeByName(testName) {
        for (let tag of this._list) {
            for (let tagName of tag.names) {
                if (tagName.toLowerCase() === testName.toLowerCase()) {
                    this.remove(tag);
                }
            }
        }
    }

    filterMetrics() {
        return this.filter((tag) => tag.metric);
    }
}

if (lens.isUniversal) {
    TagList.search = TagList.apiSearch;
}

TagList._itemClass = Tag;
TagList._itemName = "tag";

module.exports = TagList;
