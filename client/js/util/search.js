"use strict";

const misc = require("./misc.js");
const keyboard = require("../util/keyboard.js");
const views = require("./views.js");

function searchInputNodeFocusHelper(inputNode) {
    keyboard.bind("q", () => {
        inputNode.focus();
        inputNode.setSelectionRange(
            inputNode.value.length,
            inputNode.value.length
        );
        return false;
    });
}

module.exports = {
    searchInputNodeFocusHelper: searchInputNodeFocusHelper,
};
