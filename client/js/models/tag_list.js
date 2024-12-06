"use strict";

const api = require("../api.js");
const vars = require("../vars.js");
const tags = require("../tags.js");
const uri = require("../util/uri.js");
const lens = require("../lens.js");
const AbstractList = require("./abstract_list.js");
const Tag = require("./tag.js");

let allRelevantTags = null;
let topRelevantMatches = null;

const fields = [
    "names",
    "suggestions",
    "implications",
    "creationTime",
    "usages",
    "category",
];

class TagList extends AbstractList {
    static search(text, offset, limit, fields, all) {
        let path = "tags";
        if (all) {
            path = "all-tags";
        }
        return api
            .get(
                uri.formatApiLink(path, {
                    q: text,
                    offset: offset,
                    limit: limit,
                    fields: fields.join(","),
                }),
                { noProgress: true },
                (response) => {
                    /*
                    response.results = lens.excludeRedundantTags(
                        response.results
                    );
					*/
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

    static getAllRelevant(refresh) {
        if (allRelevantTags && !refresh) {
            return Promise.resolve(allRelevantTags);
        }

        if (lens.isUniversal) {
            return this.search("sort:usages", 0, 5000, fields, true).then(
                (response) => {
                    allRelevantTags = response;
                    /*
                allRelevantTags = Object.assign({}, response, {
                    results: this.fromResponse(response.results),
                });
				*/
                    return Promise.resolve(allRelevantTags);
                }
            );
        }

        return api
            .get(uri.formatApiLink("lens-tags", lens.hostnameFilter), {
                noProgress: true,
            })
            .then((response) => {
                for (const result of response.results) {
                    result.tag.usages = result.occurrences;
                }

                const results = lens.excludeRedundantTags(
                    response.results.map((result) => result.tag)
                );

                allRelevantTags = Object.assign({}, response, {
                    results: this.fromResponse(results),
                });

                return Promise.resolve(allRelevantTags);
            });
    }

    static getRelevant(query, offset, limit) {
        return this.getAllRelevant().then((_tags) => {
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
                _tags.results
                    .copy()
                    .filter((tag) => matchFunc(tag.names[0]))
                    .slice(offset, offset + limit)
            );
        });
    }

    static getTopRelevantMatches(refresh) {
        if (topRelevantMatches && !refresh) {
            return Promise.resolve(topRelevantMatches);
        }

        return this.getAllRelevant(refresh).then((response) => {
            topRelevantMatches = tags.tagListToMatches(
                response.results.copy().slice(0, vars.maxSuggestedResults),
                {
                    isTaggedWith: () => false,
                }
            );
            return Promise.resolve(topRelevantMatches);
        });
    }

    static refreshRelevant() {
        //console.log("refreshing relevant tags");
        return this.getTopRelevantMatches(true);
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

TagList._itemClass = Tag;
TagList._itemName = "tag";

module.exports = TagList;
