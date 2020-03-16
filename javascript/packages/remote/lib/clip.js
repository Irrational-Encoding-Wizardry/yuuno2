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
const networking_1 = require("@yuuno2/networking");
const clips_1 = require("@yuuno2/clips");
const utils_1 = require("./utils");
exports.RemoteClipServer = {
    create(connection, clip) {
        const srv = new networking_1.RpcServer(connection);
        srv.register("metadata", (msg) => __awaiter(this, void 0, void 0, function* () {
            const frameno = msg.text.frame;
            let metadata;
            if (frameno == null) {
                metadata = yield clip.metadata();
            }
            else {
                metadata = yield utils_1.using(yield clip.get(frameno), (frame) => __awaiter(this, void 0, void 0, function* () {
                    return yield frame.metadata();
                }));
            }
            return { text: utils_1.toObject(metadata), blobs: [] };
        }));
        srv.register("length", () => __awaiter(this, void 0, void 0, function* () {
            return { text: { length: clip.size }, blobs: [] };
        }));
        srv.register("size", (msg) => __awaiter(this, void 0, void 0, function* () {
            return utils_1.using(yield clip.get(msg.text.frame), (frame) => __awaiter(this, void 0, void 0, function* () {
                const sz = yield frame.size();
                return { text: [sz.width, sz.height], blobs: [] };
            }));
        }));
        srv.register("format", (msg) => __awaiter(this, void 0, void 0, function* () {
            return utils_1.using(yield clip.get(msg.text.frame), (frame) => __awaiter(this, void 0, void 0, function* () {
                return { text: (yield frame.nativeFormat()).toJSON(), blobs: [] };
            }));
        }));
        srv.register("render", (msg) => __awaiter(this, void 0, void 0, function* () {
            const frameno = msg.text.frame;
            const formatJSON = msg.text.format;
            const planesRaw = msg.text.planes;
            return utils_1.using(yield clip.get(frameno), (frame) => __awaiter(this, void 0, void 0, function* () {
                const frSz = yield frame.size();
                if (planesRaw === undefined || planesRaw === null) {
                    return { text: { 'size': [frSz.width, frSz.height] }, blobs: [] };
                }
                const format = clips_1.RawFormat.fromJSON(formatJSON);
                if (!(yield frame.canRender(format))) {
                    return { text: { 'size': null }, blobs: [] };
                }
                let planes;
                if (!(planesRaw instanceof Array))
                    planes = [planesRaw];
                else
                    planes = planesRaw;
                const rendered = yield frame.render(planes, format);
                return {
                    text: { size: [frSz.width, frSz.height] },
                    blobs: rendered
                };
            }));
        }));
        return srv;
    }
};
//# sourceMappingURL=clip.js.map