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