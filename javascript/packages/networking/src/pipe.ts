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
import {Connection} from './base';
import {MessageBus} from './messagebus';
import {SimpleConnection} from './connection';

/**
 * The async connection decouples the message-send operation from the event handlers it is going to call.
 * This way, using a pipe will behave more like an actual connection pool to valid users.
 * 
 * It will silently drop errors and instead will just call console.error on the event handler.
 * Fix your stupid code, guys.
 */
class AsyncConnection implements Connection {
    private conn: Connection;

    constructor(conn: Connection) {
        this.conn = conn;
    }

    registerMessageHandler(callback: (msg: import("./base").Message) => void): number {
        return this.conn.registerMessageHandler(callback);
    }
    
    unregisterMessageHandler(token: any): void {
        this.conn.unregisterMessageHandler(token);
    }

    send(message: import("./base").Message): Promise<void> {
        this.conn.send(message).catch((e) => console.error(e));
        return Promise.resolve();
    }
    async close(): Promise<void> {
        this.conn.close().catch((e) => console.error(e));
        return Promise.resolve();
    }


}


/**
 * Runs handler callbacks inline! May cause deadlocks.
 * 
 * Intended for tests.
 * Use pipe() instead.
 */
export function inlinePipe() : {first: Connection, second: Connection} {
    let bus1 = new MessageBus();
    let bus2 = new MessageBus();

    return {
        first: new SimpleConnection(bus1, bus2),
        second: new SimpleConnection(bus2, bus1)
    }

}


export function pipe() : {first: Connection, second: Connection} {
    let {first, second} = inlinePipe();
    return {
        first: new AsyncConnection(first),
        second: new AsyncConnection(second)
    }
};