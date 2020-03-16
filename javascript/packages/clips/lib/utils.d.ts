export declare class AggregateError extends Error {
    private errors;
    constructor(errors: any[]);
    private static makeNice;
}
export declare function k2a<K, V>(map: Map<K, V>): K[];
export declare function v2a<K, V>(map: Map<K, V>): V[];
