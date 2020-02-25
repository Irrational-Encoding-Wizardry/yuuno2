'use strict';

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
