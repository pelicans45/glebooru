"use strict";

const events = require("../events.js");
const misc = require("../util/misc.js");
const search = require("../util/search.js");
const views = require("../util/views.js");
const TagAutoCompleteControl = require("../controls/tag_auto_complete_control.js");

const template = views.getTemplate("tags-header");

class TagsHeaderView extends events.EventTarget {
    constructor(ctx) {
        super();

        this._hostNode = ctx.hostNode;
        views.replaceContent(this._hostNode, template(ctx));

        if (this._queryInputNode) {
            this._autoCompleteControl = new TagAutoCompleteControl(
                this._queryInputNode,
                {
                    confirm: (tag) =>
                        this._autoCompleteControl.replaceSelectedText(
                            misc.escapeSearchTerm(tag.names[0]),
                            true
                        ),
                }
            );
        }

        search.searchInputNodeFocusHelper(this._queryInputNode);

        this._formNode.addEventListener("submit", (e) => this._evtSubmit(e));
    }

    get _formNode() {
        return this._hostNode.querySelector("form");
    }

    get _queryInputNode() {
        return this._hostNode.querySelector("[name=search-text]");
    }

    _evtSubmit(e) {
        e.preventDefault();
        this._queryInputNode.blur();
        this.dispatchEvent(
            new CustomEvent("navigate", {
                detail: {
                    parameters: {
                        q: this._queryInputNode.value.trim(),
                        page: 1,
                    },
                },
            })
        );
    }
}

module.exports = TagsHeaderView;
