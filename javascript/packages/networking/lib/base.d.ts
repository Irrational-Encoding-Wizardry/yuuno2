export declare class ConnectionClosed extends Error {
    constructor(message?: string);
}
export interface Message {
    text: any;
    blobs: ArrayBuffer[];
}
export interface Connection {
    registerMessageHandler(callback: (msg: Message | null) => void): any;
    unregisterMessageHandler(token: any): void;
    send(message: Message): Promise<void>;
    close(): Promise<void>;
}
