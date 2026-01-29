"use strict";

const api = require("../api.js");
const uri = require("../util/uri.js");
const AbstractList = require("./abstract_list.js");
const Snapshot = require("./snapshot.js");

class SnapshotList extends AbstractList {
    static search(text, offset, limit) {
        const apiPromise = api.get(
                uri.formatApiLink("snapshots", {
                    q: text,
                    offset: offset,
                    limit: limit,
                })
            );
        const returnedPromise = apiPromise.then((response) => {
                return Promise.resolve(
                    Object.assign({}, response, {
                        results: SnapshotList.fromResponse(response.results),
                    })
                );
            });
        returnedPromise.abort = () => apiPromise.abort();
        return returnedPromise;
    }
}

SnapshotList._itemClass = Snapshot;
SnapshotList._itemName = "snapshot";

module.exports = SnapshotList;
