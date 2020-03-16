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
const handler_1 = require("./handler");
const base_1 = require("./base");
class MessageBus {
    constructor() {
        this.handlers = new handler_1.Handler();
    }
    registerMessageHandler(callback) {
        if (this.handlers === null) {
            callback(null);
            return null;
        }
        ;
        return this.handlers.register(callback);
    }
    unregisterMessageHandler(token) {
        if (this.handlers === null)
            return;
        this.handlers.unregister(token);
    }
    send(message) {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.handlers === null)
                throw new base_1.ConnectionClosed("The connection is closed.");
            if (message === null)
                throw new TypeError("Use close() to close instead.");
            yield this.handlers.emit(message);
        });
    }
    close() {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.handlers === null)
                return;
            yield this.handlers.emit(null);
            this.handlers.clear();
            this.handlers = null;
        });
    }
}
exports.MessageBus = MessageBus;
//# sourceMappingURL=messagebus.js.map