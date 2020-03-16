/**
 * Yuuno - IPython + VapourSynth
 * Copyright (C) 2020 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

export interface Size {
    width: number,
    height: number
}

export enum SampleType {
    INTEGER = 0,
    FLOAT
}

export class ColorFamily {

    public static GREY: ColorFamily = new ColorFamily(0, 1, "grey", ["y"]);
    public static RGB: ColorFamily  = new ColorFamily(1, 3, "rgb",  ["r", "g", "b"]);
    public static YUV: ColorFamily  = new ColorFamily(2, 3, "yuv",  ["y", "u", "v"]);
    public static CMYK: ColorFamily = new ColorFamily(3, 4, "cmyk", ["c", "m", "y", "k"]);

    private _v1num: number;
    private _planes: number;
    private _name: string;
    private _fields: string[];

    private constructor(v1num: number, planes: number, name: string, fields: string[]) {
        this._v1num = v1num;
        this._planes = planes;
        this._name = name;
        this._fields = fields;
    }

    get v1num(): number {
        return this._v1num;
    }

    get planes(): number {
        return this._planes;
    }

    get name(): string {
        return this._name;
    }

    get fields() : string[] {
        return Array.from(this._fields);
    }

    public static getColorFamilyByName(name: string): ColorFamily {
        switch(name) {
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

export class RawFormat {

    public static RGBA32: RawFormat = new RawFormat(8, ["r", "g", "b", "a"],  4, [0, 0], false, true,  ColorFamily.RGB,  SampleType.INTEGER);
    public static RGBX32: RawFormat = new RawFormat(8, ["r", "g", "b", null], 4, [0, 0], false, false, ColorFamily.RGB,  SampleType.INTEGER);
    public static RGB24: RawFormat  = new RawFormat(8, ["r", "g", "b"],       1, [0, 0], true,  false, ColorFamily.RGB,  SampleType.INTEGER);
    public static GREY8: RawFormat  = new RawFormat(8, ["y"],                 1, [0, 0], true,  false, ColorFamily.GREY, SampleType.INTEGER);

    private _alignment: number;
    private _subsampling: number[]|null;
    private _isPlanar: boolean;
    private _hasAlpha: boolean;
    private _colorFamily: ColorFamily;
    private _sampleType: SampleType;
    private _fieldOrder: string[];
    private _bitsPerSample: number;

    public toJSON(): any {
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

    static fromJSON(data: any[]): RawFormat {
        let version: string = data[data.length-1];
        // Convert V1 format to the new V2 format.
        if (version == "v1") {
            let cf = [ColorFamily.GREY, ColorFamily.RGB, ColorFamily.YUV][data[2]];
            let st = [SampleType.INTEGER, SampleType.FLOAT][data[3]];
            let bpp: number = data[0];
            let alignment: number = (data[6] ? 4 : Math.floor((bpp+7)/8))
            let hasAlpha = cf.planes+1 == data[1];
            let fields: string[] = cf.fields;
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
            }, "v2"]
        }
        
        if (version == "v2") {
            let values: any = data[0];
            let cf: ColorFamily;
            switch(values.colorspace.family) {
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
            let fields: string[] = values.colorspace.fields;
            let hasAlpha: boolean = values.colorspace.hasAlpha;

            let st: SampleType = values.dataformat.type == "integer" ? SampleType.INTEGER : SampleType.FLOAT;
            let sz: number = values.dataformat.size;
            
            let isPlanar: boolean = values.dataformat.planar;
            let subsampling: number[] = values.dataformat.subsampling;
            let alignment: number = values.dataformat.alignment;

            return new RawFormat(sz, fields, alignment, subsampling, isPlanar, hasAlpha, cf, st);
        } else {
            return null;
        }
    }

    public constructor(bitsPerSample: number, fieldOrder: string[], alignment: number, subsampling: number[], isPlanar: boolean, hasAlpha: boolean, colorFamily: ColorFamily, sampleType: SampleType) {
        this._bitsPerSample = bitsPerSample;
        this._isPlanar = isPlanar;
        this._hasAlpha = hasAlpha;
        this._colorFamily = colorFamily;
        this._sampleType = sampleType;
        this._subsampling = subsampling;
        this._alignment = alignment;
        this._fieldOrder = fieldOrder;
    }

    public static simple(colorFamily: ColorFamily, hasAlpha: boolean, sampleType: SampleType, bps: number) : RawFormat {
        let fields = colorFamily.fields;
        if (hasAlpha)
            fields.push("a");
        return new RawFormat(bps, fields, 0, [0, 0], true, hasAlpha, colorFamily, sampleType);
    }

    public get bitsPerSample(): number {
        return this._bitsPerSample;
    }

    public get bytesPerSample(): number {
        return Math.floor((this._bitsPerSample + 7)/8);
    }

    public get numFields() : number {
        return this._colorFamily.fields.length + (this._hasAlpha ? 1 : 0);
    }

    public get numPlanes() : number {
        if (this._isPlanar) {
            return this.numFields;
        }
        return 1;
    }

    public get alignment() : number {
        if (this._alignment == 0) {
            if (this._isPlanar) {
                return this.bytesPerSample;
            } else {
                return this.bytesPerSample * this.numFields;
            }
        } else {
            return this._alignment;
        }
    }

    public getPlaneDimensions(plane: number, size: Size) : Size {
        if (!this._isPlanar)
            return size;
        
        let {width, height} = size;
        if (0 < plane && plane < 4) {
            width >>= this._subsampling[0];
            height >>= this._subsampling[1];
        }
        return {width, height};
    }

    public getStride(plane: number, size: Size) : number {
        let stride = this.getPlaneDimensions(plane, size).width * this.bytesPerSample;
        if (!this._isPlanar)
            stride *= this._fieldOrder.length;
        
        let alignment = this.alignment;
        if ((stride % alignment) != 0)
            stride += (alignment - (stride % alignment));

        return stride;
    }

    public getPlaneSize(plane: number, size: Size) : number {
        let stride = this.getStride(plane, size);
        return size.height * stride;
    }
}