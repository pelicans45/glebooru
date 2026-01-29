"use strict";

const api = require("../api.js");
const uri = require("../util/uri.js");
const AbstractList = require("./abstract_list.js");
const User = require("./user.js");

class UserList extends AbstractList {
    static search(text, offset, limit) {
        const apiPromise = api.get(
                uri.formatApiLink("users", {
                    q: text,
                    offset: offset,
                    limit: limit,
                })
            );
        const returnedPromise = apiPromise.then((response) => {
                return Promise.resolve(
                    Object.assign({}, response, {
                        results: UserList.fromResponse(response.results),
                    })
                );
            });
        returnedPromise.abort = () => apiPromise.abort();
        return returnedPromise;
    }
}

UserList._itemClass = User;
UserList._itemName = "user";

module.exports = UserList;
