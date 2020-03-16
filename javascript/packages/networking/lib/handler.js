"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const utils_1 = require("./utils");
class AggregateError extends Error {
    constructor(errors) {
        super("Aggregated Exceptions from Handler: \n  " + errors.map(e => AggregateError.makeNice(e)).join("\n"));
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
class Handler {
    constructor() {
        this.handlers = {};
    }
    register(cb) {
        const newId = Handler.idCounter();
        this.handlers[newId] = cb;
        return newId;
    }
    unregister(token) {
        delete this.handlers[token];
    }
    emit(ev) {
        return __awaiter(this, void 0, void 0, function* () {
            let errors = [];
            let asyncEmits = [];
            for (let cb of Object.values(this.handlers)) {
                let res = undefined;
                try {
                    res = cb(ev);
                }
                catch (e) {
                    errors.push(e);
                    continue;
                }
                if (res instanceof Promise || (!!res && typeof res.then === 'function')) {
                    asyncEmits.push(res.then(() => { }, (err) => errors.push(err)));
                }
                else if (res instanceof Error) {
                    errors.push(res);
                }
            }
            if (asyncEmits.length > 0) {
                yield Promise.all(asyncEmits);
            }
            this.propagateError(errors);
        });
    }
    propagateError(errors) {
        if (errors.length == 0)
            return;
        throw new AggregateError(errors);
    }
    clear() {
        this.handlers = {};
    }
}
exports.Handler = Handler;
Handler.errorHandler = null;
Handler.idCounter = utils_1.makeCounter();
//# sourceMappingURL=handler.js.map