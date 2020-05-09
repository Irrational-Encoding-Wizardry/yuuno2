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
const pipe = require('../lib/pipe');
const rpc = require('../lib/rpc');

const sleep = async(t) => await new Promise((rs) => setTimeout(() => rs(), t));
const timeout = (f, t, err) => new Promise((rs, rj) => {
    if (err === undefined) err = new Error("Operation timed out");
    setTimeout(() => rj(err), t);
    f.then((v) => rs(v), (r) => rj(r));
});

describe('@yuuno2/networking', () => {
    describe('The RPC', () => {
        let first, second;
        beforeEach(() => {
            ({first, second} = pipe.inlinePipe());
        });

        describe('Server', () => {
            let srv;
            beforeEach(() => {
                srv = new rpc.Server(first);
            });

            let messages;
            beforeEach(() => {
                messages = [];
                second.registerMessageHandler((msg) => messages.push(msg));
            });

            it('should ignore unknown types', async () => {
                await second.send({text: {type: "error"}, blobs: []});
                await sleep(250);

                await second.send({text: {type: "result"}, blobs: []});
                await sleep(250);
            });

            it('should ignore packets without an ID', async () => {
                await second.send({text: {type: "invoke"}, blobs: []});
                await sleep(250);

                await second.send({text: {type: "invoke"}, blobs: []});
                await sleep(250);
            });

            it('should throw an error on invalid packets', async () => {
                srv.register("obj", {});

                let errmsg;
                await second.send({text: {type: "invoke", id: 0, target: "abc"}, blobs: []});
                await sleep(250);
                errmsg = messages.pop()
                expect(errmsg.text.type).toStrictEqual("error");
                expect(errmsg.text.message).toEqual(expect.stringContaining("Unknown target."));

                await second.send({text: {type: "invoke", id: 0, target: "obj", method: "wow"}, blobs: []});
                await sleep(250);
                errmsg = messages.pop()
                expect(errmsg.text.type).toStrictEqual("error");
                expect(errmsg.text.message).toEqual(expect.stringContaining("Unknown method."));
            })

            describe("with a registered object", () => {
                let object;
                
                beforeEach(()=> {
                    object = {
                        on_call_fast(msg) {                        
                            return msg;
                        },

                        async on_call_slow(msg) {
                            await sleep(100);
                            return msg;
                        },

                        on_fail(msg) {
                            throw new Error("Expected Failure. Testificate!");
                        }
                    };
                    srv.register('obj', object);
                });

                it('should answer to registered types', async() => {
                    await second.send({text: {type: 'invoke', id: 0, target: 'obj', method: 'call_fast', payload: {test: 1}}, blobs: []});
                    await sleep(250);
                    expect(messages.pop()).toStrictEqual({text: {type: 'result', id: 0, payload: {test: 1}}, blobs: []});

                    await second.send({text: {type: 'invoke', id: 0, target: 'obj', method: 'call_slow', payload: {test: 1}}, blobs: []});
                    await sleep(500);
                    expect(messages.pop()).toStrictEqual({text: {type: 'result', id: 0, payload: {test: 1}}, blobs: []});

                    await second.send({text: {type: 'invoke', id: 0, target: 'obj', method: 'fail', payload: {test: 1}}, blobs: []});
                    await sleep(250);
                    const errmsg = messages.pop()
                    expect(errmsg.text.type).toStrictEqual("error");
                    expect(errmsg.text.message).toEqual(expect.stringContaining("Testificate"));
                });
            });
        });

        describe('Client', () => {
            let cli;
            let srv;
            beforeEach(() => {
                cli = new rpc.Client(first);
                srv = new rpc.Server(second);
                const object = {
                    on_call_fast(msg) {                        
                        return msg;
                    },

                    async on_call_slow(msg) {
                        await sleep(100);
                        return msg;
                    },

                    on_fail(msg) {
                        throw new Error("Expected Failure. Testificate!");
                    }
                };
                srv.register('obj', object);
            });

            it('should ignore unknown types', async () => {
                await second.send({text: {type: "invoke"}, blobs: []});
                await sleep(250);
            });

            it('should accept an answer', async () => {
                expect(await timeout(cli._call("obj", "call_fast", {text: {value: "wow"}, blobs: []}), 5000)).toStrictEqual({text: {value: "wow"}, blobs: []});
                try {
                    await timeout(cli._call("obj", "fail", {text: {value: "wow"}, blobs: []}), 5000)
                    throw new Error("NO TESTIFICATE");
                } catch (msg) {
                    expect(msg.message).toEqual(expect.stringContaining("Testificate!"));
                }
            });

            describe('RPC-Proxy-Instance', () => {
                let proxy;
                beforeEach(() => {
                    cli.registerType("test", "call_fast", "call_slow", "fail");
                    proxy = cli.get("obj", "test");
                });

                it ('forward calls correctly', async() => {
                    expect(await timeout(proxy.call_fast({text:{value: "wow"}, blobs: []}), 5000)).toStrictEqual({text:{value: "wow"}, blobs: []});
                    expect(await timeout(proxy.call_slow({text:{value: "wow"}, blobs: []}), 5000)).toStrictEqual({text:{value: "wow"}, blobs: []});
                    try {
                        await timeout(proxy.fail( {text: {}, blobs: []}), 5000);
                        throw new Error("NO TESTIFICATE");
                    } catch (msg) {
                        expect(msg.message).toEqual(expect.stringContaining("Testificate!"));
                    }
                });
            });
        });
    });
});