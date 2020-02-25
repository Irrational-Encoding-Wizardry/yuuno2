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