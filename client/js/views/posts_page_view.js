"use strict";

const events = require("../events.js");
const lens = require("../lens.js");
const tags = require("../tags.js");
const views = require("../util/views.js");
const misc = require("../util/misc.js");
const settings = require("../models/settings.js");

const template = views.getTemplate("posts-page");

class PostsPageView extends events.EventTarget {
    constructor(ctx) {
        super();
        this._ctx = ctx;
        this._hostNode = ctx.hostNode;
        ctx.excludeRedundantTags = lens.excludeRedundantTags;
        //ctx.needsTagsThreshold = lens.ctx.isUniversal ? 0 : 2;
        views.replaceContent(this._hostNode, template(ctx));

        this._postIdToPost = {};
        for (let post of ctx.response.results) {
            this._postIdToPost[post.id] = post;
            post.addEventListener("change", (e) => this._evtPostChange(e));
        }

        this._postIdToListItemNode = {};
        for (let listItemNode of this._listItemNodes) {
            const postId = listItemNode.getAttribute("data-post-id");
            const post = this._postIdToPost[postId];
            this._postIdToListItemNode[postId] = listItemNode;

            listItemNode.addEventListener("click", (e) => {
                if (!e.shiftKey) {
                    return;
                }

                misc.downloadURL(post.contentUrl, post.getDownloadFilename());
                e.preventDefault();
            });

            const tagFlipperNode = this._getTagFlipperNode(listItemNode);
            if (tagFlipperNode) {
                tagFlipperNode.addEventListener("click", (e) =>
                    this._evtBulkEditTagsClick(e, post)
                );
            }

            const relationFlipperNode =
                this._getRelationFlipperNode(listItemNode);
            if (relationFlipperNode) {
                relationFlipperNode.addEventListener("click", (e) =>
                    this._evtBulkAddRelationClick(e, post)
                );
            }

            const safetyFlipperNode = this._getSafetyFlipperNode(listItemNode);
            if (safetyFlipperNode) {
                for (let linkNode of safetyFlipperNode.querySelectorAll("a")) {
                    linkNode.addEventListener("click", (e) =>
                        this._evtBulkEditSafetyClick(e, post)
                    );
                }
            }

            const deleteFlipperNode = this._getDeleteFlipperNode(listItemNode);
            if (deleteFlipperNode) {
                deleteFlipperNode.addEventListener("click", (e) =>
                    this._evtBulkToggleDeleteClick(e, post)
                );
            }
        }

        this._syncBulkEditorsHighlights();

        const elements = this._hostNode.querySelectorAll(".post-list > ul");
        elements.forEach((element) => {
            if (!element.classList.contains("layout")) {
                element.classList.add(settings.get().layoutType + "-layout");
            }
        });

		const query = this._ctx.parameters.q || "";
		const scoreSort = query.includes("sort:score");
		this._hostNode.classList.toggle("show-score", scoreSort);
    }

    get _listItemNodes() {
        return this._hostNode.querySelectorAll("li");
    }

    _getTagFlipperNode(listItemNode) {
        return listItemNode.querySelector(".tag-flipper");
    }

    _getSafetyFlipperNode(listItemNode) {
        return listItemNode.querySelector(".safety-flipper");
    }

    _getRelationFlipperNode(listItemNode) {
        return listItemNode.querySelector(".relation-flipper");
    }

    _getDeleteFlipperNode(listItemNode) {
        return listItemNode.querySelector(".delete-flipper");
    }

    _evtPostChange(e) {
        const listItemNode = this._postIdToListItemNode[e.detail.post.id];
        for (let node of listItemNode.querySelectorAll("[data-disabled]")) {
            node.removeAttribute("data-disabled");
        }
        this._syncBulkEditorsHighlights();
    }

    _evtBulkEditTagsClick(e, post) {
        e.preventDefault();
        const linkNode = e.target;
        if (linkNode.getAttribute("data-disabled")) {
            return;
        }
        linkNode.setAttribute("data-disabled", true);
        this.dispatchEvent(
            new CustomEvent(
                linkNode.classList.contains("tagged") ? "untag" : "tag",
                {
                    detail: { post: post },
                }
            )
        );
    }

    _evtBulkAddRelationClick(e, post) {
        e.preventDefault();
        const linkNode = e.target;
        if (linkNode.getAttribute("data-disabled")) {
            return;
        }
        linkNode.setAttribute("data-disabled", true);
        this.dispatchEvent(
            new CustomEvent(
                linkNode.classList.contains("related")
                    ? "removeRelation"
                    : "addRelation",
                {
                    detail: { post: post },
                }
            )
        );
    }

    _evtBulkEditSafetyClick(e, post) {
        e.preventDefault();
        const linkNode = e.target;
        if (linkNode.getAttribute("data-disabled")) {
            return;
        }
        const newSafety = linkNode.getAttribute("data-safety");
        if (post.safety === newSafety) {
            return;
        }
        linkNode.setAttribute("data-disabled", true);
        this.dispatchEvent(
            new CustomEvent("changeSafety", {
                detail: { post: post, safety: newSafety },
            })
        );
    }

    _evtBulkToggleDeleteClick(e, post) {
        e.preventDefault();
        const linkNode = e.target;
        linkNode.classList.toggle("delete");
        this.dispatchEvent(
            new CustomEvent("markForDeletion", {
                detail: {
                    post,
                    delete: linkNode.classList.contains("delete"),
                },
            })
        );
    }

    _syncBulkEditorsHighlights() {
        for (let listItemNode of this._listItemNodes) {
            const postId = listItemNode.getAttribute("data-post-id");
            const post = this._postIdToPost[postId];

            const tagFlipperNode = this._getTagFlipperNode(listItemNode);
            if (tagFlipperNode) {
                let tagged = true;
                for (let tag of this._ctx.bulkEdit.tags) {
                    let tagData = tags.parseTagAndCategory(tag);
                    tagged &= post.tags.isTaggedWith(tagData.name);
                }
                tagFlipperNode.classList.toggle("tagged", tagged);
            }

            const safetyFlipperNode = this._getSafetyFlipperNode(listItemNode);
            if (safetyFlipperNode) {
                for (let linkNode of safetyFlipperNode.querySelectorAll("a")) {
                    const safety = linkNode.getAttribute("data-safety");
                    linkNode.classList.toggle(
                        "active",
                        post.safety === safety
                    );
                }
            }

            const relationFlipperNode =
                this._getRelationFlipperNode(listItemNode);
            if (relationFlipperNode) {
                let related = this._ctx.parameters.relations.includes(postId);
                relationFlipperNode.classList.toggle("related", related);
            }

            const deleteFlipperNode = this._getDeleteFlipperNode(listItemNode);
            if (deleteFlipperNode) {
                deleteFlipperNode.classList.toggle(
                    "delete",
                    this._ctx.bulkEdit.delete.some((x) => x.id == postId)
                );
            }
        }
    }
}

module.exports = PostsPageView;
