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

import { Clip, Frame } from '../base';
import { RawFormat, Size } from '../format';

export class SimpleFrame implements Frame {
    private _size: Size;
    private _nativeFormat: RawFormat;
    private _metadata: Map<string, string>;
    private _planes: ArrayBuffer[];
    private __closed: boolean = false;

    constructor(nativeFormat: RawFormat, size: Size, metadata: Map<string, string>, planes: ArrayBuffer[]) {
        this._nativeFormat = nativeFormat;
        this._size = size;
        this._metadata = metadata;
        this._planes = planes;
    }

    private ensureOpen() : void {
        if (this.__closed) throw new Error("Frame is closed");
    }

    async nativeFormat(): Promise<RawFormat> {
        this.ensureOpen();
        return this._nativeFormat;
    }

    async size(): Promise<Size> {
        this.ensureOpen();
        return this._size;
    }

    async metadata(): Promise<Map<string, string>> {
        this.ensureOpen();
        return this._metadata;
    }
    async canRender(format: RawFormat): Promise<boolean> {
        this.ensureOpen();
        return format === this._nativeFormat;
    }
    async render(plane: number | number[], format: RawFormat): Promise<ArrayBuffer | ArrayBuffer[]> {
        this.ensureOpen();
        if (plane instanceof Array)
            return await Promise.all(plane.map(async p => (await this.render(p, format)) as ArrayBuffer));
        return this._planes[plane];
    }

    async close(): Promise<void> {
        this.__closed = true;
    }
}

export class SimpleClip implements Clip {

    private _frames: ArrayBuffer[][];
    private _size: Size;
    private _metadata: Map<string, string>;
    private _format: RawFormat;

    constructor(frames: ArrayBuffer[][], metadata: Map<string, string>, format: RawFormat, size: Size) {
        this._frames = frames;
        this._metadata = metadata;
        this._format = format;
        this._size = size;
    }

    get size(): number {
        return this._frames.length;
    };

    async metadata(): Promise<Map<string, string>> {
        return this._metadata;
    }

    async get(frameno: number): Promise<Frame> {
        return new SimpleFrame(this._format, this._size, this._metadata, this._frames[frameno]);
    }

    async close(): Promise<void> {}

    async resize(_: Size) : Promise<null> {
        return null;
    }
}