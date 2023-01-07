const sites = require("./config.js").sites;

let universalHostname;

const hostnameFilters = {};

for (const [domain, data] of Object.entries(sites)) {
    if (data.query === "") {
        universalHostname = domain;
    }
    hostnameFilters[domain] = data.query;
}

const isUniversal = location.hostname === universalHostname;
const filterHostnames = objectFlip(hostnameFilters);
const hostnameFilter = getHostnameFilter();
const site = sites[location.hostname];
const excludedTags = new Set(getExcludedTags());

function objectFlip(obj) {
    const ret = {};
    Object.keys(obj).forEach((key) => {
        ret[obj[key]] = key;
    });
    return ret;
}

function getHostnameFilter() {
    return hostnameFilters[location.hostname];
}

function getFilterHostname(tag) {
    return filterHostnames[tag];
}

function getExcludedTags() {
    const tags = [];
    if (isUniversal) {
        return tags;
    }
    for (const [hostname, tag] of Object.entries(hostnameFilters)) {
        if (hostname !== location.hostname && tag) {
            tags.push(tag);
        }
    }
    return tags;
}

function addHostnameFilter(text) {
    if (hostnameFilter) {
        text = `${hostnameFilter} ${text}`;
    }

    return text;
}

function checkHostnameFilterRedirect(post) {
    const tagNames = post.tagNames;
    if (!tagNames) {
        return;
    }

    if (tagNames[0] === hostnameFilter || isUniversal) {
        return;
    }

    const hostname = getFilterHostname(tagNames[0]);
    if (!hostname) {
        return;
    }

    location.hostname = hostname;
    return true;
}

function hostnameExcludedTag(tag) {
    if (excludedTags.has(tag.names[0])) {
        return true;
    }

    for (const implication of tag.implications) {
        if (excludedTags.has(implication.names[0])) {
            return true;
        }
    }

    return false;
}

function hostnameFilterTags(list) {
    const tags = [];
    for (let tag of list) {
        if (!hostnameExcludedTag(tag)) {
            tags.push(tag);
        }
    }

    return tags;
}

module.exports = {
    site: site,
    getHostnameFilter: getHostnameFilter,
    addHostnameFilter: addHostnameFilter,
    checkHostnameFilterRedirect: checkHostnameFilterRedirect,
    hostnameExcludedTag: hostnameExcludedTag,
    hostnameFilterTags: hostnameFilterTags,
};
