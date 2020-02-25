import {Connection} from './base';
import {MessageBus} from './messagebus';
import { SimpleConnection } from './connection';
import { JSONObject } from './typedefs';


export class Multiplexer
{
    private conn: Connection;

    private controlToken: any;

    private streams: {[x: string]: SimpleConnection} = {};

    constructor(conn: Connection) {
        this.conn = conn;
        this.controlToken = this.conn.registerMessageHandler(async (msg) => {
            if (msg.text.type != "message") return;
            const target: string = (typeof msg.text.target != "string") ? "" : (msg.text.target as string);
            if (!!this.streams[target]) {
                await this.conn.send({text: {target: msg.text.target, type: "close", payload: {}}, blobs: []})
            }
        });
    }

    /**
     * Registers a new connection that is multiplexed through the channel.
     * 
     * @param name The name of the connection
     * @returns A new connection with the given name.
     */
    register(name: string): Connection {
        let _regname = name || "";

        // If the channel already exists, return that stream instead.
        if (!!this.streams[_regname]) return this.streams[name];

        let ingressBus = new MessageBus();
        let egressBus = new MessageBus();

        // Deliver messages to the bus.
        const closeToken = this.conn.registerMessageHandler(async (msg) => {
            // On close
            if (msg === null) {
                // Forward ingress close.
                await ingressBus.close();

            // If we are the target.
            } else if (msg.text.target === name) {
                // If non-message: Close.
                if ((msg.text.type||"message") != "message") {
                    await ingressBus.close();
                } else {
                    // Kill connection on illegal message.
                    if (typeof msg.text.payload !== 'object') {
                        await this.conn.send({text: {target: name, type: 'illegal', payload: {}}, blobs: []});
                        await ingressBus.close();
                        await egressBus.close();
                    }

                    // Unwrap message and forward.
                    await ingressBus.send({text: (msg.text.payload||{}) as JSONObject, blobs: msg.blobs});
                }
            }
        });

        // Wrap messages sent to the channel.
        egressBus.registerMessageHandler(async (msg) => {
            // On close
            if (msg === null) {
                // Unregister the stream for further messages.
                delete this.streams[name];

                // Remove the handler
                this.conn.unregisterMessageHandler(closeToken);

                // Send a close messge.
                await this.conn.send({text: {target: name, type: "close", payload: {}}, blobs: []});

                // Close the ingress bus.
                await ingressBus.close();
            } else {
                // Wrap and forward.
                await this.conn.send({text: {target: name, type: "message", payload: msg.text}, blobs: msg.blobs});
            }
        })

        // Register the connection.
        let multiplexed = new SimpleConnection(ingressBus, egressBus);
        this.streams[_regname] = multiplexed;
        return multiplexed;
    }

    /**
     * Close the multiplexer and close the underlying message.
     */
    async close() {
        await Promise.all(Object.values(this.streams).map((s) => new Promise(rs => s.close().then(rs, rs))));
        this.conn.unregisterMessageHandler(this.controlToken);
        await this.conn.close();
    }
}