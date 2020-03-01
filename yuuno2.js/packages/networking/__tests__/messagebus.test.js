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
const base = require('../lib/base');

describe('@yuuno2/networking', () => {
    describe('The MessageBus', () => {
        describe('when enabled', () => {
            let messageBus;

            beforeEach(() => messageBus = new bus.MessageBus());

            it('should forward messages to registered handlers', async () => {
                var message1 = {data: {t: 1}, blobs: []};
                var message2 = {data: {t: 2}, blobs: []};

                var received1 = [];
                var received2 = [];

                messageBus.registerMessageHandler((message) => received1.push(message));
                await messageBus.send(message1);
                messageBus.registerMessageHandler((message) => received2.push(message));
                await messageBus.send(message2);

                expect(received1).toStrictEqual([message1, message2]);
                expect(received2).toStrictEqual([message2]);
            });

            it('should not forward messages to unregistered handlers', async () => {
                var message1 = {data: {t: 1}, blobs: []};
                var message2 = {data: {t: 2}, blobs: []};

                var received1 = [];
                var received2 = [];

                const token = messageBus.registerMessageHandler((message) => received1.push(message));
                messageBus.registerMessageHandler((message) => received2.push(message));
                await messageBus.send(message1);
                messageBus.unregisterMessageHandler(token);
                await messageBus.send(message2);

                expect(received1).toStrictEqual([message1]);
                expect(received2).toStrictEqual([message1, message2]);
            });

            it('should send null to all event handlers on close', async () => {
                var received1 = [];
                var received2 = [];

                messageBus.registerMessageHandler((message) => received1.push(message));
                messageBus.registerMessageHandler((message) => received2.push(message));
                await messageBus.close();

                expect(received1).toStrictEqual([null]);
                expect(received2).toStrictEqual([null]);
            });
        });

        describe('when closed', () => {
            let messageBus;
            beforeEach(async () => {messageBus = new bus.MessageBus(); await messageBus.close();});

            it('should send null to all new event handlers', async () => {
                var received = [];
                messageBus.registerMessageHandler((v) => received.push([1, v]));
                messageBus.registerMessageHandler((v) => received.push([2, v]));

                expect(received).toStrictEqual([[1, null], [2, null]]);
            });

            it('should refuse sending messages with an error', async () => {
                expect(messageBus.send({data: {t: 1}, blobs: []})).rejects.toBeInstanceOf(base.ConnectionClosed);
            });
        });
    });
});