"use strict";

const router = require("../router.js");
const views = require("../util/views.js");
const uri = require("../util/uri.js");
const keyboard = require("../util/keyboard.js");
const Touch = require("../util/touch.js");
const PostContentControl = require("../controls/post_content_control.js");
const PostNotesOverlayControl = require("../controls/post_notes_overlay_control.js");
const PostReadonlySidebarControl = require("../controls/post_readonly_sidebar_control.js");
const PostEditSidebarControl = require("../controls/post_edit_sidebar_control.js");
const CommentControl = require("../controls/comment_control.js");
const CommentListControl = require("../controls/comment_list_control.js");

const template = views.getTemplate("post-main");

class PostMainView {
    constructor(ctx) {
        this._hostNode = document.getElementById("content-holder");
		this._loaded = false;

        window.loadMainContentTaggedUrl = () => {
			if (this._loaded) {
				return;
			}
			this._loaded = true;

            if (ctx.post.type !== "image") {
                return;
            }
            const mainContent = this._hostNode.querySelector(".main-content");
            if (!mainContent) {
                return;
            }
            const taggedUrl = ctx.post.taggedEnrichedContentUrl;
            if (mainContent.src === taggedUrl) {
                return;
            }

            mainContent.src = taggedUrl;
        };

        const sourceNode = template(ctx);
        const postContainerNode = sourceNode.querySelector(".post-container");
        //const sidebarNode = sourceNode.querySelector(".sidebar");
        views.replaceContent(this._hostNode, sourceNode);
        views.syncScrollPosition();

        //const topNavigationNode = document.body.querySelector("#top-navigation");

        /*
        this._postContentControl = new PostContentControl(
            postContainerNode,
            ctx.post,
            () => {
                return [
                    postContainerNode.getBoundingClientRect().width,
                    iosCorrectedInnerHeight() -
                        postContainerNode.getBoundingClientRect().top,
                ];
            }
        );
		*/

        this._postContentControl = new PostContentControl(
            postContainerNode,
            ctx.post,
            null
        );

        this._postNotesOverlayControl = new PostNotesOverlayControl(
            postContainerNode.querySelector(".post-overlay"),
            ctx.post
        );

        if (ctx.post.type === "video" || ctx.post.type === "flash") {
            this._postContentControl.disableOverlay();
        }

        this._installSidebar(ctx);
        const commentForm = this._installCommentForm();
        this._installAddCommentButton(commentForm);
        this._installComments(ctx.post.comments);

        const showPreviousImage = () => {
            if (ctx.prevPostId) {
                if (ctx.editMode) {
                    router.show(
                        ctx.getPostEditUrl(ctx.prevPostId, ctx.parameters)
                    );
                } else {
                    router.show(
                        ctx.getPostUrl(ctx.prevPostId, ctx.parameters)
                    );
                }
            }
        };

        const showNextImage = () => {
            if (ctx.nextPostId) {
                if (ctx.editMode) {
                    router.show(
                        ctx.getPostEditUrl(ctx.nextPostId, ctx.parameters)
                    );
                } else {
                    router.show(
                        ctx.getPostUrl(ctx.nextPostId, ctx.parameters)
                    );
                }
            }
        };

        const showRandomImage = () => {
            if (ctx.randomPostId) {
                const params = Object.assign({}, ctx.parameters);
                params.r = Math.round(Math.random() * 998) + 1;
                router.show(ctx.getPostUrl(ctx.randomPostId, params));
            }
        };

        keyboard.bind(["t", "e"], (e) => {
            if (ctx.editMode) {
                router.show(uri.formatClientLink("", ctx.post.id));
            } else {
                router.show(uri.formatClientLink("", ctx.post.id, "edit"));
            }
            e.preventDefault();
        });
        keyboard.bind(["a", "left"], showPreviousImage);
        keyboard.bind(["d", "right"], showNextImage);

        keyboard.bind(["alt+left"], (e) => {
            showPreviousImage();
            e.preventDefault();
            e.stopImmediatePropagation();
        });
        keyboard.bind(["alt+right"], (e) => {
            showNextImage();
            e.preventDefault();
            e.stopImmediatePropagation();
        });

        keyboard.bind("r", showRandomImage);
        keyboard.bind("del", (e) => {
            if (ctx.editMode) {
                this.sidebarControl._evtDeleteClick(e);
            }
        });

        new Touch(
            postContainerNode,
            () => {
                if (!ctx.editMode) {
                    showNextImage();
                }
            },
            () => {
                if (!ctx.editMode) {
                    showPreviousImage();
                }
            },
            () => {},
            () => {}
        );
    }

    _installSidebar(ctx) {
        const sidebarContainerNode = document.querySelector(
            "#content-holder .sidebar-container"
        );

        if (ctx.editMode) {
            this.sidebarControl = new PostEditSidebarControl(
                sidebarContainerNode,
                ctx,
                this._postContentControl,
                this._postNotesOverlayControl
            );
        } else {
            this.sidebarControl = new PostReadonlySidebarControl(
                sidebarContainerNode,
                ctx,
                this._postContentControl
            );
        }
    }

    _installCommentForm() {
        const commentFormContainer = document.querySelector(
            "#content-holder .comment-form-container"
        );
        if (!commentFormContainer) {
            return null;
        }
        this.commentControl = new CommentControl(
            commentFormContainer,
            null,
            true
        );
        return commentFormContainer;
    }

    _installAddCommentButton(commentForm) {
        const addCommentButton = document.querySelector("#add-comment-button");
        if (!addCommentButton || !commentForm) {
            return;
        }
        commentForm.hidden = true; // collapse by default
        addCommentButton.addEventListener("click", () => {
            commentForm.hidden = !commentForm.hidden;
            this.commentControl._textareaNode.focus();
        });
    }

    _installComments(comments) {
        const commentsContainerNode = document.querySelector(
            "#content-holder .comments-container"
        );
        if (!commentsContainerNode) {
            return;
        }

        this.commentListControl = new CommentListControl(
            commentsContainerNode,
            comments
        );
    }
}

module.exports = PostMainView;
