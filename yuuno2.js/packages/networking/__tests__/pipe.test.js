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