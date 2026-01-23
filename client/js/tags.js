"use strict";

const misc = require("./util/misc.js");
const TagCategoryList = require("./models/tag_category_list.js");
const Tag = require("./models/tag.js");
const vars = require("./vars.js");

let _stylesheet = null;
const minLengthForPartialSearch = 3;
const tagNamePattern = new RegExp(vars.tagNameRegex);

function isTagNameValid(name) {
    if (!name) {
        return false;
    }
    if (name === "." || name === "..") {
        return false;
    }
    if (/^\d+$/.test(name)) {
        return false;
    }
    if (
        name.startsWith("-") ||
        name.startsWith("_") ||
        name.endsWith("-") ||
        name.endsWith("_")
    ) {
        return false;
    }
    return tagNamePattern.test(name);
}

function refreshCategoryColorMap() {
    return TagCategoryList.get().then((response) => {
        if (_stylesheet) {
            document.head.removeChild(_stylesheet);
        }
        _stylesheet = document.createElement("style");
        document.head.appendChild(_stylesheet);
        for (let category of response.results) {
            const ruleName = misc.makeCssName(category.name, "tag");
            _stylesheet.sheet.insertRule(
                `.${ruleName} { color: ${category.color}; border-color: ${category.color} }`,
                _stylesheet.sheet.cssRules.length
            );
            _stylesheet.sheet.insertRule(
                `.${ruleName}.selected { color: white; background-color: ${category.color} }`,
                _stylesheet.sheet.cssRules.length
            );
        }
    });
}

function parseTagAndCategory(text) {
    let nameAndCat = text.split(":");
    if (nameAndCat.length > 1) {
        // "cat:my:tag" should parse to category "cat" and tag "my:tag"
        let category = nameAndCat.shift();
        let name = nameAndCat.join(":");
        return { name: name, category: category };
    } else {
        return { name: text, category: null };
    }
}

function resolveTagAndCategory(text) {
    const tagData = parseTagAndCategory(text);
    return _createTagByCategoryAndName(tagData.category, tagData.name);
}

function _createTagByCategoryAndName(category, name) {
    category = category ? category.trim() : "default";
    name = name.trim();
    if (!name) {
        return Promise.reject(new Error("Empty tag name"));
    }
    if (!isTagNameValid(name)) {
        return Promise.reject(
            new Error(
                `Invalid tag name. Must match ${vars.tagNameRegex} and ` +
                    "cannot start or end with '-' or '_'."
            )
        );
    }
    // if tag with this name already exists, existing category will be used
    return Tag.get(name).then(
        (tag) => {
            return Promise.resolve(tag);
        },
        () => {
            const tag = new Tag();
            tag.names = [name];
            tag.category = category;
            return Promise.resolve(tag);
        }
    );
}

function tagListToMatches(tags, options) {
    return [...tags]
        .sort((tag1, tag2) => {
            return tag2.usages - tag1.usages;
        })
        .map((tag) => {
            let cssName = misc.makeCssName(tag.category, "tag");
            tag.matchingNames = tag.names;
            /*
            if (options.isTaggedWith(tag.names[0])) {
                cssName += " disabled";
            }
			*/
            const caption =
                '<span class="' +
                cssName +
                '">' +
                misc.escapeHtml(
                    tag.matchingNames[0] + " (" + tag.postCount + ")"
                ) +
                "</span>";
            return {
                caption: caption,
                value: tag,
            };
        });
}

module.exports = {
    refreshCategoryColorMap: refreshCategoryColorMap,
    parseTagAndCategory: parseTagAndCategory,
    resolveTagAndCategory: resolveTagAndCategory,
    tagListToMatches: tagListToMatches,
    minLengthForPartialSearch: minLengthForPartialSearch,
    isTagNameValid: isTagNameValid,
};
