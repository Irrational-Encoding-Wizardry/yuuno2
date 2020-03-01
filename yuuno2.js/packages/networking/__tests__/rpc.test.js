const { RpcClient, RpcServer } = require('../lib/rpc');
const { pipe, inlinePipe } = require('../lib/pipe');


describe('@yuuno2/networking', () => {
    describe('The RpcServer', () => {
        let received;
        let remoteSide;
        let server;
        beforeEach(() => {
            let {first, second} = inlinePipe();
            remoteSide = second;
            received = [];
            second.registerMessageHandler((msg) => received.push(msg));
            server = new RpcServer(first);
        });

        it('should error if the request is malformed.', async() => {
            await remoteSide.send({text: {}, blobs: []});
            await remoteSide.send({text: {id: 3}, blobs: []});
            await remoteSide.send({text: {id: 4, type: "unicorn"}, blobs: []});
            await remoteSide.send({text: {id: 5, type: "request"}, blobs: []});
            await remoteSide.send({text: {id: 6, type: "request", method: "invalid-params", params: 5}, blobs: []});

            expect(received.length).toBe(5);
            for (let single of received) {
                expect(single.text.type).toBe("error");
            }
            expect(received.map(m => m.text.id)).toStrictEqual([null, 3,4,5,6]);
            expect(received.map(m => m.text.type)).toStrictEqual(["error", "error", "error", "error", "error"]);
        });

        it('should error if the method could not be found.', async() => {
            await remoteSide.send({text: {id: 1, type: "request", method: "unknown", params: {}}, blobs: []});
            expect(received.length).toBe(1);
            expect(received[0].text.id).toBe(1);
            expect(received[0].text.type).toBe("error");
        });

        it('should forward the params to the method.', async()=>{
            server.register("known", (params)=>params);
            await remoteSide.send({text: {id: 1, type: "request", method: "known", params: {test: 123}}, blobs: []});
            expect(received).toStrictEqual([{text: {id: 1, type: "response", result: {test: 123}}, blobs: []}]);
        });

        it('should correctly forward an error.', async()=>{
            server.register("known", (params)=>{throw new Error("wow");});
            await remoteSide.send({text: {id: 1, type: "request", method: "known", params: {test: 123}}, blobs: []});
            expect(received.length).toBe(1);
            expect(received[0].text.id).toBe(1);
            expect(received[0].text.type).toBe("error");
            expect(received[0].text.error).toMatch(/wow/);
        });

        it('should await the promise and forward the result', async()=>{
            server.register("known", (params)=>Promise.resolve(params));
            await remoteSide.send({text: {id: 1, type: "request", method: "known", params: {test: 123}}, blobs: []});
            expect(received).toStrictEqual([{text: {id: 1, type: "response", result: {test: 123}}, blobs: []}]);
        });

        it('should await the promise and forward the rejection', async()=>{
            server.register("known", (params)=>Promise.reject(new Error("wow")));
            await remoteSide.send({text: {id: 1, type: "request", method: "known", params: {test: 123}}, blobs: []});
            expect(received.length).toBe(1);
            expect(received[0].text.id).toBe(1);
            expect(received[0].text.type).toBe("error");
            expect(received[0].text.error).toMatch(/wow/);
        });
    });

    describe('The RpcClient', () => {
        let received;
        let remoteSide;
        let server;
        beforeEach(() => {
            let {first, second} = pipe();
            remoteSide = second;
            received = [];
            second.registerMessageHandler((msg) => received.push(msg));
            server = new RpcServer(first);

            server.register("pass", (msg) => ({text: {myid: msg.text.myid}, blobs: []}));
            server.register("fail", (msg) => {throw new Error(`lol${msg.text.myid}`);});

            server.register("wait", (msg) => new Promise((rs) => setTimeout(() => rs({text: msg.text.response, blobs: []}), msg.text.waittime)));
        });

        it('should create an object with the given functions', () => {
            const client = RpcClient.create(remoteSide, ["pass", "fail"]);
            expect(typeof client.pass).toBe("function");
            expect(typeof client.fail).toBe("function");
        });

        it('should add a close function to the returned object', () => {
            const client = RpcClient.create(remoteSide, ["pass", "fail"]);
            expect(typeof client.close).toBe("function");
        });

        it('should call the pass function and return the correct value back', async () => {
            const client = RpcClient.create(remoteSide, ["pass", "fail"]);
            let result1 = await client.pass({text: {myid: 1}, blobs:[]}, 1000);
            let result2 = await client.pass({text: {myid: 2}, blobs:[]}, 1000);
            expect(result1.text.myid).toBe(1);
            expect(result2.text.myid).toBe(2);
        });

        it('should call the fail function an get the correct error message back', async () => {
            const client = RpcClient.create(remoteSide, ["pass", "fail"]);
            await expect(client.fail({text: {myid: 3}, blobs: []})).rejects.toThrow(/lol3/);
            await expect(client.fail({text: {myid: 4}, blobs: []})).rejects.toThrow(/lol4/);
        });

        it('should timeout if a timeout is given', async() => {
            const client = RpcClient.create(remoteSide, ["wait"]);
            await expect(client.wait({text: {response: {myid: 5}, waittime: 1000}, blobs: []}, 500)).rejects.toThrow();
            await expect(client.wait({text: {response: {myid: 6}, waittime: 500}, blobs: []}, 1000)).resolves.toStrictEqual({text: {myid: 6}, blobs: []});
            await expect(client.wait({text: {response: {myid: 7}, waittime: 2000}, blobs: []})).resolves.toStrictEqual({text: {myid: 7}, blobs: []});
        });
    });
})