import { Clip } from "./base";

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

export type ConfigTypes = Uint8Array|string|number|null;


/**
 * Represents a script that renders one or more clips.
 */
export interface Script {
    /**
     * Sets the configuration with the given key.
     * 
     * @param key    The name of the key.
     * @param value  The new value.
     */
    setConfig(key: string, value: ConfigTypes): Promise<void>;
 
    /**
     * Retrieves the configuration key.
     * 
     * @param key The name of the key.
     */
    getConfig(key: string) : Promise<ConfigTypes>;
 
    /**
     * Retrieves all configuration keys of this script.
     */
    listConfig() : Promise<string[]>;
 
    /**
     * Runs the code at the given script.
     * @param code The code to run.
     */
    run(code: string|ArrayBuffer) : Promise<void>;
 
    /**
     * Lists the clips currently running in the current script.
     */
    listClips() : Promise<string[]>;

    /**
     * Retrieves the clip.
     * 
     * @param name The name of the requested clip.
     */
    getClip(name: string) : Promise<Clip>;

    /**
     * Closes the script and releases all clips derived from this script;
     */
    close(): Promise<void>;
}

export interface ScriptProvider {

    /**
     * Gets a script with the given options.
     * @param options The options for the given provider.
     */
    get(options: object) : Promise<Script>;

    /**
     * Closes the script-provider and releases all clips derived from this provider
     */
    close() : Promise<void>;

}