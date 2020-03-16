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
const utils_1 = require("../utils");
class SimpleScript {
    constructor() {
        this.config = new Map();
        this.ctx = {};
        this.clips = new Map();
        const $self = this;
        this.ctx.register = (name, clip) => $self.clips.set(name, clip);
    }
    setConfig(key, value) {
        return __awaiter(this, void 0, void 0, function* () {
            this.config.set(key, value);
        });
    }
    getConfig(key) {
        return __awaiter(this, void 0, void 0, function* () {
            return this.config.get(key);
        });
    }
    listConfig() {
        return __awaiter(this, void 0, void 0, function* () {
            return utils_1.k2a(this.config);
        });
    }
    run(code) {
        return __awaiter(this, void 0, void 0, function* () {
            if (code instanceof ArrayBuffer) {
                code = String.fromCharCode.apply(null, new Uint16Array(code));
            }
            (() => { eval(code); }).call(this.ctx);
        });
    }
    listClips() {
        return __awaiter(this, void 0, void 0, function* () {
            return utils_1.k2a(this.clips);
        });
    }
    getClip(name) {
        return __awaiter(this, void 0, void 0, function* () {
            return this.clips.get(name);
        });
    }
    close() {
        return __awaiter(this, void 0, void 0, function* () {
            this.ctx = null;
            this.clips = null;
        });
    }
}
exports.SimpleScript = SimpleScript;
//# sourceMappingURL=script.js.map