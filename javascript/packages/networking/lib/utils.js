"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.makeCounter = (function (start = 0, step = 1) {
    return function counter() {
        let count = start;
        return function __increment() {
            const previous = count;
            count = count + step;
            return previous;
        };
    };
})();
//# sourceMappingURL=utils.js.map