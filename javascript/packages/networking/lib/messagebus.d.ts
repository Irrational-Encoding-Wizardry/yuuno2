import { Message, Connection } from './base';
export declare class MessageBus implements Connection {
    private handlers;
    registerMessageHandler(callback: (msg: Message) => void): number;
    unregisterMessageHandler(token: number): void;
    send(message: Message): Promise<void>;
    close(): Promise<void>;
}
