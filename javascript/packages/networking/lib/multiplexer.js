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
class Multiplexer {
    constructor(conn) {
        this.streams = new Map();
        this.conn = conn;
        this.controlToken = this.conn.registerMessageHandler((msg) => __awaiter(this, void 0, void 0, function* () {
            if (msg.text.type != "message")
                return;
            const target = ((typeof msg.text.target != "string") ? "" : msg.text.target);
            if (!this.streams.has(target)) {
                yield this.conn.send({ text: { target: msg.text.target, type: "close", payload: {} }, blobs: [] });
            }
        }));
    }
    register(name) {
        if (!!this.streams.has(name))
            return this.streams.get(name);
        let ingressBus = new messagebus_1.MessageBus();
        let egressBus = new messagebus_1.MessageBus();
        const closeToken = this.conn.registerMessageHandler((msg) => __awaiter(this, void 0, void 0, function* () {
            if (msg === null) {
                yield ingressBus.close();
            }
            else if (msg.text.target === name) {
                if ((msg.text.type || "message") != "message") {
                    yield ingressBus.close();
                }
                else {
                    if (msg.text.payload === null || msg.text.payload === undefined || typeof msg.text.payload !== 'object') {
                        yield this.conn.send({ text: { target: name, type: 'illegal', payload: {} }, blobs: [] });
                        yield ingressBus.close();
                        egressBus.unregisterMessageHandler(skipEgress);
                        yield egressBus.close();
                        return;
                    }
                    yield ingressBus.send({ text: (msg.text.payload || {}), blobs: msg.blobs });
                }
            }
        }));
        const skipEgress = egressBus.registerMessageHandler((msg) => __awaiter(this, void 0, void 0, function* () {
            if (msg === null) {
                this.streams.delete(name);
                this.conn.unregisterMessageHandler(closeToken);
                yield this.conn.send({ text: { target: name, type: "close", payload: {} }, blobs: [] });
                yield ingressBus.close();
            }
            else {
                yield this.conn.send({ text: { target: name, type: "message", payload: msg.text }, blobs: msg.blobs });
            }
        }));
        let multiplexed = new connection_1.SimpleConnection(ingressBus, egressBus);
        this.streams.set(name, multiplexed);
        return multiplexed;
    }
    close() {
        return __awaiter(this, void 0, void 0, function* () {
            yield Promise.all(__map_values(this.streams).map((s) => s.close().then(() => { }, console.error)));
            this.conn.unregisterMessageHandler(this.controlToken);
            yield this.conn.close();
        });
    }
}
exports.Multiplexer = Multiplexer;
function __map_values(map) {
    if (typeof map.values === 'function')
        return Array.from(map.values());
    let vs = [];
    map.forEach((v, k) => vs.push(v));
    return vs;
}
//# sourceMappingURL=multiplexer.js.map