const hostnameFilters = {
    "glegle.gallery": "glegle",
    "bury.pink": "bury",
};

const filterHostnames = objectFlip(hostnameFilters);

const excludedTags = new Set(getExcludedTags());

const hostnameFilter = getHostnameFilter();

const universalHostname = "a.com";

function objectFlip(obj) {
    const ret = {};
    Object.keys(obj).forEach((key) => {
        ret[obj[key]] = key;
    });
    return ret;
}

function isUniversalHostname() {
    return location.hostname === universalHostname;
}

function getHostnameFilter() {
    return hostnameFilters[location.hostname];
}

function getFilterHostname(tag) {
    return filterHostnames[tag];
}

function getExcludedTags() {
    const tags = [];
    if (isUniversalHostname()) {
        return tags;
    }
    for (const [hostname, tag] of Object.entries(hostnameFilters)) {
        if (hostname !== location.hostname) {
            tags.push(tag);
        }
    }
    return tags;
}

function addHostnameFilter(text) {
    const hostnameFilter = hostnameFilters[location.hostname];
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

    if (tagNames[0] === hostnameFilter || isUniversalHostname()) {
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
    for (const name of tag.names) {
        if (excludedTags.has(name)) {
            return true;
        }
    }

    for (const implication of tag.implications) {
        for (const name of implication.names) {
            if (excludedTags.has(name)) {
                return true;
            }
        }
    }

    return false;
}

/*
function hostnameExcludedImplication(tag) {
    for (const name of tag.names) {
        if (excludedTags.has(name)) {
            return true;
        }
    }

    for (const implication of tag.implications) {
        for (const name of implication.names) {
            if (excludedTags.has(name)) {
                return true;
            }
        }
    }

    return false;
}
*/

function hostnamefilterTags(list) {
    const tags = [];
    for (let tag of list) {
        if (!hostnameExcludedTag(tag)) {
            tags.push(tag);
        }
    }

    return tags;
}

module.exports = {
    getHostnameFilter: getHostnameFilter,
    addHostnameFilter: addHostnameFilter,
    checkHostnameFilterRedirect: checkHostnameFilterRedirect,
    hostnameExcludedTag: hostnameExcludedTag,
    hostnamefilterTags: hostnamefilterTags,
};
