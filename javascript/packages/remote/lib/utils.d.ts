export interface Closable {
    close(): Promise<void>;
}
export declare function using<T, R>(closable: T & Closable, cb: (obj: T) => Promise<R>): Promise<R>;
export declare function toObject(map: Map<string, string>): {
    [k: string]: string;
};
