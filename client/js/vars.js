const vars = require("./config.js").vars;
vars.newPostVisibilityThresholdMilliseconds =
    vars.newPostVisibilityThresholdMinutes * 60 * 1000;

module.exports = vars;
