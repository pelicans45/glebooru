"use strict";

function formatApiLink(...values) {
    let parts = [];
    for (let value of values) {
        if (value.constructor === Object) {
            // assert this is the last piece
            let variableParts = [];
            for (let key of Object.keys(value)) {
                if (value[key]) {
                    variableParts.push(
                        key + "=" + encodeURIComponent(value[key].toString().trim())
                    );
                }
            }
            if (variableParts.length) {
                parts.push("?" + variableParts.join("&"));
            }
            break;
        } else {
            parts.push(encodeURIComponent(value.toString()));
        }
    }
    return "/" + parts.join("/");
}

function escapeParam(text) {
    return encodeURIComponent(text);
}

function unescapeParam(text) {
    return decodeURIComponent(text);
}

function getPostsQuery(parameters) {
    let normalQuery = parameters.q ? parameters.q.trim() : "";
    if (!parameters.metrics) {
        return normalQuery;
    }
    let metricQuery = parameters.metrics
        .split(" ") //see metric_header_control
        .filter((m) => m)
        .map((m) => m + " sort:metric-" + m)
        .join(" ");
    return normalQuery + " " + metricQuery;
}

function formatClientLink(...values) {
    let parts = [];
    for (let value of values) {
        if (value.constructor === Object) {
            // assert this is the last piece
            let variableParts = [];
            for (let key of Object.keys(value)) {
                if (value[key]) {
                    variableParts.push(
                        key + "=" + escapeParam(value[key].toString().trim())
                    );
                }
            }
            if (variableParts.length) {
                parts.push(variableParts.join(";"));
            }
            break;
        } else {
            parts.push(escapeParam(value.toString()));
        }
    }
    return parts.join("/");
}

function formatPostsLink(...values) {
    let parts = [];
    for (let value of values) {
        if (value.constructor === Object) {
            // assert this is the last piece
            let variableParts = [];
            for (let key of Object.keys(value)) {
                if (key === "q") {
                    if (value[key]) {
                        parts.unshift(
                            escapeParam(value[key].toString().trim())
                                .replace(/%20/g, "+")
                                .replace(/%3A/g, ":")
                        );
                    }
                    continue;
                }

                if (value[key]) {
                    variableParts.push(
                        key + "=" + escapeParam(value[key].toString().trim())
                    );
                }
            }
            if (variableParts.length) {
                parts.push(variableParts.join(";"));
            }
            break;
        } else {
            parts.push(escapeParam(value.toString()));
        }
    }
    return "/" + parts.join(";");
}

function extractHostname(url) {
    // https://stackoverflow.com/a/23945027
    return url
        .split("/")
        [url.indexOf("//") > -1 ? 2 : 0].split(":")[0]
        .split("?")[0];
}

function extractRootDomain(url) {
    // https://stackoverflow.com/a/23945027
    let domain = extractHostname(url);
    let splitArr = domain.split(".");
    let arrLen = splitArr.length;

    // if there is a subdomain
    if (arrLen > 2) {
        domain = splitArr[arrLen - 2] + "." + splitArr[arrLen - 1];
        // check to see if it's using a Country Code Top Level Domain (ccTLD) (i.e. ".me.uk")
        if (
            splitArr[arrLen - 2].length === 2 &&
            splitArr[arrLen - 1].length === 2
        ) {
            // this is using a ccTLD
            domain = splitArr[arrLen - 3] + "." + domain;
        }
    }
    return domain;
}

function escapeTagName(text) {
    return text.replace(/:/g, "\\:").replace(/\./g, "\\.");
}

module.exports = {
    getPostsQuery: getPostsQuery,
    formatClientLink: formatClientLink,
    formatPostsLink: formatPostsLink,
    formatApiLink: formatApiLink,
    escapeTagName: escapeTagName,
    escapeParam: escapeParam,
    unescapeParam: unescapeParam,
    extractHostname: extractHostname,
    extractRootDomain: extractRootDomain,
};
