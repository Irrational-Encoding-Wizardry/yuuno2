"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
class AggregateError extends Error {
    constructor(errors) {
        super("Aggregated Exceptions: \n  " + errors.map(e => AggregateError.makeNice(e)).join("\n"));
        this.errors = errors;
        Object.setPrototypeOf(this, new.target.prototype);
    }
    static makeNice(obj) {
        if (obj instanceof Error) {
            return `  ${obj.name}: ${obj.message}\n    ${obj.stack.split("\n").map(l => "    " + l).join("\n")}`;
        }
        return "  " + obj.toString();
    }
}
exports.AggregateError = AggregateError;
function k2a(map) {
    if (typeof map.keys === 'function')
        return Array.from(map.keys());
    const ary = [];
    map.forEach((_, k) => ary.push(k));
    return ary;
}
exports.k2a = k2a;
function v2a(map) {
    if (typeof map.keys === 'function')
        return Array.from(map.values());
    const ary = [];
    map.forEach(v => ary.push(v));
    return ary;
}
exports.v2a = v2a;
//# sourceMappingURL=utils.js.map