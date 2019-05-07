const direction = {
    NONE: null,
    LEFT: 'left',
    RIGHT: 'right',
    DOWN: 'down',
    UP: 'up'
};

function getSwipeThresholdInPx() {
    // how big is the movement in pixels to be registered as swipe
    return Math.min(screen.width, screen.height) * 0.15;
}

function handleTouchStart(handler, evt) {
    const touchEvent = evt.touches[0];
    if (window.visualViewport.scale === 1) {
        handler._xStart = touchEvent.clientX;
        handler._yStart = touchEvent.clientY;
        handler._startScrollY = window.scrollY;
    }
}

function handleTouchMove(handler, evt) {
    if (!handler._xStart || !handler._yStart) {
        return;
    }
    if (window.visualViewport.scale > 1) {
        handler._xStart = null;
        handler._yStart = null;
        return;
    }

    const xDirection = handler._xStart - evt.touches[0].clientX;
    const yDirection = handler._yStart - evt.touches[0].clientY;
    let threshold = getSwipeThresholdInPx();

    if (Math.abs(xDirection) > Math.abs(yDirection)) {
        if (Math.abs(xDirection) < threshold) {
            return;
        } else if (xDirection > 0) {
            handler._direction = direction.LEFT;
        } else {
            handler._direction = direction.RIGHT;
        }
    } else {
        if (Math.abs(yDirection) < threshold) {
            return;
        } else if (yDirection > 0) {
            handler._direction = direction.UP;
        } else {
            handler._direction = direction.DOWN;
        }
    }
}

function handleTouchEnd(handler, evt) {
    evt.startScrollY = handler._startScrollY;
    switch (handler._direction) {
        case direction.NONE:
            return;
        case direction.LEFT:
            handler._swipeLeftTask(evt);
            break;
        case direction.RIGHT:
            handler._swipeRightTask(evt);
            break;
        case direction.DOWN:
            handler._swipeDownTask(evt);
            break;
        case direction.UP:
            handler._swipeUpTask(evt);
    }

    handler._xStart = null;
    handler._yStart = null;
}

class Touch {
    constructor(target,
                swipeLeft = () => {},
                swipeRight = () => {},
                swipeUp = () => {},
                swipeDown = () => {}) {
        this._target = target;

        this._swipeLeftTask = swipeLeft;
        this._swipeRightTask = swipeRight;
        this._swipeUpTask = swipeUp;
        this._swipeDownTask = swipeDown;

        this._xStart = null;
        this._yStart = null;
        this._direction = direction.NONE;

        this._target.addEventListener('touchstart',
            (evt) => { handleTouchStart(this, evt); });
        this._target.addEventListener('touchmove',
            (evt) => { handleTouchMove(this, evt); });
        this._target.addEventListener('touchend',
            (evt) => { handleTouchEnd(this, evt); });
    }
}

module.exports = Touch;