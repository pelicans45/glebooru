"use strict";

const events = require("../events.js");
const settings = require("../models/settings.js");
const keyboard = require("../util/keyboard.js");
const misc = require("../util/misc.js");
const search = require("../util/search.js");
const views = require("../util/views.js");
const TagList = require("../models/tag_list.js");
const TagAutoCompleteControl = require("../controls/tag_auto_complete_control.js");
const PostListTagAutoCompleteControl = require("../controls/post_list_tag_auto_complete_control.js");

const template = views.getTemplate("posts-header");

class BulkEditor extends events.EventTarget {
    constructor(hostNode) {
        super();
        this._hostNode = hostNode;
        if (this._openLinkNode) {
            this._openLinkNode.addEventListener("click", (e) =>
                this._evtOpenLinkClick(e)
            );
        }
        if (this._closeLinkNode) {
            this._closeLinkNode.addEventListener("click", (e) =>
                this._evtCloseLinkClick(e)
            );
        }
    }

    get opened() {
        return (
            this._hostNode.classList.contains("opened") &&
            !this._hostNode.classList.contains("hidden")
        );
    }

    get _openLinkNode() {
        return this._hostNode.querySelector(".open");
    }

    get _closeLinkNode() {
        return this._hostNode.querySelector(".close");
    }

    get _submitLinkNode() {
        return this._hostNode.querySelector("input[type=submit]");
    }

    toggleOpen(state) {
        this._hostNode.classList.toggle("opened", state);
    }

    toggleHide(state) {
        this._hostNode.classList.toggle("hidden", state);
    }

    reset() {
        this.toggleOpen(false);
        this.toggleHide(false);
    }

    _evtOpenLinkClick(e) {
        throw new Error("Not implemented");
    }

    _evtCloseLinkClick(e) {
        throw new Error("Not implemented");
    }
}

class BulkSafetyEditor extends BulkEditor {
    _evtOpenLinkClick(e) {
        e.preventDefault();
        this.toggleOpen(true);
        this.dispatchEvent(new CustomEvent("open", { detail: {} }));
    }

    _evtCloseLinkClick(e) {
        e.preventDefault();
        this.toggleOpen(false);
        this.dispatchEvent(new CustomEvent("close", { detail: {} }));
    }
}

class BulkTagEditor extends BulkEditor {
    constructor(hostNode, options = {}) {
        super(hostNode);
        this._isActive = Boolean(options.active);
        this._autoCompleteControl = new TagAutoCompleteControl(
            this._inputNode,
            {
                confirm: (tag) => {
                    let tag_list = new TagList();
                    tag_list
                        .addByName(tag.names[0], true)
                        .then(
                            () => {
                                return tag_list
                                    .map((s) => s.names[0])
                                    .join(" ");
                            },
                            (err) => {
                                return tag.names[0];
                            }
                        )
                        .then((tag_str) => {
                            this._autoCompleteControl.replaceSelectedText(
                                tag_str,
                                false
                            );
                            this._syncSubmitButton();
                        });
                },
            }
        );
        this._hostNode.addEventListener("submit", (e) =>
            this._evtFormSubmit(e)
        );

        if (this._selectAllNode) {
            this._selectAllNode.addEventListener("click", (e) =>
                this._evtSelectAllClick(e)
            );
        }

        if (this._actionNode) {
            this._actionNode.addEventListener("change", () =>
                this._syncSubmitButton()
            );
        }
        if (this._inputNode) {
            this._inputNode.addEventListener("input", () =>
                this._syncSubmitButton()
            );
        }
        this._syncSubmitButton();
    }

    get value() {
        return this._inputNode.value;
    }

    get action() {
        return this._actionNode && this._actionNode.value === "remove"
            ? "remove"
            : "add";
    }

    get _inputNode() {
        return this._hostNode.querySelector("input[name=tag]");
    }

    get _actionNode() {
        return this._hostNode.querySelector("select[name=tag-action]");
    }

    get _selectAllNode() {
        return this._hostNode.querySelector(".select-all");
    }

    focusInput() {
        search.focusInputNode(this._inputNode);
    }

    blur() {
        this._autoCompleteControl.hide();
        this._inputNode.blur();
    }

    _evtFormSubmit(e) {
        e.preventDefault();
        if (this._isActive) {
            this._isActive = false;
            this._inputNode.value = "";
            this._syncSubmitButton();
            this.focusInput();
            this.dispatchEvent(new CustomEvent("submit", { detail: {} }));
            return;
        }
        if (!this._hasTagValue()) {
            this._syncSubmitButton();
            this.focusInput();
            return;
        }
        this.dispatchEvent(new CustomEvent("submit", { detail: {} }));
        this._isActive = true;
        this._syncSubmitButton();
    }

    _evtSelectAllClick(e) {
        e.preventDefault();
        if (this._selectAllNode.classList.contains("inactive")) {
            return;
        }
        const selectForRemove = this.action === "remove";
        const flipperNodes = [...document.querySelectorAll(".tag-flipper")];
        const selectable = flipperNodes.filter((node) =>
            selectForRemove
                ? node.classList.contains("tagged")
                : !node.classList.contains("tagged")
        );
        if (!selectable.length) {
            return;
        }
        const actionVerb = selectForRemove ? "untag" : "tag";
        const noun = selectable.length === 1 ? "post" : "posts";
        if (!confirm(`Apply ${actionVerb} to ${selectable.length} ${noun}?`)) {
            return;
        }
        selectable.forEach((node) => node.click());
    }

    _evtOpenLinkClick(e) {
        e.preventDefault();
        this.toggleOpen(true);
        this.dispatchEvent(new CustomEvent("open", { detail: {} }));
        this._syncSubmitButton();
        this.focusInput();
    }

    _evtCloseLinkClick(e) {
        e.preventDefault();
        this.reset();
        this.dispatchEvent(new CustomEvent("close", { detail: {} }));
    }

    reset() {
        this._inputNode.value = "";
        if (this._actionNode) {
            this._actionNode.value = "add";
        }
        this._isActive = false;
        this.blur();
        this._syncSubmitButton();
        super.reset();
    }

    _syncSubmitButton() {
        const node = this._submitLinkNode;
        const actionNode = this._actionNode;
        const inputNode = this._inputNode;
        const selectAllNode = this._selectAllNode;
        node.disabled = !this._isActive && !this._hasTagValue();
        if (actionNode) {
            actionNode.disabled = this._isActive;
        }
        if (inputNode) {
            inputNode.disabled = this._isActive;
        }
        if (selectAllNode) {
            selectAllNode.classList.toggle("inactive", !this._isActive);
            selectAllNode.setAttribute(
                "aria-disabled",
                this._isActive ? "false" : "true"
            );
            if (this._isActive) {
                selectAllNode.removeAttribute("tabindex");
            } else {
                selectAllNode.setAttribute("tabindex", "-1");
            }
        }
        if (this._isActive) {
            node.value =
                this.action === "remove"
                    ? "Untagging images... (click to stop)"
                    : "Tagging images... (click to stop)";
            return;
        }
        node.value =
            this.action === "remove" ? "Start untagging" : "Start tagging";
    }

    _hasTagValue() {
        return Boolean((this._inputNode.value || "").trim());
    }
}

class BulkDeleteEditor extends BulkEditor {
    constructor(hostNode) {
        super(hostNode);
        this._hostNode.addEventListener("submit", (e) =>
            this._evtFormSubmit(e)
        );
        this._hostNode
            .querySelector(".select-all")
            .addEventListener("click", (e) => {
                document
                    .querySelectorAll(".delete-flipper")
                    .forEach((node) => {
                        node.click();
                    });
            });
    }

    _evtFormSubmit(e) {
        e.preventDefault();
        this.dispatchEvent(
            new CustomEvent("deleteSelectedPosts", { detail: {} })
        );
    }

    _evtOpenLinkClick(e) {
        e.preventDefault();
        this.toggleOpen(true);
        this.dispatchEvent(new CustomEvent("open", { detail: {} }));
    }

    _evtCloseLinkClick(e) {
        e.preventDefault();
        this.toggleOpen(false);
        this.dispatchEvent(new CustomEvent("close", { detail: {} }));
    }
}

class BulkAddRelationEditor extends BulkEditor {
    constructor(hostNode) {
        super(hostNode);
    }

    _evtOpenLinkClick(e) {
        e.preventDefault();
        this.toggleOpen(true);
        this.dispatchEvent(new CustomEvent("open", { detail: {} }));
    }

    _evtCloseLinkClick(e) {
        e.preventDefault();
        this.toggleOpen(false);
        this.dispatchEvent(new CustomEvent("close", { detail: {} }));
    }
}

class PostsHeaderView extends events.EventTarget {
    constructor(ctx) {
        super();

        ctx.settings = settings.get();
        this._ctx = ctx;
        this._hostNode = ctx.hostNode;
        views.replaceContent(this._hostNode, template(ctx));

        this._autoCompleteControl = new PostListTagAutoCompleteControl(
            this._queryInputNode,
            {
                confirm: (tag) => {
                    this._autoCompleteControl.replaceSelectedText(
                        misc.escapeSearchTerm(tag.matchingNames[0]),
                        true
                    );
                    this._navigate();
                },
                isNegationAllowed: true,
            }
        );

        search.searchInputNodeFocusHelper(this._queryInputNode);

        /*
        // Focus search input on hover
        this._queryInputNode.addEventListener(
            "mouseover",
            (e) => {
                this.focusQueryInput();
            },
            { passive: true }
        );
		*/

        keyboard.bind("p", () => this._focusFirstPostNode());

        for (let safetyButtonNode of this._safetyButtonNodes) {
            safetyButtonNode.addEventListener("click", (e) =>
                this._evtSafetyButtonClick(e)
            );
        }
        this._formNode.addEventListener("submit", (e) =>
            this._evtFormSubmit(e)
        );

        this._randomSortButtonNode.addEventListener("mousedown", (e) => {
            this._ctx.parameters.r = Math.round(Math.random() * 998) + 1;
            this._handleSortButtonClick(e, "random");
        });

        this._scoreSortButtonNode.addEventListener("mousedown", (e) => {
            this._handleSortButtonClick(e, "score");
        });

        for (let shortcut of this._shortcutButtonNodes) {
            this._setupQueryShortcutButton(shortcut, ctx.parameters.q);
            shortcut.addEventListener("mousedown", (e) =>
                this._evtToggleQueryShortcut(e)
            );
            this.addEventListener("navigate", (e) =>
                this._setupQueryShortcutButton(shortcut, e.detail.parameters.q)
            );
        }

        this._bulkEditors = [];
        if (this._bulkEditTagsNode) {
            this._bulkTagEditor = new BulkTagEditor(this._bulkEditTagsNode, {
                active: Boolean(ctx.parameters.tag),
            });
            this._bulkEditors.push(this._bulkTagEditor);
        }

        if (this._bulkEditSafetyNode) {
            this._bulkSafetyEditor = new BulkSafetyEditor(
                this._bulkEditSafetyNode
            );
            this._bulkEditors.push(this._bulkSafetyEditor);
        }

        if (this._bulkEditDeleteNode) {
            this._bulkDeleteEditor = new BulkDeleteEditor(
                this._bulkEditDeleteNode
            );
            this._bulkEditors.push(this._bulkDeleteEditor);
        }

        if (this._bulkAddRelationNode) {
            this._bulkAddRelationEditor = new BulkAddRelationEditor(
                this._bulkAddRelationNode
            );
            this._bulkEditors.push(this._bulkAddRelationEditor);
        }

        if (this._bulkEditOpenButtonNode) {
            this._bulkEditOpenButtonNode.addEventListener("click", (e) =>
                this._evtOpenBulkEditBtnClick(e)
            );
            this._bulkEditCloseButtonNode.addEventListener("click", (e) =>
                this._evtCloseBulkEditBtnClick(e)
            );
        }


        for (let editor of this._bulkEditors) {
            editor.addEventListener("submit", (e) => {
                this._navigate();
            });
            editor.addEventListener("open", (e) => {
                this._hideBulkEditorsExcept(editor);
                this._navigate();
            });
            editor.addEventListener("close", (e) => {
                this._closeAndShowAllBulkEditors();
                this._navigate();
            });
        }

        if (ctx.parameters.tag && this._bulkTagEditor) {
            this._openBulkEditor(this._bulkTagEditor);
        } else if (ctx.parameters.safety && this._bulkSafetyEditor) {
            this._openBulkEditor(this._bulkSafetyEditor);
        } else if (ctx.parameters.delete && this._bulkDeleteEditor) {
            this._openBulkEditor(this._bulkDeleteEditor);
        } else if (ctx.parameters.relations && this._bulkAddRelationEditor) {
            this._openBulkEditor(this._bulkAddRelationEditor);
        }
    }

    focusSearchInputIfSet() {
        if (this._queryInputNode.value) {
            this.focusQueryInput();
        }
    }

    toggleButtonSelected(button, buttonState) {
        const nodes = {
            random: this._randomSortButtonNode,
            score: this._scoreSortButtonNode,
        };
        nodes[button].classList.toggle("selected", buttonState);
    }

    focusQueryInput() {
        search.focusInputNode(this._queryInputNode);
    }

    get _formNode() {
        return this._hostNode.querySelector("form.search");
    }

    get _safetyButtonNodes() {
        return this._hostNode.querySelectorAll("form .safety");
    }

    get _queryInputNode() {
        return this._hostNode.querySelector("form input[name=search-text]");
    }

    get _randomSortButtonNode() {
        return this._hostNode.querySelector("#randomize-button");
    }

    get _scoreSortButtonNode() {
        return this._hostNode.querySelector("#score-sort-button");
    }

    get _shortcutButtonNodes() {
        return this._hostNode.querySelectorAll("form .query-shortcut");
    }

    get _bulkEditBtnHolderNode() {
        return this._hostNode.querySelector(".bulk-edit-btn-holder");
    }

    get _bulkEditOpenButtonNode() {
        return this._hostNode.querySelector(".bulk-edit-btn.open");
    }

    get _bulkEditCloseButtonNode() {
        return this._hostNode.querySelector(".bulk-edit-btn.close");
    }

    get _bulkEditBlockNode() {
        return this._hostNode.querySelector(".bulk-edit-block");
    }

    get _bulkEditTagsNode() {
        return this._hostNode.querySelector(".bulk-edit-tags");
    }

    get _bulkEditSafetyNode() {
        return this._hostNode.querySelector(".bulk-edit-safety");
    }

    get _bulkEditDeleteNode() {
        return this._hostNode.querySelector(".bulk-edit-delete");
    }

    get _bulkAddRelationNode() {
        return this._hostNode.querySelector(".bulk-add-relation");
    }

    _evtOpenBulkEditBtnClick(e) {
        e.preventDefault();
        this._toggleBulkEditBlock(true);
        this._navigate();
    }

    _evtCloseBulkEditBtnClick(e) {
        e.preventDefault();
        this._toggleBulkEditBlock(false);
        this._closeAndShowAllBulkEditors();
        this._navigate();
    }

    _openBulkEditor(editor) {
        editor.toggleOpen(true);
        this._toggleBulkEditBlock(true);
        this._hideBulkEditorsExcept(editor);
    }

    _toggleBulkEditBlock(open) {
        this._bulkEditBtnHolderNode.classList.toggle("opened", open);
        this._bulkEditBlockNode.classList.toggle("hidden", !open);
    }

    _hideBulkEditorsExcept(editor) {
        for (let otherEditor of this._bulkEditors) {
            if (otherEditor !== editor) {
                otherEditor.toggleOpen(false);
                otherEditor.toggleHide(true);
            }
        }
    }

    _closeAndShowAllBulkEditors() {
        for (let otherEditor of this._bulkEditors) {
            otherEditor.reset();
        }
    }

    _evtSafetyButtonClick(e, url) {
        e.preventDefault();
        e.target.classList.toggle("disabled");
        const safety = e.target.getAttribute("data-safety");
        let browsingSettings = settings.get();
        browsingSettings.listPosts[safety] =
            !browsingSettings.listPosts[safety];
        settings.save(browsingSettings, true);
        this.dispatchEvent(
            new CustomEvent("navigate", {
                detail: {
                    parameters: Object.assign({}, this._ctx.parameters, {
                        tag: null,
                        tagAction: null,
                        offset: 0,
                    }),
                },
            })
        );
    }

    _setupQueryShortcutButton(btn, query) {
        const term = btn.getAttribute("data-term");
        const selectedContent = btn.querySelector(".term-selected");
        const unselectedContent = btn.querySelector(".term-unselected");
        const termInUse = (query || "").includes(term);
        if (termInUse) {
            selectedContent.style.display = "inline-block";
            unselectedContent.style.display = "none";
        } else {
            selectedContent.style.display = "none";
            unselectedContent.style.display = "inline-block";
        }
    }

    _evtToggleQueryShortcut(e) {
        e.preventDefault();
        const term = e.currentTarget.getAttribute("data-term");
        let query = this._ctx.parameters.q
            ? this._ctx.parameters.q.trim()
            : "";
        if (query.includes(term)) {
            query = query.replace(" " + term, "");
            query = query.replace(term, "");
        } else {
            const space = query ? " " : "";
            query += space + term + " ";
        }
        this._queryInputNode.value = query;
        this.dispatchEvent(
            new CustomEvent("navigate", {
                detail: {
                    parameters: Object.assign({}, this._ctx.parameters, {
                        q: query,
                        tag: null,
                        tagAction: null,
                        offset: 0,
                    }),
                },
            })
        );
    }

    _evtFormSubmit(e) {
        e.preventDefault();
        this._navigate();
    }

    _handleSortButtonClick(e, sort) {
        e.preventDefault();
        const query = this._queryInputNode.value.trim();
        let modified = query.replaceAll(/ *sort:(random|score)/gi, "").trim();
        if (sort === "random" || !query.includes(sort)) {
            modified += ` sort:${sort} `;
        }
        this._queryInputNode.value = modified;
        this._navigate();
    }

    _addQuerySpace() {
        const q = this._queryInputNode.value.trim();
        if (q) {
            this._queryInputNode.value = q + " ";
        }
    }

    _navigate() {
        this._autoCompleteControl.hide();
        let parameters = {
            q: this._queryInputNode.value.trim(),
            r: this._ctx.parameters.r,
        };

        // convert falsy values to an empty string "" so that we can correctly compare with the current query
        const prevQuery = this._ctx.parameters.q
            ? this._ctx.parameters.q.trim()
            : "";

        parameters.offset =
            parameters.q === prevQuery ? this._ctx.parameters.offset : 0;
        if (this._bulkTagEditor && this._bulkTagEditor.opened) {
            const tagValue = this._bulkTagEditor.value.trim();
            parameters.tag = tagValue || null;
            parameters.tagAction =
                tagValue && this._bulkTagEditor.action === "remove"
                    ? "remove"
                    : null;
            this._bulkTagEditor.blur();
        } else {
            parameters.tag = null;
            parameters.tagAction = null;
        }
        parameters.safety =
            this._bulkSafetyEditor && this._bulkSafetyEditor.opened
                ? "1"
                : null;
        parameters.delete =
            this._bulkDeleteEditor && this._bulkDeleteEditor.opened
                ? "1"
                : null;
        parameters.relations =
            this._bulkAddRelationEditor && this._bulkAddRelationEditor.opened
                ? this._ctx.parameters.relations || " "
                : null;
        this.dispatchEvent(
            new CustomEvent("navigate", { detail: { parameters: parameters } })
        );
    }

    _focusFirstPostNode() {
        const firstPostNode = document.body.querySelector(
            ".post-list li:first-child a"
        );
        if (firstPostNode) {
            firstPostNode.focus();
        }
    }
}

module.exports = PostsHeaderView;
