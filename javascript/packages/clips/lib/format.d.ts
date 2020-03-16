export interface Size {
    width: number;
    height: number;
}
export declare enum SampleType {
    INTEGER = 0,
    FLOAT = 1
}
export declare class ColorFamily {
    static GREY: ColorFamily;
    static RGB: ColorFamily;
    static YUV: ColorFamily;
    static CMYK: ColorFamily;
    private _v1num;
    private _planes;
    private _name;
    private _fields;
    private constructor();
    get v1num(): number;
    get planes(): number;
    get name(): string;
    get fields(): string[];
    static getColorFamilyByName(name: string): ColorFamily;
}
export declare class RawFormat {
    static RGBA32: RawFormat;
    static RGBX32: RawFormat;
    static RGB24: RawFormat;
    static GREY8: RawFormat;
    private _alignment;
    private _subsampling;
    private _isPlanar;
    private _hasAlpha;
    private _colorFamily;
    private _sampleType;
    private _fieldOrder;
    private _bitsPerSample;
    toJSON(): any;
    static fromJSON(data: any[]): RawFormat;
    constructor(bitsPerSample: number, fieldOrder: string[], alignment: number, subsampling: number[], isPlanar: boolean, hasAlpha: boolean, colorFamily: ColorFamily, sampleType: SampleType);
    static simple(colorFamily: ColorFamily, hasAlpha: boolean, sampleType: SampleType, bps: number): RawFormat;
    get bitsPerSample(): number;
    get bytesPerSample(): number;
    get numFields(): number;
    get numPlanes(): number;
    get alignment(): number;
    getPlaneDimensions(plane: number, size: Size): Size;
    getStride(plane: number, size: Size): number;
    getPlaneSize(plane: number, size: Size): number;
}
