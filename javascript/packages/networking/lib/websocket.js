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
class WebsocketHandler {
    constructor(ws, msgCb) {
        this.ws = ws;
        this.msgCb = msgCb;
        this.setupWebSocket();
    }
    setupWebSocket() {
        this.ws.binaryType = "arraybuffer";
        this.ws.onclose = () => this.msgCb(null);
        this.ws.onmessage = (ev) => {
            if (ev.data instanceof ArrayBuffer)
                WebsocketHandler.fromByteArray(ev.data).forEach((m) => this.msgCb(m));
            else
                this.msgCb({ text: JSON.parse(ev.data), blobs: [] });
        };
    }
    static toByteArray(msg) {
        return null;
    }
    static fromByteArray(ary) {
        return null;
    }
    send(msg) {
        return __awaiter(this, void 0, void 0, function* () {
            if (msg.blobs.length == 0)
                this.ws.send(JSON.stringify(msg.text));
            else
                this.ws.send(WebsocketHandler.toByteArray(msg));
        });
    }
}
//# sourceMappingURL=websocket.js.map