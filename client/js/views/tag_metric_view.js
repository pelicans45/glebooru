'use strict';

const events = require('../events.js');
const api = require('../api.js');
const views = require('../util/views.js');
const Metric = require('../models/metric.js');

const template = views.getTemplate('tag-metric');

class TagMetricView extends events.EventTarget {
    constructor(ctx) {
        super();

        this._tag = ctx.tag;
        this._hostNode = ctx.hostNode;

        if (ctx.tag.metric) {
            ctx.metricMin = ctx.tag.metric.min;
            ctx.metricMax = ctx.tag.metric.max;
        } else {
            // default new values
            ctx.metricMin = 0;
            ctx.metricMax = 10;
        }

        views.replaceContent(this._hostNode, template(ctx));

        this._formNode.addEventListener('submit', e => this._evtSubmit(e));
    }

    _evtSubmit(e) {
        e.preventDefault();
        this.dispatchEvent(new CustomEvent('submit', {
            detail: {
                tag: this._tag,
                metricMin: this._minFieldNode.value,
                metricMax: this._maxFieldNode.value,
            },
        }));
    }

    clearMessages() {
        views.clearMessages(this._hostNode);
    }

    enableForm() {
        views.enableForm(this._formNode);
    }

    disableForm() {
        views.disableForm(this._formNode);
    }

    showSuccess(message) {
        views.showSuccess(this._hostNode, message);
    }

    showError(message) {
        views.showError(this._hostNode, message);
    }

    get _formNode() {
        return this._hostNode.querySelector('form');
    }

    get _minFieldNode() {
        return this._formNode.querySelector('input[name=metric-min]');
    }

    get _maxFieldNode() {
        return this._formNode.querySelector('input[name=metric-max]');
    }
}

module.exports = TagMetricView;
