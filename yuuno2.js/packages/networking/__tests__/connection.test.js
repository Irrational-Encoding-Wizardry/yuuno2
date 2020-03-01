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

describe('@yuuno2/networking', () => {
    describe('The SimpleConnection-class', () => {
        describe('when enabled', () => {
            let messageBus1, messageBus2;
            let conn;

            beforeEach(() => {messageBus1 = new bus.MessageBus(); messageBus2 = new bus.MessageBus(); conn=new connection.SimpleConnection(messageBus1, messageBus2)});

            it('should forward messages to the egress-bus', async () => {
                let messages = [];

                messageBus1.registerMessageHandler((v) => messages.push([1, v]));
                messageBus2.registerMessageHandler((v) => messages.push([2, v]));

                const message = {data: {t: 1}, blobs: []};
                await conn.send(message);
                expect(messages).toStrictEqual([[2, {data: {t: 1}, blobs: []}]]);
            });

            it('should forward forward messages from the ingress-bus', async() => {
                let messages = [];
                conn.registerMessageHandler((v) => messages.push(v));
                const message = {data: {t: 1}, blobs: []};
                await messageBus1.send(message);
                await messageBus2.send(message);
                expect(messages).toStrictEqual([{data: {t: 1}, blobs: []}]);
            });
        });
    });
});