import { Connection, Client, RpcClient, RpcServer, Message } from '@yuuno2/networking';
import { Frame, Clip, RawFormat } from '@yuuno2/clips';

import { using, toObject, object2map } from './utils';


export const RemoteClipServer = {
    create(connection: Connection, clip: Clip) : RpcServer {
        const srv = new RpcServer(connection);

        srv.register("metadata", async(msg: Message) => {
            const frameno: number = msg.text.frame as number;
            let metadata: Map<string, string>;
            if (frameno == null) {
                metadata = await clip.metadata();
            } else {
                metadata = await using(await clip.get(frameno), async(frame) => {
                    return await frame.metadata()
                });
            }
            return { text: toObject(metadata), blobs: [] }
        });
        srv.register("length", async () => {
            return {text: {length: clip.size}, blobs: []}
        });
        srv.register("size", async(msg: Message) => {
            return using(await clip.get(msg.text.frame as number), async(frame) => {
                const sz = await frame.size();
                return {text: [sz.width, sz.height], blobs: []}
            });
        });
        srv.register("format", async(msg: Message) => {
            return using(await clip.get(msg.text.frame as number), async(frame) => {
                return {text: (await frame.nativeFormat()).toJSON(), blobs: []};
            });
        });
        srv.register("render", async(msg: Message) => {
            const frameno = msg.text.frame as number;
            const formatJSON = msg.text.format as any[];
            const planesRaw = msg.text.planes as number|number[];

            return using(await clip.get(frameno), async(frame) => {
                const frSz = await frame.size();

                if (planesRaw === undefined || planesRaw === null) {
                    return {text: {'size': [frSz.width, frSz.height]}, blobs: []};
                }

                const format = RawFormat.fromJSON(formatJSON);
                if (!await frame.canRender(format)) {
                    return {text: {'size': null}, blobs: []};
                }

                let planes: number[];
                if (!(planesRaw instanceof Array))
                    planes = [planesRaw];
                else
                    planes = planesRaw;

                const rendered: ArrayBuffer[] = await frame.render(planes, format) as ArrayBuffer[];
                
                return {
                    text: {size: [frSz.width, frSz.height]},
                    blobs: rendered
                }
            });
        });

        return srv;
    }
}


interface RawClipInterface {
    metadata(msg: Message) : Promise<Message>;
    length(msg: Message) : Promise<Message>;
    size(msg: Message) : Promise<Message>;
    format(msg: Message) : Promise<Message>;
    render(msg: Message) : Promise<Message>;
}


class RemoteClip implements Clip {
    private _size: number;
    private _interface: RawClipInterface&Client;

    constructor(rci: RawClipInterface&Client, sz: number) {
        this._interface = rci;
        this._size = sz;
    }

    get size() : number {
        return this._size;
    }

    async metadata(): Promise<Map<string, string>> {
        return object2map((await this._interface.metadata({text:{frame: null}, blobs: []})).text);
    }
    get(frameno: number): Promise<Frame> {
        throw new Error("Method not implemented.");
    }
    async close(): Promise<void> {
        await this._interface.close();
    }


}


export async function connect(connection: Connection) : Promise<Clip> {
    const rci: RawClipInterface&Client = RpcClient.create(connection, ["metadata", "length", "size", "format", "render"]);
    const size: number = (await rci.length({text: {}, blobs: []})).text.length;
    return new RemoteClip(rci, size);
}