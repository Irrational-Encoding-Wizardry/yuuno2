"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
class ConnectionClosed extends Error {
    constructor(message) {
        super(message);
        Object.setPrototypeOf(this, new.target.prototype);
    }
}
exports.ConnectionClosed = ConnectionClosed;
//# sourceMappingURL=base.js.map