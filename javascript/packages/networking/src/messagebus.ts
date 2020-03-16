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
import { Handler } from './handler';
import { Message, Connection, ConnectionClosed } from './base';


export class MessageBus implements Connection {

    private handlers: Handler<Message|null>|null = new Handler();

    registerMessageHandler(callback: (msg: Message) => void): number {
        if (this.handlers === null) {
            callback(null);
            return null;
        };

        return this.handlers.register(callback);
    }
    
    unregisterMessageHandler(token: number): void {
        if (this.handlers === null) return;
        this.handlers.unregister(token);
    }

    async send(message: Message): Promise<void> {
        if (this.handlers === null) throw new ConnectionClosed("The connection is closed.");
        if (message === null) throw new TypeError("Use close() to close instead.");
        await this.handlers.emit(message);
    }

    async close(): Promise<void> {
        if (this.handlers === null)  return;
        await this.handlers.emit(null);
        this.handlers.clear();
        this.handlers = null;
    }
}