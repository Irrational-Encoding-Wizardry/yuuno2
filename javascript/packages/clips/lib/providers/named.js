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
class CloseForwardingScript {
    constructor(parent, onClose) {
        this._parent = parent;
        this._onClose = onClose;
    }
    setConfig(key, value) {
        return __awaiter(this, void 0, void 0, function* () {
            yield this._parent.setConfig(key, value);
        });
    }
    getConfig(key) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this._parent.getConfig(key);
        });
    }
    listConfig() {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this._parent.listConfig();
        });
    }
    run(code) {
        return __awaiter(this, void 0, void 0, function* () {
            yield this._parent.run(code);
        });
    }
    listClips() {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this._parent.listClips();
        });
    }
    getClip(name) {
        return __awaiter(this, void 0, void 0, function* () {
            return yield this._parent.getClip(name);
        });
    }
    close() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                yield this._parent.close();
            }
            finally {
                this._onClose();
            }
        });
    }
}
class NamedScriptProvider {
    constructor(parent, optionName = "name") {
        this._cache = new Map();
        this._parent = parent;
        this._optionName = optionName;
    }
    get(options) {
        return __awaiter(this, void 0, void 0, function* () {
            if (options[this._optionName] === undefined)
                return yield this._parent.get(options);
            const name = options[this._optionName];
            delete options[this._optionName];
            if (this._cache.has(name))
                return this._cache.get(name);
            const script = new CloseForwardingScript(yield this._parent.get(options), () => this._cache.delete(name));
            this._cache.set(name, script);
            return script;
        });
    }
    close() {
        return __awaiter(this, void 0, void 0, function* () {
            const pAry = [];
            const errs = [];
            utils_1.v2a(this._cache).map((p) => __awaiter(this, void 0, void 0, function* () { return yield p.close().then((r) => r, (e) => errs.push(e)); }));
            yield Promise.all(pAry);
            if (errs.length > 0)
                throw new utils_1.AggregateError(errs);
            yield this._parent.close();
        });
    }
}
exports.NamedScriptProvider = NamedScriptProvider;
//# sourceMappingURL=named.js.map