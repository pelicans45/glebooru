"use strict";

const misc = require("./misc.js");
const keyboard = require("../util/keyboard.js");
const views = require("./views.js");

function focusInputNode(inputNode) {
    const inputLength = inputNode.value.length;
    inputNode.focus();
    inputNode.setSelectionRange(inputLength, inputLength);
}

function searchInputNodeFocusHelper(inputNode) {
    keyboard.bind("q", () => {
        focusInputNode(inputNode);
        return false;
    });
}

module.exports = {
    searchInputNodeFocusHelper: searchInputNodeFocusHelper,
    focusInputNode: focusInputNode,
};
