import { Script, ScriptProvider } from "../scripts";

export class SingleScriptProvider implements ScriptProvider {
    private _script: Script;

    constructor(script: Script) {
        this._script = script;
    }

    async get(options: object): Promise<Script> {
        return this._script;
    }
    async close(): Promise<void> {
        await this._script.close()
    }
}