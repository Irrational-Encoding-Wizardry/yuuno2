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
const messagebus_1 = require("./messagebus");
const connection_1 = require("./connection");
class AsyncConnection {
    constructor(conn) {
        this.conn = conn;
    }
    registerMessageHandler(callback) {
        return this.conn.registerMessageHandler(callback);
    }
    unregisterMessageHandler(token) {
        this.conn.unregisterMessageHandler(token);
    }
    send(message) {
        this.conn.send(message).catch((e) => console.error(e));
        return Promise.resolve();
    }
    close() {
        return __awaiter(this, void 0, void 0, function* () {
            this.conn.close().catch((e) => console.error(e));
            return Promise.resolve();
        });
    }
}
function inlinePipe() {
    let bus1 = new messagebus_1.MessageBus();
    let bus2 = new messagebus_1.MessageBus();
    return {
        first: new connection_1.SimpleConnection(bus1, bus2),
        second: new connection_1.SimpleConnection(bus2, bus1)
    };
}
exports.inlinePipe = inlinePipe;
function pipe() {
    let { first, second } = inlinePipe();
    return {
        first: new AsyncConnection(first),
        second: new AsyncConnection(second)
    };
}
exports.pipe = pipe;
;
//# sourceMappingURL=pipe.js.map