"use strict";

const settings = require("../models/settings.js");
const api = require("../api.js");
const vars = require("../vars.js");
const uri = require("../util/uri.js");
const lens = require("../lens.js");
const AbstractList = require("./abstract_list.js");
const Post = require("./post.js");

class PostList extends AbstractList {
    static getAround(id, searchQuery, r, fields, options) {
        const params = {
            q: PostList.decorateSearchQuery(searchQuery || ""),
            fields: "id",
            r: r,
        };
        if (fields && fields.length) {
            params.fields = fields.join(",");
        }
        const apiPromise = api.get(
            uri.formatApiLink("post", id, "around", {
                q: params.q,
                fields: params.fields,
                r: params.r,
            }),
            options
        );
        apiPromise.abort = apiPromise.abort || (() => {});
        return apiPromise;
    }

    static search(text, offset, limit, fields, r, canSeeNewPosts, options = {}) {
        const skipCount = "1";
        const beforeId = options.beforeId || null;
        const apiPromise = api.get(
                uri.formatApiLink(
                    "posts",
                    {
                        q: PostList.decorateSearchQuery(text || ""),
                        offset: offset,
                        limit: limit,
                        fields: fields.join(","),
                        r: r,
                        skipCount: skipCount,
                        beforeId: beforeId,
                    },
                    { showProgress: false }
                )
            );
        const returnedPromise = apiPromise.then((response) => {
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
        returnedPromise.abort = () => apiPromise.abort();
        return returnedPromise;
    }

    static getMedian(text, fields) {
        const apiPromise = api.get(
                uri.formatApiLink("posts", "median", {
                    q: PostList.decorateSearchQuery(text || ""),
                    fields: fields.join(","),
                })
            );
        const returnedPromise = apiPromise.then((response) => {
                return Promise.resolve(
                    Object.assign({}, response, {
                        results: PostList.fromResponse(response.results),
                    })
                );
            });
        returnedPromise.abort = () => apiPromise.abort();
        return returnedPromise;
    }

    static reverseSearch(id, limit, threshold, fields, query) {
        const apiPromise = api.get(
                uri.formatApiLink("post", id, "reverse-search", {
                    limit: limit,
                    threshold: threshold,
                    fields: fields.join(","),
                    q: query,
                })
            );
        const returnedPromise = apiPromise.then((response) => {
                const results = response.similarPosts.map((sim) => sim.post);
                return Promise.resolve(
                    Object.assign({}, response, {
                        results: PostList.fromResponse(results),
                    })
                );
            });
        returnedPromise.abort = () => apiPromise.abort();
        return returnedPromise;
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

        if (settings.get().hideAI) {
            if (!text.match(/\bai\b/i)) {
                text += " -tag:ai";
            }
        }

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
