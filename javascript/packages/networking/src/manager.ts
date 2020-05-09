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
import { v4 as uuid4 } from 'uuid';
import { Client, Server } from './rpc';
import { Message } from './base';


const MANAGER_ID: string = "a6eb965e-1c6a-4c23-897f-99ef0b9fb762";


interface Service {
    obj: any,
    temporary: boolean
}


export class LocalManager {

    private server: Server;

    private services: Map<string, Service> = new Map();
    private objects: Map<string, string> = new Map();

    constructor(server: Server) {
        this.server = server;
        this.server.register(MANAGER_ID, this);
    }

    add_temporary_object(object: any) {
        const name = uuid4();
        this.services.set(name, {obj: object, temporary: true});
        return name;
    }

    add_service(name: string, object: any) {
        this.services.set(name, {obj: object, temporary: false});
    }

    remove_service(name: string) {
        if (this.services.has(name))
            this.services.delete(name);
    }
    
    on_version(msg: Message): Message {
        return {text: {version: 1, extensions: []}, blobs: []};
    }

    on_has_service(msg: Message): Message {
        if (!msg.text.service) return {text: {exists: false}, blobs: []};
        return {text: {exists: this.services.has(msg.text.service)}, blobs: []}
    }

    on_acquire_object(msg: Message): Message {
        if (!msg.text.service) return {text: {exists: false}, blobs: []};
        if (!this.services.has(msg.text.service)) return {text: {exists: false}, blobs: []};

        const service = this.services.get(msg.text.service);
        if (service.temporary) this.services.delete(msg.text.service);

        const id = uuid4();
        this.server.register(id, service.obj);
        this.objects.set(id, service.obj);

        return {text: {exists: true, id: id}, blobs: []};
    }

    on_release_object(msg: Message): Message {
        if (!msg.text.obj) return {text: {removed: true}, blobs: []};
        if (!this.objects.has(msg.text.obj)) return {text: {removed: true}, blobs: []};
        this.server.unregister(msg.text.obj);
        this.objects.delete(msg.text.obj);
        return {text: {removed: true}, blobs: []};
    }
}

interface RemoteManagerProxy {
    version:        (msg: Message) => Promise<Message>;
    has_service:    (msg: Message) => Promise<Message>;
    acquire_object: (msg: Message) => Promise<Message>;
    release_object: (msg: Message) => Promise<Message>;
}

export interface Closable {
    close: () => Promise<void>;
}

export class RemoteManager {
    private client: Client;
    private proxy: RemoteManagerProxy;

    private constructor(client: Client) {
        this.client = client;
        this.client.registerType("remote_manager", "version", "has_service", "acquire_object", "release_object");
        this.proxy = client.get<RemoteManagerProxy>(MANAGER_ID, "remote_manager");
    }

    async has(name: string): Promise<boolean> {
        return (await this.proxy.has_service({text: {service: name}, blobs: []})).text.exists;
    }

    async get<T>(name: string, type: string) : Promise<(T&Closable)|null> {
        let message = await this.proxy.acquire_object({text: {service: name}, blobs: []})
        if (!message.text.exists) return null;

        let id = message.text.id;
        let result: T&Closable = this.client.get(id, type);
        result["close"] = async () => {
            await this.proxy.release_object({text: {obj: id}, blobs: []});
        }
        return result;
    }

    static async create(client: Client) : Promise<RemoteManager> {
        let result = new RemoteManager(client);
        const response = await result.proxy.version({text: {supported: [{version: 1, extensions: []}]}, blobs: []});
        if (response.text.version != 1)
            throw new Error("Remote endpoint has an unsupported version.");
        return result;
    }
}