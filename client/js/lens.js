const config = require("./config.js");
const vars = config.vars;

const hostnameFilters = {};

for (const [domain, data] of Object.entries(config.sites)) {
    hostnameFilters[domain] = data.query;
}

const site = config.sites[location.hostname];

if (!site) {
    throw "Unable to load site data";
}
const name = site.name;

const universalHostname = vars.mainDomain;
const isUniversal = location.hostname === universalHostname;
const filterHostnames = objectFlip(hostnameFilters);
const hostnameFilter = getHostnameFilter();
let excludedTags = new Set(getExcludedTags());
const implies = site.implies || [];

let siteExcludedTags = new Set();
if (site.implies && site.implies.length) {
    siteExcludedTags = new Set(site.implies);
}
excludedTags = new Set([...excludedTags, ...siteExcludedTags]);

const siteTags = [site.query, ...implies];

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

function isHostnameTagName(name) {
    return name === hostnameFilter;
}

function addHostnameFilter(text) {
    if (hostnameFilter) {
        text = `${hostnameFilter} ${text}`;
    }

    return text;
}

function containsFilter(tags) {
	for (const tag of tags) {
		if (tag.names[0] === hostnameFilter) {
			return true;
		}
	}

	return false;

}

function isLensTag(tag) {
    const name = tag.names[0];
    return name === hostnameFilter || siteExcludedTags.has(name);
}

function excludeRedundantTags(tags) {
    return tags.filter((tag) => {
        const name = tag.names[0];
        return name !== hostnameFilter && !siteExcludedTags.has(name);
    });
}

function checkHostnameFilterRedirect(post) {
    return;

    const tagNames = post.tagNames;
    if (!tagNames || isUniversal) {
        return;
    }

    if (tagNames[0] === hostnameFilter || isUniversal) {
        return;
    }

    const hostname = filterHostnames[tagNames[0]];
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
    if (isUniversal) {
        return list;
    }

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
    name: name,
    hostnameFilter: hostnameFilter,
    isUniversal: isUniversal,
    siteTags,
    addHostnameFilter: addHostnameFilter,
    checkHostnameFilterRedirect: checkHostnameFilterRedirect,
    hostnameExcludedTag: hostnameExcludedTag,
    hostnameFilterTags: hostnameFilterTags,
    excludeRedundantTags: excludeRedundantTags,
    isHostnameTagName: isHostnameTagName,
    isLensTag,
    containsFilter,
};
