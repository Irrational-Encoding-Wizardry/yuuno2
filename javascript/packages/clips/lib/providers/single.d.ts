import { Script, ScriptProvider } from "../scripts";
export declare class SingleScriptProvider implements ScriptProvider {
    private _script;
    constructor(script: Script);
    get(options: object): Promise<Script>;
    close(): Promise<void>;
}
