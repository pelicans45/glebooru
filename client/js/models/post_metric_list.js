'use strict';

const AbstractList = require('./abstract_list.js');
const PostMetric = require('./post_metric.js');

class PostMetricList extends AbstractList {
}

PostMetricList._itemClass = PostMetric;
PostMetricList._itemName = 'postMetric';

module.exports = PostMetricList;
