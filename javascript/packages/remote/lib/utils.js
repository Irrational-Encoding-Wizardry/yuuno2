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
function using(closable, cb) {
    return __awaiter(this, void 0, void 0, function* () {
        let result;
        try {
            result = yield cb(closable);
        }
        finally {
            yield closable.close();
        }
        return result;
    });
}
exports.using = using;
function toObject(map) {
    const obj = {};
    map.forEach((v, k) => obj[k] = v);
    return obj;
}
exports.toObject = toObject;
//# sourceMappingURL=utils.js.map