'use strict';

const events = require('../events.js');
const misc = require('../util/misc.js');
const views = require('../util/views.js');
const MetricList = require('../models/metric_list.js');

const mainTemplate = views.getTemplate('metric-header');
const metricItemTemplate = views.getTemplate('metric-header-item');

class MetricHeaderControl extends events.EventTarget {
    constructor(hostNode, ctx) {
        super();
        this._ctx = ctx;
        this._hostNode = hostNode;

        this._headerNode = mainTemplate(ctx);
        this._metricListNode = this._headerNode.querySelector('ul.metric-list');

        this._hostNode.insertBefore(
            this._headerNode, this._hostNode.nextSibling);

        MetricList.loadAll().then(response => {
            this._metrics = response.results;
            this._installMetrics(response.results);
        });
    }

    _installMetrics(metrics) {
        for (let metric of metrics) {
            const node = metricItemTemplate({metric: metric, ctx: this._ctx});
            this._metricListNode.appendChild(node);
        }
    }
}

module.exports = MetricHeaderControl;
