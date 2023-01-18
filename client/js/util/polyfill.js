/* eslint-disable func-names, no-extend-native */

"use strict";

// non standard
Promise.prototype.always = function (onResolveOrReject) {
    return this.then(onResolveOrReject, (reason) => {
        onResolveOrReject(reason);
        throw reason;
    });
};

// non standard
Number.prototype.between = function (a, b, inclusive) {
    const min = Math.min(a, b);
    const max = Math.max(a, b);
    return inclusive ? this >= min && this <= max : this > min && this < max;
};

// non standard
Promise.prototype.abort = () => {};

// non standard
Date.prototype.addDays = function (days) {
    let dat = new Date(this.valueOf());
    dat.setDate(dat.getDate() + days);
    return dat;
};
