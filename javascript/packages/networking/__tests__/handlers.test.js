'use strict';
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

const handlers = require('../lib/handler');

describe('@yuuno2/networking', () => {
    describe('The Handler<T>', () => {
        const handlerList = new handlers.Handler();

        beforeEach(() => {handlerList.clear();});

        it('should give out numeric ids', () => {
            for (let i=0; i<10000; i++) {
                let token = handlerList.register(i);
                expect(typeof token).toBe('number');
            }
        });

        it('should give out unique ids', () => {
            let set = new Set();
            for (let i=0; i<10000; i++) {
                let token = handlerList.register(i);
                set.add(token);
            }
            expect(set.size).toBe(10000);
        });

        it('should call all event handlers on emit', () => {
            let data = [];
            const cb = (v) => data.push(v);
            const token = handlerList.register(cb);
            handlerList.emit(1);
            handlerList.emit(2);
            expect(data).toStrictEqual([1,2]);
        });

        it('should unregister handlers with the given token', () => {
            let data = [];
            const token = handlerList.register(() => data.push(1));
            handlerList.emit(null);
            handlerList.unregister(token);
            handlerList.emit(null);
            expect(data).toStrictEqual([1]);
        })
    })
});
