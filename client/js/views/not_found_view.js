"use strict";

const views = require("../util/views.js");

const template = views.getTemplate("not-found");

class NotFoundView {
    constructor(path) {
		if (path.includes("/discord")) {
			location.href = "/discord/";
			return;
		}

        this._hostNode = document.getElementById("content-holder");

        const sourceNode = template({ path: path });
        views.replaceContent(this._hostNode, sourceNode);
        views.syncScrollPosition();
    }
}

module.exports = NotFoundView;
