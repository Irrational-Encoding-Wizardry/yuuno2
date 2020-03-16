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
const base_1 = require("./base");
const utils_1 = require("./utils");
class _InvocationException extends Error {
    constructor(message) {
        super(message);
        Object.setPrototypeOf(this, new.target.prototype);
    }
}
class RpcServer {
    constructor(conn) {
        this.methodMap = {};
        this.conn = conn;
        const token = this.conn.registerMessageHandler((msg) => __awaiter(this, void 0, void 0, function* () {
            if (msg === null) {
                this.conn.unregisterMessageHandler(token);
                return;
            }
            yield this.invoke(msg);
        }));
    }
    register(name, func) {
        this.methodMap[name] = func;
    }
    close() {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.conn.close();
        });
    }
    send(message) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                yield this.conn.send(message);
            }
            catch (e) {
                if (!(e instanceof base_1.ConnectionClosed))
                    throw e;
            }
        });
    }
    invoke(message) {
        return __awaiter(this, void 0, void 0, function* () {
            if (message.text.id === null || message.text.id === undefined) {
                yield this.send({ text: { id: null, type: 'error', message: 'ID is missing.' }, blobs: [] });
                return;
            }
            let response;
            try {
                response = yield this._invoke(message);
            }
            catch (e) {
                if (e instanceof _InvocationException) {
                    yield this.send({ text: { id: message.text.id, type: 'error', error: e.message }, blobs: [] });
                }
                else if (e instanceof Error) {
                    yield this.send({ text: { id: message.text.id, type: 'error', error: `Error during RPC Invocation:\n${e.name}: ${e.message}\n${e.stack}` }, blobs: [] });
                }
                else {
                    yield this.send({ text: { id: message.text.id, type: 'error', error: `Error during RPC Invocation: ${e.toString()}` }, blobs: [] });
                }
                return;
            }
            yield this.send({ text: { id: message.text.id, type: "response", result: response.text }, blobs: response.blobs });
        });
    }
    _invoke(message) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!message.text.type)
                throw new _InvocationException("Type missing");
            if (message.text.type != "request")
                throw new _InvocationException(`Unknown type: ${message.text.type}`);
            if (!message.text.method || typeof message.text.method != 'string')
                throw new _InvocationException("Method-Name is missing.");
            if (typeof message.text.params != "object")
                throw new _InvocationException("Params must be an object.");
            return yield this._invokeReal(message.text.method, { text: (message.text.params || {}), blobs: message.blobs });
        });
    }
    _invokeReal(name, message) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.methodMap[name])
                throw new _InvocationException(`Unknown method ${name}`);
            const rawResult = this.methodMap[name](message);
            return ((!!rawResult && typeof rawResult.then == 'function') ? (yield rawResult) : rawResult);
        });
    }
}
exports.RpcServer = RpcServer;
class RpcClient {
    static create(conn, functions) {
        const requestMap = {};
        conn.registerMessageHandler((msg) => {
            if (msg === null) {
                for (let handler of Object.values(requestMap)) {
                    handler(null);
                }
            }
            else {
                if (msg.text.id === undefined)
                    return;
                if (typeof msg.text.id != "number")
                    return;
                if (!requestMap[msg.text.id])
                    return;
                requestMap[msg.text.id](msg);
            }
        });
        const result = {
            close() {
                return __awaiter(this, void 0, void 0, function* () {
                    yield conn.close();
                });
            }
        };
        functions.forEach(func => {
            result[func] = (msg, timeout = 0) => __awaiter(this, void 0, void 0, function* () {
                const rqid = RpcClient.openRequestCounter();
                const resultPromise = new Promise((rs, rj) => {
                    requestMap[rqid] = (msg) => {
                        if (msg === null)
                            rj(new Error("Connection is closing."));
                        if ((msg.text.type || "response") === "error") {
                            rj(new Error((msg.text.error || "Remote error while handling exception.")));
                        }
                        else {
                            rs({ text: (msg.text.result || {}), blobs: msg.blobs });
                        }
                    };
                    if (timeout > 0) {
                        setTimeout(() => rj(new Error("Operation timed out")), timeout);
                    }
                });
                yield conn.send({ text: { type: "request", id: rqid, method: func, params: msg.text }, blobs: msg.blobs });
                try {
                    return yield resultPromise;
                }
                finally {
                    delete requestMap[rqid];
                }
            });
        });
        result.prototype = RpcClient;
        return result;
    }
}
exports.RpcClient = RpcClient;
RpcClient.openRequestCounter = utils_1.makeCounter();
//# sourceMappingURL=rpc.js.map