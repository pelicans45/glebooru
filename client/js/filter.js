const hostnameFilters = {
    "glegle.gallery": "glegle",
    "bury.pink": "bury",
};

function getHostnameFilter(text) {
    return hostnameFilters[location.hostname];
}

function addHostnameFilter(text) {
    const hostnameFilter = hostnameFilters[location.hostname];
    if (hostnameFilter) {
        text = `${hostnameFilter} ${text}`;
    }

    return text;
}

module.exports = {
    getHostnameFilter: getHostnameFilter,
    addHostnameFilter: addHostnameFilter,
};
