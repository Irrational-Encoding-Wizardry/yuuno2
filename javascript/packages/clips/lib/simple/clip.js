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
class SimpleFrame {
    constructor(nativeFormat, size, metadata, planes) {
        this.__closed = false;
        this._nativeFormat = nativeFormat;
        this._size = size;
        this._metadata = metadata;
        this._planes = planes;
    }
    ensureOpen() {
        if (this.__closed)
            throw new Error("Frame is closed");
    }
    nativeFormat() {
        return __awaiter(this, void 0, void 0, function* () {
            this.ensureOpen();
            return this._nativeFormat;
        });
    }
    size() {
        return __awaiter(this, void 0, void 0, function* () {
            this.ensureOpen();
            return this._size;
        });
    }
    metadata() {
        return __awaiter(this, void 0, void 0, function* () {
            this.ensureOpen();
            return this._metadata;
        });
    }
    canRender(format) {
        return __awaiter(this, void 0, void 0, function* () {
            this.ensureOpen();
            return format === this._nativeFormat;
        });
    }
    render(plane, format) {
        return __awaiter(this, void 0, void 0, function* () {
            this.ensureOpen();
            if (plane instanceof Array)
                return yield Promise.all(plane.map((p) => __awaiter(this, void 0, void 0, function* () { return (yield this.render(p, format)); })));
            return this._planes[plane];
        });
    }
    close() {
        return __awaiter(this, void 0, void 0, function* () {
            this.__closed = true;
        });
    }
}
exports.SimpleFrame = SimpleFrame;
class SimpleClip {
    constructor(frames, metadata, format, size) {
        this._frames = frames;
        this._metadata = metadata;
        this._format = format;
        this._size = size;
    }
    get size() {
        return this._frames.length;
    }
    ;
    metadata() {
        return __awaiter(this, void 0, void 0, function* () {
            return this._metadata;
        });
    }
    get(frameno) {
        return __awaiter(this, void 0, void 0, function* () {
            return new SimpleFrame(this._format, this._size, this._metadata, this._frames[frameno]);
        });
    }
    close() {
        return __awaiter(this, void 0, void 0, function* () { });
    }
}
exports.SimpleClip = SimpleClip;
//# sourceMappingURL=clip.js.map