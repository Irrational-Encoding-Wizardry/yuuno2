import { Clip, Frame } from '../base';
import { RawFormat, Size } from '../format';
export declare class SimpleFrame implements Frame {
    private _size;
    private _nativeFormat;
    private _metadata;
    private _planes;
    private __closed;
    constructor(nativeFormat: RawFormat, size: Size, metadata: Map<string, string>, planes: ArrayBuffer[]);
    private ensureOpen;
    nativeFormat(): Promise<RawFormat>;
    size(): Promise<Size>;
    metadata(): Promise<Map<string, string>>;
    canRender(format: RawFormat): Promise<boolean>;
    render(plane: number | number[], format: RawFormat): Promise<ArrayBuffer | ArrayBuffer[]>;
    close(): Promise<void>;
}
export declare class SimpleClip implements Clip {
    private _frames;
    private _size;
    private _metadata;
    private _format;
    constructor(frames: ArrayBuffer[][], metadata: Map<string, string>, format: RawFormat, size: Size);
    get size(): number;
    metadata(): Promise<Map<string, string>>;
    get(frameno: number): Promise<Frame>;
    close(): Promise<void>;
}
