import { Clip } from '../base';
import { Script, ConfigTypes } from '../scripts';
export declare class SimpleScript implements Script {
    private config;
    private ctx;
    private clips;
    constructor();
    setConfig(key: string, value: ConfigTypes): Promise<void>;
    getConfig(key: string): Promise<ConfigTypes>;
    listConfig(): Promise<string[]>;
    run(code: string | ArrayBuffer): Promise<void>;
    listClips(): Promise<string[]>;
    getClip(name: string): Promise<Clip>;
    close(): Promise<void>;
}
