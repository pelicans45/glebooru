"use strict";

const api = require("../api.js");
const lens = require("../lens.js");
const vars = require("../vars.js");
const events = require("../events.js");
const settings = require("../models/settings.js");
const views = require("../util/views.js");
const uri = require("../util/uri.js");
const misc = require("../util/misc.js");
const PostMetricListControl = require("./post_metric_list_control.js");
const PostList = require("../models/post_list.js");

const template = views.getTemplate("post-readonly-sidebar");
const scoreTemplate = views.getTemplate("score");
const favTemplate = views.getTemplate("fav");
const similarItemTemplate = views.getTemplate("similar-post-item");

const similarPostCount = 4;

class PostReadonlySidebarControl extends events.EventTarget {
    constructor(hostNode, ctx, postContentControl) {
        super();
        this._hostNode = hostNode;
        this._ctx = ctx;
        this._post = ctx.post;
        this._postContentControl = postContentControl;

        this._post.addEventListener("changeFavorite", (e) =>
            this._evtChangeFav(e)
        );
        this._post.addEventListener("changeScore", (e) =>
            this._evtChangeScore(e)
        );

        views.replaceContent(
            this._hostNode,
            template({
                post: this._post,
                tags: lens.excludeRedundantTags(this._post.tags),
                enableSafety: vars.safetyEnabled,
                canListPosts: api.hasPrivilege("posts:list"),
                canEditPosts: api.hasPrivilege("posts:edit"),
                canViewTags: api.hasPrivilege("tags:view"),
                canViewSimilar: api.hasPrivilege("posts:view:similar"),
                escapeTagName: uri.escapeTagName,
                extractRootDomain: uri.extractRootDomain,
                getPrettyName: misc.getPrettyName,
            })
        );

        this._installFav();
        this._installScore();
        /*
        this._installFitButtons();
        this._syncFitButton();
		*/
        /*
        if (this._metricsListNode) {
            this._metricsControl = new PostMetricListControl(
                this._metricsListNode,
                this._post
            );
        }
			*/
        this._loadLookalikePosts().then(() => this._loadSimilarPosts());
    }

    get _scoreContainerNode() {
        return this._hostNode.querySelector(".score-container");
    }

    get _favContainerNode() {
        return this._hostNode.querySelector(".fav-container");
    }

    get _upvoteButtonNode() {
        return this._hostNode.querySelector(".upvote");
    }

    get _downvoteButtonNode() {
        return this._hostNode.querySelector(".downvote");
    }

    get _addFavButtonNode() {
        return this._hostNode.querySelector(".add-favorite");
    }

    get _remFavButtonNode() {
        return this._hostNode.querySelector(".remove-favorite");
    }

    get _fitBothButtonNode() {
        return this._hostNode.querySelector(".fit-both");
    }

    get _fitOriginalButtonNode() {
        return this._hostNode.querySelector(".fit-original");
    }

    get _fitWidthButtonNode() {
        return this._hostNode.querySelector(".fit-width");
    }

    get _fitHeightButtonNode() {
        return this._hostNode.querySelector(".fit-height");
    }

    get _metricsListNode() {
        return this._hostNode.querySelector("ul.compact-post-metrics");
    }

    get _similarNode() {
        return this._hostNode.querySelector("nav.similar");
    }

    get _similarListNode() {
        return this._hostNode.querySelector("nav.similar ul");
    }

    get _lookalikesNode() {
        return this._hostNode.querySelector("nav.similar");
    }

    get _lookalikesListNode() {
        return this._hostNode.querySelector("nav.similar ul");
    }

    _installFitButtons() {
        this._fitBothButtonNode.addEventListener(
            "mousedown",
            this._eventZoomProxy(() => this._postContentControl.fitBoth())
        );
        this._fitOriginalButtonNode.addEventListener(
            "mousedown",
            this._eventZoomProxy(() => this._postContentControl.fitOriginal())
        );
        this._fitWidthButtonNode.addEventListener(
            "mousedown",
            this._eventZoomProxy(() => this._postContentControl.fitWidth())
        );
        this._fitHeightButtonNode.addEventListener(
            "mousedown",
            this._eventZoomProxy(() => this._postContentControl.fitHeight())
        );
    }

    _installFav() {
        views.replaceContent(
            this._favContainerNode,
            favTemplate({
                favoriteCount: this._post.favoriteCount,
                ownFavorite: this._post.ownFavorite,
                canFavorite: api.hasPrivilege("posts:favorite"),
            })
        );

        if (this._addFavButtonNode) {
            this._addFavButtonNode.addEventListener("mousedown", (e) =>
                this._evtAddToFavoritesClick(e)
            );
        }
        if (this._remFavButtonNode) {
            this._remFavButtonNode.addEventListener("mousedown", (e) =>
                this._evtRemoveFromFavoritesClick(e)
            );
        }
    }

    _installScore() {
        views.replaceContent(
            this._scoreContainerNode,
            scoreTemplate({
                score: this._post.score,
                ownScore: this._post.ownScore,
                canScore: api.hasPrivilege("posts:score"),
            })
        );
        if (this._upvoteButtonNode) {
            this._upvoteButtonNode.addEventListener("mousedown", (e) =>
                this._evtScoreClick(e, 1)
            );
        }
        if (this._downvoteButtonNode) {
            this._downvoteButtonNode.addEventListener("mousedown", (e) =>
                this._evtScoreClick(e, -1)
            );
        }
    }

    _eventZoomProxy(func) {
        return (e) => {
            e.preventDefault();
            e.target.blur();
            func();
            /*
            this._syncFitButton();
            this.dispatchEvent(
                new CustomEvent("fitModeChange", {
                    detail: {
                        mode: this._getFitMode(),
                    },
                })
            );
			*/
        };
    }

    _getFitMode() {
        const funcToName = {};
        funcToName[this._postContentControl.fitBoth] = "fit-both";
        funcToName[this._postContentControl.fitOriginal] = "fit-original";
        funcToName[this._postContentControl.fitWidth] = "fit-width";
        funcToName[this._postContentControl.fitHeight] = "fit-height";
        return funcToName[this._postContentControl._currentFitFunction];
    }

    _syncFitButton() {
        const className = this._getFitMode();
        const oldNode = this._hostNode.querySelector(".zoom a.active");
        const newNode = this._hostNode.querySelector(`.zoom a.${className}`);
        if (oldNode) {
            oldNode.classList.remove("active");
        }
        newNode.classList.add("active");
    }

    _evtAddToFavoritesClick(e) {
        e.preventDefault();
        this.dispatchEvent(
            new CustomEvent("favorite", {
                detail: {
                    post: this._post,
                },
            })
        );
    }

    _evtRemoveFromFavoritesClick(e) {
        e.preventDefault();
        this.dispatchEvent(
            new CustomEvent("unfavorite", {
                detail: {
                    post: this._post,
                },
            })
        );
    }

    _evtScoreClick(e, score) {
        e.preventDefault();
        this.dispatchEvent(
            new CustomEvent("score", {
                detail: {
                    post: this._post,
                    score: this._post.ownScore === score ? 0 : score,
                },
            })
        );
    }

    _evtChangeFav(e) {
        this._installFav();
    }

    _evtChangeScore(e) {
        this._installScore();
    }

    _loadSimilarPosts() {
        if (this._post.tags.length < 3) {
            return Promise.resolve();
        }

        return PostList.search(
            "similar:" + this._post.id + " -id:" + this._post.id,
            0,
            similarPostCount,
            ["id", "thumbnailUrl"],
            undefined,
            true
        ).then((response) => {
            if (response.results.length === 0) {
                return;
            }

            const existingIds = Array.from(this._similarListNode.children).map(
                (node) =>
                    node
                        .querySelector("a")
                        .getAttribute("href")
                        .split("/")
                        .pop()
            );

            const listNode = this._similarListNode;

            for (let post of response.results) {
                // prevent duplicates
                if (existingIds.includes(post.id.toString())) {
                    continue;
                }

                let postNode = similarItemTemplate({
                    id: post.id,
                    thumbnailUrl: post.thumbnailUrl,
                });

                postNode.classList.add("similar-item");

                listNode.appendChild(postNode);
            }
        });
    }

    _loadLookalikePosts() {
        const limit = similarPostCount;
        const fields = ["id", "thumbnailUrl"];
        const threshold = 0.6;
        return PostList.reverseSearch(
            this._post.id,
            limit,
            threshold,
            fields
        ).then((response) => {
            if (response.results.length === 0) {
                return;
            }

            const listNode = this._lookalikesListNode;

            for (let post of response.results) {
                let postNode = similarItemTemplate({
                    id: post.id,
                    thumbnailUrl: post.thumbnailUrl,
                });

                postNode.classList.add("lookalike-item");

                listNode.appendChild(postNode);
            }
        });
    }
}

module.exports = PostReadonlySidebarControl;
