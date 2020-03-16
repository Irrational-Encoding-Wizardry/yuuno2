import { Clip } from "./base";
export declare type ConfigTypes = Uint8Array | string | number | null;
export interface Script {
    setConfig(key: string, value: ConfigTypes): Promise<void>;
    getConfig(key: string): Promise<ConfigTypes>;
    listConfig(): Promise<string[]>;
    run(code: string | ArrayBuffer): Promise<void>;
    listClips(): Promise<string[]>;
    getClip(name: string): Promise<Clip>;
    close(): Promise<void>;
}
export interface ScriptProvider {
    get(options: object): Promise<Script>;
    close(): Promise<void>;
}
