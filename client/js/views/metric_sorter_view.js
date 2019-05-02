'use strict';

const events = require('../events.js');
const views = require('../util/views.js');
const iosCorrectedInnerHeight = require('ios-inner-height');
const PostContentControl = require('../controls/post_content_control.js');

const template = views.getTemplate('metric-sorter');
const sideTemplate = views.getTemplate('metric-sorter-side');

class MetricSorterView extends events.EventTarget {
    constructor(ctx) {
        super();

        this._ctx = ctx;
        this._hostNode = document.getElementById('content-holder');
        views.replaceContent(this._hostNode, template(ctx));
        this._skipButtonNode.addEventListener('click', e => this._evtSkipClick(e));
    }

    installLeftPost(post) {
        this._leftPostControl = this._installPostControl(post, this._leftSideNode);
    }

    installRightPost(post) {
        this._rightPostControl = this._installPostControl(post, this._rightSideNode);
    }

    _installPostControl(post, sideNode) {
        views.replaceContent(
            sideNode,
            sideTemplate(Object.assign({}, this._ctx, {
                post: post,
            })));
        let containerNode = this._getSidePostContainerNode(sideNode);
        return new PostContentControl(
            containerNode,
            post,
            () => {
                // TODO: come up with a more reliable resizing mechanism
                return window.innerWidth < 1000 ?
                    [
                        window.innerWidth,
                        window.innerHeight * 0.6
                    ] : [
                        containerNode.getBoundingClientRect().width,
                        window.innerHeight - containerNode.getBoundingClientRect().top -
                            this._buttonsNode.getBoundingClientRect().height * 2
                    ];
            });
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

    get _leftSideNode() {
        return this._hostNode.querySelector('.left-post-container');
    }

    get _rightSideNode() {
        return this._hostNode.querySelector('.right-post-container');
    }

    get _buttonsNode() {
        return this._hostNode.querySelector('.buttons');
    }

    get _skipButtonNode() {
        return this._hostNode.querySelector('.skip-btn');
    }

    _getSidePostContainerNode(sideNode) {
        return sideNode.querySelector('.post-container');
    }

    _evtSkipClick(e) {
        e.preventDefault();
        this.dispatchEvent(new CustomEvent('skip'));
    }
}

module.exports = MetricSorterView;
