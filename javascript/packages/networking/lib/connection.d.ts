import { Message, Connection } from "./base";
export declare class SimpleConnection implements Connection {
    private ingress;
    private egress;
    constructor(ingress: Connection, egress: Connection);
    registerMessageHandler(callback: (msg: Message) => void): any;
    unregisterMessageHandler(token: any): void;
    send(message: Message): Promise<void>;
    close(): Promise<void>;
}
