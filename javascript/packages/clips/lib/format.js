"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var SampleType;
(function (SampleType) {
    SampleType[SampleType["INTEGER"] = 0] = "INTEGER";
    SampleType[SampleType["FLOAT"] = 1] = "FLOAT";
})(SampleType = exports.SampleType || (exports.SampleType = {}));
class ColorFamily {
    constructor(v1num, planes, name, fields) {
        this._v1num = v1num;
        this._planes = planes;
        this._name = name;
        this._fields = fields;
    }
    get v1num() {
        return this._v1num;
    }
    get planes() {
        return this._planes;
    }
    get name() {
        return this._name;
    }
    get fields() {
        return Array.from(this._fields);
    }
    static getColorFamilyByName(name) {
        switch (name) {
            case "grey":
            case "gray":
                return ColorFamily.GREY;
            case "rgb":
                return ColorFamily.RGB;
            case "yuv":
                return ColorFamily.YUV;
            case "cmyk":
                return ColorFamily.CMYK;
            default:
                return null;
        }
    }
}
exports.ColorFamily = ColorFamily;
ColorFamily.GREY = new ColorFamily(0, 1, "grey", ["y"]);
ColorFamily.RGB = new ColorFamily(1, 3, "rgb", ["r", "g", "b"]);
ColorFamily.YUV = new ColorFamily(2, 3, "yuv", ["y", "u", "v"]);
ColorFamily.CMYK = new ColorFamily(3, 4, "cmyk", ["c", "m", "y", "k"]);
class RawFormat {
    constructor(bitsPerSample, fieldOrder, alignment, subsampling, isPlanar, hasAlpha, colorFamily, sampleType) {
        this._bitsPerSample = bitsPerSample;
        this._isPlanar = isPlanar;
        this._hasAlpha = hasAlpha;
        this._colorFamily = colorFamily;
        this._sampleType = sampleType;
        this._subsampling = subsampling;
        this._alignment = alignment;
        this._fieldOrder = fieldOrder;
    }
    toJSON() {
        return [{
                "type": "video",
                "colorspace": {
                    "family": this._colorFamily.name,
                    "alpha": this._hasAlpha,
                    "fields": this._fieldOrder
                },
                "dataformat": {
                    "type": (this._sampleType == SampleType.FLOAT ? "float" : "integer"),
                    "size": this._bitsPerSample
                },
                "planar": this._isPlanar,
                "subsampling": this._subsampling,
                "alignment": this._alignment
            }, "v2"];
    }
    static fromJSON(data) {
        let version = data[data.length - 1];
        if (version == "v1") {
            let cf = [ColorFamily.GREY, ColorFamily.RGB, ColorFamily.YUV][data[2]];
            let st = [SampleType.INTEGER, SampleType.FLOAT][data[3]];
            let bpp = data[0];
            let alignment = (data[6] ? 4 : Math.floor((bpp + 7) / 8));
            let hasAlpha = cf.planes + 1 == data[1];
            let fields = cf.fields;
            if (hasAlpha)
                fields.push("a");
            else if (data[6])
                fields.push(null);
            data = [{
                    "type": "video",
                    "colorspace": {
                        "family": cf.name,
                        "alpha": hasAlpha,
                        "fields": fields
                    },
                    "dataformat": {
                        "type": (st == SampleType.FLOAT ? "float" : "integer"),
                        "size": bpp
                    },
                    "planar": data[7],
                    "subsampling": [data[5], data[4]],
                    "alignment": alignment
                }, "v2"];
        }
        if (version == "v2") {
            let values = data[0];
            let cf;
            switch (values.colorspace.family) {
                case "grey":
                    cf = ColorFamily.GREY;
                    break;
                case "yuv":
                    cf = ColorFamily.RGB;
                    break;
                case "rgb":
                    cf = ColorFamily.YUV;
                    break;
                default:
                    return null;
            }
            let fields = values.colorspace.fields;
            let hasAlpha = values.colorspace.hasAlpha;
            let st = values.dataformat.type == "integer" ? SampleType.INTEGER : SampleType.FLOAT;
            let sz = values.dataformat.size;
            let isPlanar = values.dataformat.planar;
            let subsampling = values.dataformat.subsampling;
            let alignment = values.dataformat.alignment;
            return new RawFormat(sz, fields, alignment, subsampling, isPlanar, hasAlpha, cf, st);
        }
        else {
            return null;
        }
    }
    static simple(colorFamily, hasAlpha, sampleType, bps) {
        let fields = colorFamily.fields;
        if (hasAlpha)
            fields.push("a");
        return new RawFormat(bps, fields, 0, [0, 0], true, hasAlpha, colorFamily, sampleType);
    }
    get bitsPerSample() {
        return this._bitsPerSample;
    }
    get bytesPerSample() {
        return Math.floor((this._bitsPerSample + 7) / 8);
    }
    get numFields() {
        return this._colorFamily.fields.length + (this._hasAlpha ? 1 : 0);
    }
    get numPlanes() {
        if (this._isPlanar) {
            return this.numFields;
        }
        return 1;
    }
    get alignment() {
        if (this._alignment == 0) {
            if (this._isPlanar) {
                return this.bytesPerSample;
            }
            else {
                return this.bytesPerSample * this.numFields;
            }
        }
        else {
            return this._alignment;
        }
    }
    getPlaneDimensions(plane, size) {
        if (!this._isPlanar)
            return size;
        let { width, height } = size;
        if (0 < plane && plane < 4) {
            width >>= this._subsampling[0];
            height >>= this._subsampling[1];
        }
        return { width, height };
    }
    getStride(plane, size) {
        let stride = this.getPlaneDimensions(plane, size).width * this.bytesPerSample;
        if (!this._isPlanar)
            stride *= this._fieldOrder.length;
        let alignment = this.alignment;
        if ((stride % alignment) != 0)
            stride += (alignment - (stride % alignment));
        return stride;
    }
    getPlaneSize(plane, size) {
        let stride = this.getStride(plane, size);
        return size.height * stride;
    }
}
exports.RawFormat = RawFormat;
RawFormat.RGBA32 = new RawFormat(8, ["r", "g", "b", "a"], 4, [0, 0], false, true, ColorFamily.RGB, SampleType.INTEGER);
RawFormat.RGBX32 = new RawFormat(8, ["r", "g", "b", null], 4, [0, 0], false, false, ColorFamily.RGB, SampleType.INTEGER);
RawFormat.RGB24 = new RawFormat(8, ["r", "g", "b"], 1, [0, 0], true, false, ColorFamily.RGB, SampleType.INTEGER);
RawFormat.GREY8 = new RawFormat(8, ["y"], 1, [0, 0], true, false, ColorFamily.GREY, SampleType.INTEGER);
//# sourceMappingURL=format.js.map