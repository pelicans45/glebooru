const hostnameFilters = {
    "glegle.gallery": "glegle",
    "bury.pink": "bury",
};

function getHostnameFilter() {
    return hostnameFilters[location.hostname];
}

module.exports = {
    getHostnameFilter: getHostnameFilter,
};
