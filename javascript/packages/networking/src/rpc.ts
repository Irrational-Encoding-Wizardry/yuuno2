import { Message, Connection } from './base';
import { PromiseDelegate } from './utils';


export class Server {

    private connToken: any;
    private conn: Connection;
    private objects: Map<string, any> = new Map();

    constructor(conn: Connection) {
        this.conn = conn;
        this.connToken = this.conn.registerMessageHandler(this._receive);
    }

    private async _receive(msg: Message) : Promise<void> {
        if (msg.text.type !== "invoke") return;
        if (msg.text.id === undefined) return;

        let id: any = msg.text.id;
        if (!this.objects.has(msg.text.target)) {
            await this.conn.send({text: {type: "error", id: id, message: "Unknown target."}, blobs: []});
            return;
        }
        
        let obj : any = this.objects.get(msg.text.target);
        let func: any = obj[msg.text.method];
        if (typeof func !== "function") {
            await this.conn.send({text: {type: "error", id: id, message: "Unknown method."}, blobs: []});
            return;
        }

        let payload: any = {text: msg.text.payload||{}, blobs: msg.blobs};

        // Fire and forget the invocation.
        this._invoke(id, obj, func, payload).then(()=>{}, console.error);
    }

    private async _invoke(id: any, thisArg: any, func: (msg: Message) => Promise<Message>|Message, payload: Message) : Promise<void> {
        let message: Message;
        try {
            message = await this.__invoke(thisArg, func, payload);
        } catch(e) {
            let text = e.toString()
            if (!!e.stack && !!e.name && e.message !== undefined)
                text = "Got error: " + e.name + ": " + e.message + "\n" + e.stack;

            await this.conn.send({text: {type: "error", id: id, message: text}, blobs: []});
            return;
        }

        await this.conn.send({text: {type: "result", id: id, payload: message.text}, blobs: message.blobs});
    }

    private async __invoke(thisArg: any, func: (msg: Message) => Promise<Message>|Message, payload: Message): Promise<Message> {
        let result: Promise<Message>|Message = func.apply(thisArg, [payload]);
        if (!!result && typeof (<Promise<Message>>result).then === 'function')
            result = await result;
        return <Message>result;
    }

    register(name: string, object: any) : void {
        this.objects.set(name, object);
    }

    unregister(name: string) : void {
        if (this.objects.has(name)) {
            this.objects.delete(name);
        }
    }

    async close() : Promise<void> {
        this.conn.unregisterMessageHandler(this.connToken);
    }
}

export class RPCCallFailedError extends Error {
    constructor(m: string) {
        super(m);

        // Set the prototype explicitly.
        Object.setPrototypeOf(this, RPCCallFailedError.prototype);
    }
}

export class Client {

    private currentId: number = 0;
    private connToken: any;
    private conn: Connection;
    private types: Map<string, string[]> = new Map();
    private waiters: Map<number, PromiseDelegate<Message>> = new Map();

    constructor(conn: Connection) {
        this.conn = conn;
        this.connToken = this.conn.registerMessageHandler(this._receive);
    }

    register_type(typename: string, ...names: string[]) : void {
        this.types.set(typename, names);
    }

    get<T>(name: string, type: string) : T {
        if (!this.types.has(type)) {
            throw new Error("Unknown type");
        }

        const obj: {[name: string]: (msg: Message) => Promise<Message>} = {};
        for(let t of this.types.get(type)) {
            ((n)=>{obj[n] = (msg: Message) => this._call(name, n, msg)})(t);
        }

        return <T><unknown>obj;
    }

    async _call(target: string, method: string, data: Message) : Promise<Message> {
        const requestId = ++this.currentId;
        const delegate = new PromiseDelegate<Message>();

        this.waiters.set(requestId, delegate);
        await this.conn.send({
            text: {
                type: "invoke",
                target: target,
                method: method,
                payload: data.text
            },
            blobs: data.blobs
        })

        return await delegate.promise;
    }

    async _receive(msg: Message) : Promise<void> {
        if (msg.text.type !== "return" && msg.text.type !== "error") return;
        if (!!msg.text.id) return;

        let id = msg.text.id;
        if (!this.waiters.has(id)) return;
        let delegate = this.waiters.get(id);
        this.waiters.delete(id);

        if (msg.text.type == "error") {
            delegate.reject(new RPCCallFailedError(msg.text.message || "Remote call failed."));
        } else {
            delegate.resolve({text: msg.text.payload, blobs: msg.blobs});
        }
    }

    async close() : Promise<void> {
        this.conn.unregisterMessageHandler(this.connToken);
    }
}