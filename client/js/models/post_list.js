'use strict';

const settings = require('../models/settings.js');
const api = require('../api.js');
const uri = require('../util/uri.js');
const AbstractList = require('./abstract_list.js');
const Post = require('./post.js');

class PostList extends AbstractList {
    static getAround(id, searchQuery, cachenumber) {
        return api.get(
            uri.formatApiLink(
                'post', id, 'around', {
                    query: PostList._decorateSearchQuery(searchQuery || ''),
                    fields: 'id',
                    cachenumber: cachenumber,
                }));
    }

    static search(text, offset, limit, fields, cachenumber) {
        return api.get(
                uri.formatApiLink(
                    'posts', {
                        query: PostList._decorateSearchQuery(text || ''),
                        offset: offset,
                        limit: limit,
                        fields: fields.join(','),
                        cachenumber: cachenumber,
                    }))
            .then(response => {
                return Promise.resolve(Object.assign(
                    {},
                    response,
                    {results: PostList.fromResponse(response.results)}));
            });
    }

    static getMedian(text, fields) {
        return api.get(
            uri.formatApiLink(
                'posts', 'median', {
                    query: PostList._decorateSearchQuery(text || ''),
                    fields: fields.join(','),
                }))
            .then(response => {
                return Promise.resolve(Object.assign(
                    {},
                    response,
                    {results: PostList.fromResponse(response.results)}));
            });
    }

    static _decorateSearchQuery(text) {
        const browsingSettings = settings.get();
        const disabledSafety = [];
        if (api.safetyEnabled()) {
            for (let key of Object.keys(browsingSettings.listPosts)) {
                if (browsingSettings.listPosts[key] === false) {
                    disabledSafety.push(key);
                }
            }
            if (disabledSafety.length) {
                text = `-rating:${disabledSafety.join(',')} ${text}`;
            }
        }
        return text.trim();
    }

}

PostList._itemClass = Post;
PostList._itemName = 'post';

module.exports = PostList;
