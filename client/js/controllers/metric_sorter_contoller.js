'use strict';

const api = require('../api.js');
const topNavigation = require('../models/top_navigation.js');
const PostMetric = require('../models/post_metric.js');
const PostMetricRange = require('../models/post_metric_range.js');
const PostList = require('../models/post_list.js');
const MetricSorterView = require('../views/metric_sorter_view.js');
const EmptyView = require('../views/empty_view.js');

class MetricSorterController  {
    constructor(ctx) {
        if (!api.hasPrivilege('posts:view') ||
            !api.hasPrivilege('metrics:edit:posts')) {
            this._view = new EmptyView();
            this._view.showError('You don\'t have privileges to edit post metric values.');
            return;
        }

        topNavigation.activate('posts');
        topNavigation.setTitle('Sorting metrics');

        this._ctx = ctx;
        this._metricNames = (ctx.parameters.metrics || '')
            .split(' ')
            .filter(m => m);
        if (!this._metricNames.length) {
            this._view = new EmptyView();
            this._view.showError('No metrics selected');
            return;
        }
        this._primaryMetricName = this._metricNames[0];

        this._view = new MetricSorterView({
            primaryMetric: this._primaryMetricName,
        });
        this._view.addEventListener('submit', e => this._evtSubmit(e));
        this._view.addEventListener('skip', e => this._evtSkip(e));
        this._view.addEventListener('changeMetric', e => this._evtChangeMetric(e));

        this.startSortingNewPost();
    }

    startSortingNewPost() {
        const metricName = this._primaryMetricName;
        this._getRandomUnsortedPost().then(unsortedPost => {
            this._unsortedPost = unsortedPost;
            this._view.installLeftPost(unsortedPost);
            let range = this._getOrCreateRange(unsortedPost, metricName);
            return this._tryGetMedianPost(metricName, range);
        }).then(medianResponse => {
            if (medianResponse.post) {
                this._view.installRightPost(medianResponse.post);
            } else {
                // No existing metrics, apply the median value
                let exactValue = (medianResponse.range.low + medianResponse.range.high) / 2;
                this._view.showSuccess(`Found exact value: ${exactValue}`);
                this._setExactMetric(this._unsortedPost, metricName, exactValue);
                //TODO continue sorting
            }
        }).catch(error => {
            this._view.showError(error.message)
        });
    }

    _getRandomUnsortedPost() {
        let unsetMetricsQuery = this._metricNames
            .map(m => `${m} -metric:${m}`)
            .join(' ');
        let filterQuery = this._ctx.parameters.query || '';
        let unsetFullQuery = `${filterQuery} ${unsetMetricsQuery} sort:random`;

        return PostList.search(unsetFullQuery, 0, 1, []).then(response => {
            if (!response.results.length) {
                return Promise.reject(new Error('No posts found'));
            } else {
                return Promise.resolve(response.results.at(0));
            }
        });
    }

    _tryGetMedianPost(metric, range) {
        let median_query = `metric-${metric}:${range.low}..${range.high} sort:metric-${metric}`;
        return PostList.getMedian(median_query, []).then(response => {
            return Promise.resolve({
                range: range,
                post: response.results.at(0)
            });
        });
    }

    _getOrCreateRange(post, metricName) {
        let range = post.metricRanges.findByTagName(metricName);
        if (!range) {
            let tag = post.tags.findByName(metricName);
            range = PostMetricRange.create(post.id, tag);
            post.metricRanges.add(range);
        }
        return range;
    }

    _setExactMetric(post, metricName, value) {
        let range = post.metricRanges.findByTagName(metricName);
        if (!range) {
            post.metricRanges.remove(range);
        }
        let tag = post.tags.findByName(metricName);
        let exactMetric = PostMetric.create(post.id, tag);
        exactMetric.value = value;
        post.metrics.add(exactMetric);
    }

    _evtSubmit(e) {
        //TODO update metric ranges
        // Then A) reload median or B) start sorting a new post
    }

    _evtSkip(e) {
        this.startSortingNewPost();
    }

    _evtChangeMetric(e) {
        this._primaryMetricName = e.detail.metricName;
    }
}

module.exports = router => {
    router.enter(
        ['posts', 'metric-sorter'],
        (ctx, next) => {
            ctx.controller = new MetricSorterController(ctx);
        });
};
