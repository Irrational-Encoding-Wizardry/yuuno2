export interface Closable {
    close(): Promise<void>;
}


export async function using<T, R>(closable: T&Closable, cb: (obj: T) => Promise<R>) : Promise<R> {
    let result: R;
    try {
        result = await cb(closable);
    } finally {
        await closable.close();
    }
    return result;
}


export function toObject(map: Map<string, string>) : {[k: string]: string} {
    const obj: {[k: string]: string} = {};
    map.forEach((v, k) => obj[k] = v);
    return obj;
}

export function object2map(obj: {[k: string]: string}) : Map<string, string> {
    const map = new Map<string, string>();
    for (let k of Object.keys(obj))
        map.set(k, obj[k]);
    return map;
}