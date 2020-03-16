export declare class AggregateError extends Error {
    private errors;
    constructor(errors: any[]);
    private static makeNice;
}
export declare class Handler<T> {
    static errorHandler: (error: any) => void;
    static idCounter: () => number;
    private handlers;
    register(cb: (ev: T) => Promise<void> | void): number;
    unregister(token: number): void;
    emit(ev: T): Promise<void>;
    private propagateError;
    clear(): void;
}
