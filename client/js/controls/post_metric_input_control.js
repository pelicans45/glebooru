'use strict';

const api = require('../api.js');
const tags = require('../tags.js');
const misc = require('../util/misc.js');
const uri = require('../util/uri.js');
const Tag = require('../models/tag.js');
const TagList = require('../models/tag_list.js');
const PostMetric = require('../models/post_metric.js');
const PostMetricList = require('../models/post_metric_list.js');
const settings = require('../models/settings.js');
const events = require('../events.js');
const views = require('../util/views.js');

const mainTemplate = views.getTemplate('post-metric-input');
const metricNodeTemplate = views.getTemplate('compact-metric-list-item');
const postMetricNodeTemplate = views.getTemplate('compact-post-metric-list-item');

class PostMetricInputControl extends events.EventTarget {
    constructor(hostNode, post) {
        super();
        this._post = post;
        this._hostNode = hostNode;

        // dom
        const editAreaNode = mainTemplate({
            tags: this._post.tags,
            postMetrics: this._post.metrics,
            escapeColons: uri.escapeColons,
        });
        this._editAreaNode = editAreaNode;
        this._metricListNode = editAreaNode.querySelector('ul.compact-unset-metrics');
        this._separatorNode = editAreaNode.querySelector('hr.separator');
        this._postMetricListNode = editAreaNode.querySelector('ul.compact-post-metrics');

        // show
        this._hostNode.style.display = 'none';
        this._hostNode.parentNode.insertBefore(
            this._editAreaNode, hostNode.nextSibling);

        // add existing metrics and post metrics:
        this._refreshContent();
    }

    _refreshContent() {
        this._metricListNode.innerHTML = '';
        for (let tag of this._post.tags.filterMetrics()) {
            const metricNode = this._createMetricNode(tag);
            this._metricListNode.appendChild(metricNode);
        }
        this._separatorNode.style.display =
            this._post.tags.filterMetrics().length && this._post.metrics.length
                ? 'block' : 'none';
        this._postMetricListNode.innerHTML = '';
        for (let pm of this._post.metrics) {
            const postMetricNode = this._createPostMetricNode(pm);
            this._postMetricListNode.appendChild(postMetricNode);
        }
    }

    _createMetricNode(tag) {
        const node = metricNodeTemplate({
            editMode: true,
            tag: tag,
        });
        const createExactNode = node.querySelector('a.create-exact');
        if (this._post.metrics.hasTagName(tag.names[0])) {
            createExactNode.style.display = 'none';
        } else {
            createExactNode.addEventListener('click', e => {
                e.preventDefault();
                this.createPostMetric(tag);
            });
        }
        const createRangeNode = node.querySelector('a.create-range');
        createRangeNode.addEventListener('click', e => {
            e.preventDefault();
            this.createPostMetricRange(tag);
        });
        return node;
    }

    _createPostMetricNode(pm) {
        const tag = this._post.tags.findByName(pm.tagName);
        const node = postMetricNodeTemplate({
            editMode: true,
            postMetric: pm,
            tag: tag,
        });
        return node;
    }

    createPostMetric(tag) {
        this._post.metrics.add(PostMetric.create(this._post.id, tag));
        this._refreshContent();
    }

    createPostMetricRange(tag) {
        //TODO
    }
}

module.exports = PostMetricInputControl;
