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
const { RawFormat, ColorFamily, SampleType } = require('../lib/format');


describe('@yuuno2/clips', ()=>{
    describe('RawFormat', () => {
        it('should calculate bytes per sample correctly', () => {
            for (let i = 1; i<8; i++) {
                expect(RawFormat.simple(ColorFamily.GREY, false, SampleType.INTEGER, (i*8)-1).bytesPerSample).toBe(i);
                expect(RawFormat.simple(ColorFamily.GREY, false, SampleType.INTEGER, (i*8)  ).bytesPerSample).toBe(i);
                expect(RawFormat.simple(ColorFamily.GREY, false, SampleType.INTEGER, (i*8)+1).bytesPerSample).toBe(i+1);
            }
        });
        it('should calculate the component count correctly', () => {
            expect(new RawFormat(8, ["y"], 0, [], true, false, ColorFamily.GREY, SampleType.INTEGER).numFields).toBe(1);
            expect(new RawFormat(8, ["y", "a"], 0, [], true, true, ColorFamily.GREY, SampleType.INTEGER).numFields).toBe(2);
            expect(new RawFormat(8, ["r", "g", "b"], 0, [], true, false, ColorFamily.RGB, SampleType.INTEGER).numFields).toBe(3);
            expect(new RawFormat(8, ["r", "g", "b", null], 0, [], true, false, ColorFamily.RGB, SampleType.INTEGER).numFields).toBe(3);
            expect(new RawFormat(8, ["r", "g", "b", "a"], 0, [], true, true, ColorFamily.RGB, SampleType.INTEGER).numFields).toBe(4);
            expect(new RawFormat(8, ["c", "m", "y", "k"], 0, [], true, false, ColorFamily.CMYK, SampleType.INTEGER).numFields).toBe(4);
            expect(new RawFormat(8, ["c", "m", "y", "k", "a"], 0, [], true, true, ColorFamily.CMYK, SampleType.INTEGER).numFields).toBe(5);
        });
        it('should calculate the plane count correctly', () => {
            expect(new RawFormat(8, ["y"], 0, [], true, false, ColorFamily.GREY, SampleType.INTEGER).numPlanes).toBe(1);
            expect(new RawFormat(8, ["y", "a"], 0, [], true, true, ColorFamily.GREY, SampleType.INTEGER).numPlanes).toBe(2);
            expect(new RawFormat(8, ["r", "g", "b"], 0, [], true, false, ColorFamily.RGB, SampleType.INTEGER).numPlanes).toBe(3);
            expect(new RawFormat(8, ["r", "g", "b", null], 0, [], true, false, ColorFamily.RGB, SampleType.INTEGER).numPlanes).toBe(3);
            expect(new RawFormat(8, ["r", "g", "b", "a"], 0, [], true, true, ColorFamily.RGB, SampleType.INTEGER).numPlanes).toBe(4);
            expect(new RawFormat(8, ["c", "m", "y", "k"], 0, [], true, false, ColorFamily.CMYK, SampleType.INTEGER).numPlanes).toBe(4);
            expect(new RawFormat(8, ["c", "m", "y", "k", "a"], 0, [], true, true, ColorFamily.CMYK, SampleType.INTEGER).numPlanes).toBe(5);

            expect(new RawFormat(8, ["y"], 0, [], false, false, ColorFamily.GREY, SampleType.INTEGER).numPlanes).toBe(1);
            expect(new RawFormat(8, ["y", "a"], 0, [], false, true, ColorFamily.GREY, SampleType.INTEGER).numPlanes).toBe(1);
            expect(new RawFormat(8, ["r", "g", "b"], 0, [], false, false, ColorFamily.RGB, SampleType.INTEGER).numPlanes).toBe(1);
            expect(new RawFormat(8, ["r", "g", "b", null], 0, [], false, false, ColorFamily.RGB, SampleType.INTEGER).numPlanes).toBe(1);
            expect(new RawFormat(8, ["r", "g", "b", "a"], 0, [], false, true, ColorFamily.RGB, SampleType.INTEGER).numPlanes).toBe(1);
            expect(new RawFormat(8, ["c", "m", "y", "k"], 0, [], false, false, ColorFamily.CMYK, SampleType.INTEGER).numPlanes).toBe(1);
            expect(new RawFormat(8, ["c", "m", "y", "k", "a"], 0, [], false, true, ColorFamily.CMYK, SampleType.INTEGER).numPlanes).toBe(1);
        });
        it('should calculate the implicit alignment correctly', ()=>{
            expect(new RawFormat(8, ["y"], 0, [0, 0], true, false, ColorFamily.GREY, SampleType.INTEGER).alignment).toBe(1);
            expect(new RawFormat(8, ["r", "g", "b"], 0, [0, 0], true, false, ColorFamily.RGB, SampleType.INTEGER).alignment).toBe(1);
            expect(new RawFormat(10, ["r", "g", "b"], 0, [0, 0], true, false, ColorFamily.RGB, SampleType.INTEGER).alignment).toBe(2);
            expect(new RawFormat(8, ["r", "g", "b"], 0, [0, 0], false, false, ColorFamily.RGB, SampleType.INTEGER).alignment).toBe(3);
            expect(new RawFormat(16, ["r", "g", "b"], 0, [0, 0], false, false, ColorFamily.RGB, SampleType.INTEGER).alignment).toBe(6);
        });
        it('should calculate the plane dimensions correctly', ()=>{
            const sz = {width: 100, height: 200};
            expect(new RawFormat(8, ["y", "u", "v"], 0, [0, 0], true, false, ColorFamily.YUV, SampleType.INTEGER).getPlaneDimensions(0, sz)).toStrictEqual({width: 100, height: 200});
            expect(new RawFormat(8, ["y", "u", "v"], 0, [0, 0], true, false, ColorFamily.YUV, SampleType.INTEGER).getPlaneDimensions(1, sz)).toStrictEqual({width: 100, height: 200});
            expect(new RawFormat(8, ["y", "u", "v"], 0, [0, 0], true, false, ColorFamily.YUV, SampleType.INTEGER).getPlaneDimensions(2, sz)).toStrictEqual({width: 100, height: 200});

            expect(new RawFormat(8, ["y", "u", "v"], 0, [1, 0], true, false, ColorFamily.YUV, SampleType.INTEGER).getPlaneDimensions(0, sz)).toStrictEqual({width: 100, height: 200});
            expect(new RawFormat(8, ["y", "u", "v"], 0, [1, 0], true, false, ColorFamily.YUV, SampleType.INTEGER).getPlaneDimensions(1, sz)).toStrictEqual({width:  50, height: 200});
            expect(new RawFormat(8, ["y", "u", "v"], 0, [1, 0], true, false, ColorFamily.YUV, SampleType.INTEGER).getPlaneDimensions(2, sz)).toStrictEqual({width:  50, height: 200});

            expect(new RawFormat(8, ["y", "u", "v"], 0, [1, 1], true, false, ColorFamily.YUV, SampleType.INTEGER).getPlaneDimensions(0, sz)).toStrictEqual({width: 100, height: 200});
            expect(new RawFormat(8, ["y", "u", "v"], 0, [1, 1], true, false, ColorFamily.YUV, SampleType.INTEGER).getPlaneDimensions(1, sz)).toStrictEqual({width:  50, height: 100});
            expect(new RawFormat(8, ["y", "u", "v"], 0, [1, 1], true, false, ColorFamily.YUV, SampleType.INTEGER).getPlaneDimensions(2, sz)).toStrictEqual({width:  50, height: 100});
        });
        it('should calculate the stride correctly', ()=>{
            const sz = {width: 100, height: 200};
            expect(new RawFormat(8, ["y"], 0, [0, 0], true, false, ColorFamily.GREY, SampleType.INTEGER).getStride(0, sz)).toBe(100);
            expect(new RawFormat(9, ["y"], 0, [0, 0], true, false, ColorFamily.GREY, SampleType.INTEGER).getStride(0, sz)).toBe(200);

            expect(new RawFormat(8, ["r", "g", "b"], 0, [0, 0], true, false, ColorFamily.RGB, SampleType.INTEGER).getStride(0, sz)).toBe(100);
            expect(new RawFormat(8, ["r", "g", "b", "a"], 0, [0, 0], true, true, ColorFamily.RGB, SampleType.INTEGER).getStride(0, sz)).toBe(100);

            expect(new RawFormat(8, ["r", "g", "b"], 0, [0, 0], false, false, ColorFamily.RGB, SampleType.INTEGER).getStride(0, sz)).toBe(300);
            expect(new RawFormat(8, ["r", "g", "b", null], 4, [0, 0], false, false, ColorFamily.RGB, SampleType.INTEGER).getStride(0, sz)).toBe(400);
            expect(new RawFormat(8, ["r", "g", "b", "a"], 4, [0, 0], false, true, ColorFamily.RGB, SampleType.INTEGER).getStride(0, sz)).toBe(400);
        })
    });
});