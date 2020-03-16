import { Script, ScriptProvider, ConfigTypes } from "../scripts";
import { Clip } from "../base";
import { v2a, AggregateError } from "../utils";

class CloseForwardingScript implements Script {
    private _parent: Script;
    private _onClose: ()=>void;
    
    constructor(parent: Script, onClose: ()=>void) {
        this._parent = parent;
        this._onClose = onClose;
    }

    async setConfig(key: string, value: ConfigTypes): Promise<void> {
        await this._parent.setConfig(key, value);
    }
    async getConfig(key: string): Promise<ConfigTypes> {
        return await this._parent.getConfig(key);
    }
    async listConfig(): Promise<string[]> {
        return await this._parent.listConfig();
    }
    async run(code: string | ArrayBuffer): Promise<void> {
        await this._parent.run(code);
    }
    async listClips(): Promise<string[]> {
        return await this._parent.listClips();
    }
    async getClip(name: string): Promise<Clip> {
        return await this._parent.getClip(name);
    }
    async close(): Promise<void> {
        try {
            await this._parent.close();
        } finally {
            this._onClose();
        }
    }
}

export class NamedScriptProvider<K = string> implements ScriptProvider {

    private _parent: ScriptProvider;
    private _cache: Map<K, Script> = new Map<K, Script>();
    private _optionName: string;

    public constructor(parent: ScriptProvider, optionName: string = "name") {
        this._parent = parent;
        this._optionName = optionName;
    }

    async get(options: {[p: string]: any}): Promise<Script> {
        if (options[this._optionName] === undefined) return await this._parent.get(options);
        const name: K = options[this._optionName] as K;
        delete options[this._optionName];
        if (this._cache.has(name)) return this._cache.get(name);
        const script = new CloseForwardingScript(await this._parent.get(options), ()=>this._cache.delete(name));
        this._cache.set(name, script);
        return script;
    }
    async close(): Promise<void> {
        const pAry: Promise<void>[] = [];
        const errs: any[] = [];
        v2a(this._cache).map(async(p) => await p.close().then((r)=>r, (e) => errs.push(e)));
        
        await Promise.all(pAry);
        if (errs.length > 0)
            throw new AggregateError(errs);

        await this._parent.close();
    }
}