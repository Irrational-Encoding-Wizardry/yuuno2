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

import { RawFormat, Size } from "./format";



/**
 * Represents a frame of a clip.
 */
export interface Frame {

    /**
     * Requests the native format of a frame.
     */
    nativeFormat(): Promise<RawFormat>;

    /**
     * Returns the size of the frame.
     */
    size(): Promise<Size>;

    /**
     * Requests metadata of a frame.
     */
    metadata() : Promise<Map<string, string>>;

    /**
     * Checks if the frame can be rendered into the given format.
     * @param format The requested format.
     */
    canRender(format: RawFormat) : Promise<boolean>;

    /**
     * Renders the given plane(s) of the frame.
     * @param plane  The frame to render.
     * @param format The format to render as.
     */
    render(plane: number|number[], format: RawFormat) : Promise<ArrayBuffer|ArrayBuffer[]>;

    /**
     * Releases the resources associated with the frame.
     */
    close(): Promise<void>;
}


/**
 * Represents an actual clip.
 */
export interface Clip {

    /**
     * Requests the metadata of a frame.
     */
    metadata() : Promise<Map<string, string>>;

    /**
     * Requests the size of a clip.
     */
    size: number;

    /**
     * Returns the frame with the given name.
     */
    get(frameno: number) : Promise<Frame>;

    /**
     * Releases the resources associated with the clip (and frames derived from this clip).
     */
    close(): Promise<void>;

}