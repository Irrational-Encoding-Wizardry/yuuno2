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
const pipe = require('../lib/pipe');

describe('@yuuno2/networking', () => {
    let first, second;
    beforeEach(() => {
        ({first, second} = pipe.inlinePipe());
    });

    [["first", ()=>[first, second]], ["second", ()=>[second, first]]].forEach(([which, order]) => {

        describe(`The ${which} side of a pipe`, () => {
            let recv, send;
            beforeEach(() => ([recv, send] = order()));

            let recvList;
            beforeEach(() => {recvList=[]; recv.registerMessageHandler((msg) => recvList.push(msg))});

            let sendList;
            beforeEach(() => {sendList=[]; send.registerMessageHandler((msg) => sendList.push(msg))});
            
            it('should see a message from the other side', async()=>{
                await send.send({text: {a: 1}, blobs: []});
                expect(sendList.length).toBe(0);
                expect(recvList).toStrictEqual([{text: {a: 1}, blobs: []}]);
            });

            it('should see a close from the other side', async()=>{
                await send.close();
                expect(sendList.length).toBe(0);
                expect(recvList).toStrictEqual([null]);
            });
        });
    });
});