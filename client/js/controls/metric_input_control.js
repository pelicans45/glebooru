'use strict';

const api = require('../api.js');
const tags = require('../tags.js');
const misc = require('../util/misc.js');
const uri = require('../util/uri.js');
const Tag = require('../models/tag.js');
const TagList = require('../models/tag_list.js');
const PostMetricList = require('../models/post_metric_list.js');
const settings = require('../models/settings.js');
const events = require('../events.js');
const views = require('../util/views.js');

const template = views.getTemplate('metric-input');

class MetricInputControl extends events.EventTarget {
    constructor(hostNode, tagList, postMetricList) {
        super();
        this.tags = tagList;
        this.postMetrics = postMetricList;
        this._hostNode = hostNode;

        // dom
        this._editAreaNode = template({
            tags: this.tags,
            postMetrics: this.postMetrics,
            escapeColons: uri.escapeColons,
        });

        // show
        this._hostNode.style.display = 'none';
        this._hostNode.parentNode.insertBefore(
            this._editAreaNode, hostNode.nextSibling);
    }
}

module.exports = MetricInputControl;
