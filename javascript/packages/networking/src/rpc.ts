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
import { Connection, ConnectionClosed, Message } from "./base";
import { makeCounter } from "./utils";
import { JSONObject, JSONSerializable } from "./typedefs";
import { pipe } from "./pipe";


class _InvocationException extends Error
{
    constructor(message: string)
    {
        super(message);
        Object.setPrototypeOf(this, new.target.prototype);
    }
}



export class RpcServer
{

    private conn: Connection;

    private methodMap: {[x: string]: (msg: Message) => Message|Promise<Message>} = {};

    constructor(conn: Connection) {
        this.conn = conn;
        const token = this.conn.registerMessageHandler(async (msg) => {
            if (msg === null) { this.conn.unregisterMessageHandler(token); return; }
            await this.invoke(msg);
        });
    }

    public register(name: string, func: (msg: Message) => Message|Promise<Message>) {
        this.methodMap[name] = func;
    }

    public async close() {
        await this.conn.close();
    }

    private async send(message: Message): Promise<void> {
        try {
            await this.conn.send(message)
        } catch (e) {
            if (!(e instanceof ConnectionClosed)) throw e;
        }
    }

    private async invoke(message: Message): Promise<void> {
        if (message.text.id === null || message.text.id === undefined) {
            await this.send({text: {id: null, type: 'error', message: 'ID is missing.'}, blobs: []});
            return;
        }
        
        let response;
        try {
            response = await this._invoke(message);
        } catch (e) {
            if (e instanceof _InvocationException) {
                await this.send({text: {id: message.text.id, type: 'error', error: e.message}, blobs: []});
            } else if (e instanceof Error) {
                await this.send({text: {id: message.text.id, type: 'error', error: `Error during RPC Invocation:\n${e.name}: ${e.message}\n${e.stack}`}, blobs: []});
            } else {
                await this.send({text: {id: message.text.id, type: 'error', error: `Error during RPC Invocation: ${e.toString()}`}, blobs: []});
            }
            return;
        }
        await this.send({text: {id: message.text.id, type: "response", result: response.text}, blobs: response.blobs});
    }

    private async _invoke(message: Message): Promise<Message> {
        if (!message.text.type)
            throw new _InvocationException("Type missing");
        if (message.text.type != "request")
            throw new _InvocationException(`Unknown type: ${message.text.type}`);
        if (!message.text.method || typeof message.text.method != 'string')
            throw new _InvocationException("Method-Name is missing.");
        if (typeof message.text.params != "object")
            throw new _InvocationException("Params must be an object.");
        return await this._invokeReal(message.text.method, {text: (message.text.params||{}) as JSONObject, blobs: message.blobs});
    }

    private async _invokeReal(name: string, message: Message): Promise<Message> {
        if (!this.methodMap[name])
            throw new _InvocationException(`Unknown method ${name}`);

        const rawResult = this.methodMap[name](message);
        return ((!!rawResult && typeof (rawResult as Promise<Message>).then == 'function') ? (await rawResult) : rawResult);
    }

}


export interface Client
{
    /**
     * Closes the connection to an Yuuno RPC Endpoint.
     */
    close(): Promise<void>;
}


export class RpcClient
{
    private static openRequestCounter: ()=>number = makeCounter();

    public static create<T>(conn: Connection, functions: string[]): T&Client
    {
        const requestMap: {[x: number]: (msg: Message) => void} = {};
        conn.registerMessageHandler((msg: Message) => {
            if (msg === null) {
                for (let handler of Object.values(requestMap)) {
                    handler(null);
                }
            } else {
                if (msg.text.id === undefined) return;
                if (typeof msg.text.id != "number") return;
                if (!requestMap[msg.text.id]) return;
                requestMap[msg.text.id](msg);
            }
        })

        const result: any = {
            async close() : Promise<void> 
            {
                await conn.close();
            }
        };
        functions.forEach(func=>{
            result[func] = async (msg: Message, timeout: number = 0) => {
                const rqid = RpcClient.openRequestCounter();
                const resultPromise = new Promise<Message>((rs, rj) => {
                    requestMap[rqid] = (msg: Message) => {
                        if (msg === null) rj(new Error("Connection is closing."));
                        if ((msg.text.type||"response") === "error") {
                            rj(new Error((msg.text.error || "Remote error while handling exception.") as string));
                        } else {
                            rs({text: (msg.text.result||{}) as JSONObject, blobs: msg.blobs});
                        }
                    };
                    if (timeout > 0) {
                        setTimeout(() => rj(new Error("Operation timed out")), timeout);
                    }
                });
                await conn.send({text:{type: "request", id: rqid, method: func, params: msg.text}, blobs: msg.blobs});
                try {
                    return await resultPromise;
                } finally {
                    delete requestMap[rqid];
                }
            };
        });
        result.prototype = RpcClient;
        return <T&Client>result;
    }
}