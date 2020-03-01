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
import { Message, Connection, ConnectionClosed } from "./base";
import { Handler } from './handler';

export class SimpleConnection implements Connection
{
    private ingress: Connection;

    private egress: Connection;

    constructor(ingress: Connection, egress: Connection) {
        this.ingress = ingress;
        this.egress = egress;
    }

    registerMessageHandler(callback: (msg: Message) => void): any {
        return this.ingress.registerMessageHandler(callback);

    }
    unregisterMessageHandler(token: any): void {
        this.ingress.unregisterMessageHandler(token);
    }
    async send(message: Message): Promise<void> {
        await this.egress.send(message);
    }
    async close(): Promise<void> {
        await this.egress.close()
    }
}