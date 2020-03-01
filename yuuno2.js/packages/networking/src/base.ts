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
import { JSONObject, ByteArray } from "./typedefs";


export class ConnectionClosed extends Error
{
    constructor(message?: string)
    {
        super(message);
        Object.setPrototypeOf(this, new.target.prototype);
    }
}

export interface Message
{
    text: JSONObject,
    blobs: DataView[]
}

export interface Connection
{
    /**
     * Register a new handler that handles messages that come into this connection.
     * 
     * If the connection closes the handler will receive a final `null`.
     * The callback is called immediately with null if the method is called on a closed connection.
     * 
     * @param callback A callback that is called for all message handlers.
     * @returns A token that is used to unregister the message handler.
     */
    registerMessageHandler(callback: (msg: Message|null) => void): any;

    /**
     * Unregisters a message handler.
     * @param token A token that is used to identify the callback.
     */
    unregisterMessageHandler(token: any): void;

    /**
     * Sends a message through the connection. If the connection is closed, the promise will fail with an error.
     * @param message The message to send.
     */
    send(message: Message): Promise<void>;

    /**
     * Closes the connection. Does not mean that the connection is closed for reading.
     * A close signal for reading is called separately.
     */
    close(): Promise<void>;

}