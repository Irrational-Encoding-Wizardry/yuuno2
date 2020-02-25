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