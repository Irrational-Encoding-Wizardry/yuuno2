import { Clip } from '../base';
import { Script, ConfigTypes } from '../scripts';
import { k2a } from '../utils';
export class SimpleScript implements Script {

    private config: Map<string, ConfigTypes> = new Map<string, ConfigTypes>();
    private ctx: {[v: string]: any} = {};
    private clips: Map<string, Clip> = new Map<string, Clip>();

    constructor() {
        const $self = this;
        this.ctx.register = (name: string, clip: Clip) => $self.clips.set(name, clip);
    }

    async setConfig(key: string, value: ConfigTypes): Promise<void> {
        this.config.set(key, value);
    }
    async getConfig(key: string): Promise<ConfigTypes> {
        return this.config.get(key);
    }
    async listConfig(): Promise<string[]> {
        return k2a(this.config);
    }
    async run(code: string | ArrayBuffer): Promise<void> {
        if (code instanceof ArrayBuffer) { code = String.fromCharCode.apply(null, new Uint16Array(code)); }
        (()=>{eval(code as string);}).call(this.ctx);
    }
    async listClips(): Promise<string[]> {
        return k2a(this.clips);
    }
    async getClip(name: string): Promise<Clip> {
        return this.clips.get(name);
    }
    async close(): Promise<void> {
        this.ctx = null;
        this.clips = null;
    }


}