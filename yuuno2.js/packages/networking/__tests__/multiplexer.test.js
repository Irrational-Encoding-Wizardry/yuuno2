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

const bus = require('../lib/messagebus');
const connection = require('../lib/connection');
const base = require('../lib/base');
const pipe = require('../lib/pipe');
const mp = require('../lib/multiplexer');

describe('@yuuno2/networking', () => {

    describe('The Multiplexer', () => {
        let received;
        let send;
        let multiplexer;

        beforeEach(() => {
            received = [];
            const {first, second} = pipe.inlinePipe();
            second.registerMessageHandler((msg) => {
                received.push(msg)
            });
            send = async (msg) => await second.send(msg);
            multiplexer = new mp.Multiplexer(first);
        });

        describe('when it receives a message', () => {
            it('should automatically close connections that are unknown', async () => {
                await send({text: {type: "message", target: "unknown", payload: {}, blobs: []}});
                expect(received).toStrictEqual([{text: {type: "close", target: "unknown", payload: {}}, blobs: []}])
            });

            describe('on a known connection', () => {
                let child;
                let receivedChild;

                beforeEach(() => {
                    receivedChild = [];
                    child = multiplexer.register("known");
                    child.registerMessageHandler((msg) => receivedChild.push(msg));
                });

                it('should forward messages unwrapped', async() => {
                    await send({text: {type: "message", target: "known", payload: {test: 1}}, blobs: []});
                    expect(receivedChild).toStrictEqual([{text: {test: 1}, blobs: []}]);
                    expect(received.length).toBe(0);
                });

                it('should reject illegal messages', async()=>{
                    await send({text: {type: "message", target: "known", payload: null}, blobs: []});
                    expect(receivedChild).toStrictEqual([null]);
                    expect(received).toStrictEqual([{text: {type: "illegal", target: "known", payload: {}}, blobs: []}]);
                });

                it('should ignore messages for other channels', async()=>{
                    multiplexer.register("other");
                    await send({text: {type: "message", target: "other", payload: {}}, blobs: []});
                    await send({text: {type: "message", target: "unknown", payload: {}}, blobs: []});
                    expect(receivedChild.length).toBe(0);
                    expect(received).toStrictEqual([
                        {text: {type: "close", target: "unknown", payload: {}}, blobs: []}
                    ]);
                });

                it('should be able to be closed', async()=>{
                    await send({text: {type: "close", target: "known", payload: {}}, blobs: []});
                    expect(receivedChild).toStrictEqual([null]);
                    expect(received.length).toBe(0);
                });
            });
        });

        describe('when it sends a message', ()=>{
            let child;
            beforeEach(() => {
                child = multiplexer.register("known");
            });

            it('should wrap a message', async()=>{
                await child.send({text: {test: 1}, blobs: []});
                expect(received).toStrictEqual([
                    {text: {type: "message", target: "known", payload: {test: 1}}, blobs: []}
                ]);
            });

            it('should wrap a close', async() => {
                await child.close();
                expect(received).toStrictEqual([
                    {text: {type: "close", target: "known", payload: {}}, blobs: []}
                ]);
            });
        });
    });
});