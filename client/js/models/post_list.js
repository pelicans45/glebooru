"use strict";

const settings = require("../models/settings.js");
const api = require("../api.js");
const vars = require("../vars.js");
const uri = require("../util/uri.js");
const lens = require("../lens.js");
const AbstractList = require("./abstract_list.js");
const Post = require("./post.js");

class PostList extends AbstractList {
    static getAround(id, searchQuery, r) {
        return api.get(
            uri.formatApiLink("post", id, "around", {
                query: PostList.decorateSearchQuery(searchQuery || ""),
                fields: "id",
                r: r,
            })
        );
    }

    static search(text, offset, limit, fields, r, canSeeNewPosts) {
        return api
            .get(
                uri.formatApiLink("posts", {
                    query: PostList.decorateSearchQuery(text || ""),
                    offset: offset,
                    limit: limit,
                    fields: fields.join(","),
                    r: r,
                })
            )
            .then((response) => {
                let results;

                if (!canSeeNewPosts) {
                    const uploadedPostIDs = localStorage.uploadedPostIDs;
                    const uploadedPostIDSet = new Set(
                        uploadedPostIDs
                            ? uploadedPostIDs.split(";").filter((id) => id)
                            : []
                    );

                    const now = Date.now();
                    const filteredResults = [];
                    for (let item of response.results) {
                        const creationDate = Date.parse(item.creationTime);
                        if (
                            now >
                                creationDate +
                                    vars.newPostVisibilityThresholdMilliseconds ||
                            uploadedPostIDSet.has(item.id)
                        ) {
                            filteredResults.push(item);
                        }
                    }

                    results = filteredResults;
                } else {
                    results = response.results;
                }

                return Promise.resolve(
                    Object.assign({}, response, {
                        results: PostList.fromResponse(results),
                    })
                );
            });
    }

    static getMedian(text, fields) {
        return api
            .get(
                uri.formatApiLink("posts", "median", {
                    query: PostList.decorateSearchQuery(text || ""),
                    fields: fields.join(","),
                })
            )
            .then((response) => {
                return Promise.resolve(
                    Object.assign({}, response, {
                        results: PostList.fromResponse(response.results),
                    })
                );
            });
    }

    static reverseSearch(id, limit, threshold, fields) {
        return api
            .get(
                uri.formatApiLink("post", id, "reverse-search", {
                    limit: limit,
                    threshold: threshold,
                    fields: fields.join(","),
                })
            )
            .then((response) => {
                const results = response.similarPosts.map((sim) => sim.post);
                return Promise.resolve(
                    Object.assign({}, response, {
                        results: PostList.fromResponse(results),
                    })
                );
            });
    }

    static decorateSearchQuery(text) {
        const browsingSettings = settings.get();
        const disabledSafety = [];
        if (vars.safetyEnabled) {
            for (let key of Object.keys(browsingSettings.listPosts)) {
                if (browsingSettings.listPosts[key] === false) {
                    disabledSafety.push(key);
                }
            }
            if (disabledSafety.length) {
                text = `-rating:${disabledSafety.join(",")} ${text}`;
            }
        }

        text = lens.addHostnameFilter(text);
        return text.trim();
    }

    hasPostId(testId) {
        for (let post of this._list) {
            if (post.id === testId) {
                return true;
            }
        }
        return false;
    }

    addById(id) {
        if (this.hasPostId(id)) {
            return;
        }

        let post = Post.fromResponse({ id: id });
        this.add(post);
    }

    removeById(testId) {
        for (let post of this._list) {
            if (post.id === testId) {
                this.remove(post);
            }
        }
    }
}

PostList._itemClass = Post;
PostList._itemName = "post";

module.exports = PostList;
