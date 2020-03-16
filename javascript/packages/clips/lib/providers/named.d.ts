import { Script, ScriptProvider } from "../scripts";
export declare class NamedScriptProvider<K = string> implements ScriptProvider {
    private _parent;
    private _cache;
    private _optionName;
    constructor(parent: ScriptProvider, optionName?: string);
    get(options: {
        [p: string]: any;
    }): Promise<Script>;
    close(): Promise<void>;
}
