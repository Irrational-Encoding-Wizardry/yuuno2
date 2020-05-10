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

export { Size, RawFormat, SampleType, ColorFamily } from './format';
export { Clip, Frame } from './base';
export { Script, ScriptProvider, ConfigTypes } from './scripts';

export namespace Simple {
    export const { SimpleClip: Clip, SimpleFrame: Frame } = require('./simple/clip');
    export const { SimpleScript: Script } = require('./simple/script');
}

export { SingleScriptProvider } from './providers/single';
export { NamedScriptProvider } from './providers/named';
export { AggregateError } from './utils';