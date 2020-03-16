import { RawFormat, Size } from "./format";
export interface Frame {
    nativeFormat(): Promise<RawFormat>;
    size(): Promise<Size>;
    metadata(): Promise<Map<string, string>>;
    canRender(format: RawFormat): Promise<boolean>;
    render(plane: number | number[], format: RawFormat): Promise<ArrayBuffer | ArrayBuffer[]>;
    close(): Promise<void>;
}
export interface Clip {
    metadata(): Promise<Map<string, string>>;
    size: number;
    get(frameno: number): Promise<Frame>;
    close(): Promise<void>;
}
