import { Connection } from './base';
export declare class Multiplexer {
    private conn;
    private controlToken;
    private streams;
    constructor(conn: Connection);
    register(name: string): Connection;
    close(): Promise<void>;
}
