
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
const manager = require('../lib/manager');


const timeout = (f, t, err) => new Promise((rs, rj) => {
    if (err === undefined) err = new Error("Operation timed out");
    setTimeout(() => rj(err), t);
    f.then((v) => rs(v), (r) => rj(r));
});


describe('@yuuno2/networking', () => {
    describe('The RPC-Manager', () => {
        let local, remote;
        beforeEach(async ()=>{
            let first, second;
            ({first, second} = pipe.inlinePipe());

            let server = new rpc.Server(first);
            let client = new rpc.Client(second);
            client.registerType("test", "test");

            local = new manager.LocalManager(server);
            remote = await manager.RemoteManager.create(client);
        });

        let object;
        beforeEach(()=>{
            object = {
                last: null,
                on_test(msg) {
                    this.last = msg;
                    return msg;
                }
            }
        });

        describe("with a temporary object", ()=>{
            it("should be only found once", async()=>{
                var temp_id = local.add_temporary_object(object);

                var temp = await timeout(remote.get(temp_id, "test"), 5000);
                expect(await timeout(remote.get(temp_id, "test"), 5000)).toBe(null);

                await timeout(temp.test({text:{val: 1}, blobs: []}), 5000);
                expect(object.last).toStrictEqual({text:{val: 1}, blobs: []});

                await timeout(temp.close(), 5000);
            });
        });

        describe("with a permanent service", ()=>{
            it("should be found more than once", async()=>{
                local.add_service("test", object);

                var temp;

                temp = await timeout(remote.get("test", "test"), 5000);
                await timeout(temp.test({text:{val: 1}, blobs: []}), 5000);
                expect(object.last).toStrictEqual({text:{val: 1}, blobs: []});
                await timeout(temp.close(), 5000);

                temp = await timeout(remote.get("test", "test"), 5000);
                await timeout(temp.test({text:{val: 2}, blobs: []}), 5000);
                expect(object.last).toStrictEqual({text:{val: 2}, blobs: []});
            });

            it("should not be reusable after close.", async()=>{
                local.add_service("test", object);

                let temp1 = await timeout(remote.get("test", "test"), 5000);
                let temp2 = await timeout(remote.get("test", "test"), 5000);
                await timeout(temp1.test({text:{val: 1}, blobs: []}), 5000);
                expect(object.last).toStrictEqual({text:{val: 1}, blobs: []});
                await timeout(temp1.close(), 5000);
                try {
                    let it_worked_wtf = await timeout(temp1.test({text:{val: 2}, blobs: []}), 5000);
                    
                    fail(it_worked_wtf);
                } catch(e) {
                    expect(e.message).toEqual(expect.stringContaining("Unknown target"));
                }

                await timeout(temp2.test({text:{val: 3}, blobs: []}), 5000);
                expect(object.last).toStrictEqual({text:{val: 3}, blobs: []});
            })
        });
    });
});