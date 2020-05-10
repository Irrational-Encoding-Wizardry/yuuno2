import { Connection, RpcClient, RpcServer, Message, RemoteManager } from '@yuuno2/networking';
import { Frame, Clip, RawFormat, Size } from '@yuuno2/clips';

import { using, toObject, object2map, Closable } from './utils';


export class LocalClip {

    private clip: Clip;

    constructor(clip: Clip) {
        this.clip = clip;
    }

    async with_frame<T>(message: Message, cb: (f: Frame) => Promise<T>) : Promise<T> {
        const $self = this;

        const size: Size|null = (<Size>message.text.size)||null;
        let clip: Clip = this.clip;
        if (size !== null)
            clip = (await this.clip.resize(size))||clip;

        const frameno: number = message.text.frameno;
        return await using(await clip.get(frameno), async(f: Frame) => {
            return await cb.apply($self, f);
        });
    }

    on_length(msg: Message): Message {
        return {
            text: {length: this.clip.size},
            blobs: []
        }
    }

    async on_format(msg: Message) : Promise<Message> {
        const format: RawFormat = await this.with_frame(msg, async (f) => {
            return await f.nativeFormat();
        });
        return {
            text: {format: format.toJSON()},
            blobs: []
        }
    }

    async on_size(msg: Message) : Promise<Message> {
        const size: Size = await this.with_frame(msg, async(f)=>{
            return await f.size();
        });
        return {
            text: size,
            blobs: []
        };
    }

    async on_metadata(msg: Message) : Promise<Message> {
        let metadata: Map<string, string>;
        if (typeof msg.text.frameno !== "number") {
            metadata = await this.clip.metadata();
        } else {
            metadata = await this.with_frame(msg, async(f)=>{
                return await f.metadata();
            });
        }

        return {
            text: {metadata: toObject(metadata)},
            blobs: []
        };
    }

    async on_can_render(msg: Message) : Promise<Message> {
        const format: RawFormat = RawFormat.fromJSON(msg.text.format);
        const supported: boolean = await this.with_frame(msg, async(f)=>{
            return await f.canRender(format);
        });
        return {
            text: {supported},
            blobs: []
        };
    }

    async on_render(msg: Message) : Promise<Message> {
        const format: RawFormat = RawFormat.fromJSON(msg.text.format);
        const rawPlane: number|number[] = msg.text.planes;
        const planes: number[] = (rawPlane instanceof Array) ? rawPlane : [rawPlane];

        const rendered: ArrayBuffer[]|null = await this.with_frame(msg, async(f)=>{
            if (!(f.canRender(format))) {
                return null;
            }
            return <ArrayBuffer[]>(await f.render(planes, format));
        });

        if (rendered === null) {
            return {
                text: {success: false},
                blobs: []
            };
        } else {
            return {
                text: {success: true},
                blobs: rendered
            };
        }
    }
}


interface ICanOpen {
    open(): Promise<void>;
}

const add_clip_type = (cli: RpcClient) => {cli.registerType("yuuno2:clip", "length", "format", "size", "metadata", "can_render", "render")};
interface _IClipProxy extends Closable {
    length(msg: Message): Promise<Message>;
    format(msg: Message): Promise<Message>;
    size(msg: Message): Promise<Message>;
    metadata(msg: Message): Promise<Message>;
    can_render(msg: Message): Promise<Message>;
    render(msg: Message): Promise<Message>;
}
type IClipProxy = _IClipProxy&ICanOpen;


function makeRefCnt<T>(obj: T&Closable): T&Closable&ICanOpen {
    const close = obj.close;
    var refCnt = 0;
    obj.close = async function() {
        refCnt-=1;
        if (refCnt <= 0) {
            close.apply(obj);
        }
    };
    (<any>obj).open = async function() {
        refCnt += 1;
    };
    return <T&Closable&ICanOpen><unknown>obj;
}


export class RemoteFrame implements Frame {
    private _desiredSize: Size|null;
    private frameno: number;
    private proxy: IClipProxy;

    constructor(proxy: IClipProxy, frameno: number, size: Size|null) {
        this.proxy = proxy;
        this.frameno = frameno;
        this._desiredSize = size;
    }

    async nativeFormat(): Promise<RawFormat> {
        return RawFormat.fromJSON((
            await this.proxy.format({text: {frameno: this.frameno}, blobs: []})
        ).text)
    }
    async size(): Promise<Size> {
        if (this._desiredSize !== null) return this._desiredSize;
        return <Size>((await this.proxy.size({text: {frameno: this.frameno}, blobs: []})).text);
    }
    async metadata(): Promise<Map<string, string>> {
        return object2map(
            (await this.proxy.metadata({text: {frameno: this.frameno}, blobs: []})).text.metadata
        );
    }

    async canRender(format: RawFormat): Promise<boolean> {
        const response = await this.proxy.can_render({text: {frameno: this.frameno, format: format.toJSON(), size: this._desiredSize}, blobs: []});
        return <boolean>response.text.supported;
    }

    async render(plane: number | number[], format: RawFormat): Promise<ArrayBuffer | ArrayBuffer[]> {
        const wasSinglePlane = plane instanceof Array;
        if (!wasSinglePlane) plane = [<number>plane];

        const response = await this.proxy.render({
            text: {frameno: this.frameno, planes: plane, format: format.toJSON(), size: this._desiredSize},
            blobs: []
        });
        if (!response.text.success) {
            throw new Error("Failed to render video.")
        }
        if (wasSinglePlane) {
            return response.blobs[0];
        } else {
            return response.blobs;
        }
    }

    async open() : Promise<void> {
        await this.proxy.open();
    }

    async close(): Promise<void> {
        await this.proxy.close();
    }

};


export class RemoteClip implements Clip {
    private _desiredSize: Size|null;
    private _length: number;
    private proxy: IClipProxy;    

    private constructor(proxy: IClipProxy, length: number, desiredSize: Size|null = null) {
        this.proxy = proxy;
        this._desiredSize = desiredSize;

        this._length = length;
    }

    get size(): number {
        return this._length;
    }

    async metadata(): Promise<Map<string, string>> {
        return object2map(
            (await this.proxy.metadata({text: {frameno: null}, blobs: []})).text.metadata
        );
    }

    async get(frameno: number): Promise<Frame> {
        const result = new RemoteFrame(this.proxy, frameno, this._desiredSize);
        await result.open();
        return result;
    }

    async close(): Promise<void> {
        await this.proxy.close();
    }

    async resize(size: Size): Promise<RemoteClip> {
        await this.proxy.open();
        return new RemoteClip(this.proxy, this._length, size);
    }

    private static async from_proxy(_proxy: _IClipProxy) : Promise<RemoteClip> {
        let proxy = makeRefCnt(_proxy);
        await proxy.open();
        let length = (await proxy.length({text: {}, blobs: []})).text.length;
        return new RemoteClip(proxy, length);
    }

    static async from_rpc(name: string, cli: RpcClient): Promise<RemoteClip> {
        add_clip_type(cli);
        let _proxy: _IClipProxy = cli.get(name, "yuuno2:clip");
        return await RemoteClip.from_proxy(_proxy);
    }

    static async from_manager(name: string, cli: RpcClient, mgr: RemoteManager): Promise<RemoteClip> {
        add_clip_type(cli)
        let _proxy: _IClipProxy = await mgr.get(name, "yuuno2:clip");
        return await RemoteClip.from_proxy(_proxy);
    }
}