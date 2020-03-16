import { Connection, Message } from "./base";
export declare class RpcServer {
    private conn;
    private methodMap;
    constructor(conn: Connection);
    register(name: string, func: (msg: Message) => Message | Promise<Message>): void;
    close(): Promise<void>;
    private send;
    private invoke;
    private _invoke;
    private _invokeReal;
}
export interface Client {
    close(): Promise<void>;
}
export declare class RpcClient {
    private static openRequestCounter;
    static create<T>(conn: Connection, functions: string[]): T & Client;
}
