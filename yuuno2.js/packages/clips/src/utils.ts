export class AggregateError extends Error
{
    private errors: any[];

    constructor(errors: any[])
    {
        super("Aggregated Exceptions: \n  " + errors.map(e => AggregateError.makeNice(e)).join("\n"));
        this.errors = errors;
        Object.setPrototypeOf(this, new.target.prototype);
    }

    private static makeNice(obj: any) : string {
        if (obj instanceof Error) {
            return `  ${obj.name}: ${obj.message}\n    ${obj.stack.split("\n").map(l => "    "+l).join("\n")}`
        }
        return "  " + obj.toString();
    }
}


export function k2a<K, V>(map: Map<K, V>): K[] {
        if (typeof map.keys === 'function') return Array.from(map.keys());
        const ary: K[] = [];
        map.forEach((_, k) => ary.push(k));
        return ary;
}

export function v2a<K, V>(map: Map<K, V>): V[] {
        if (typeof map.keys === 'function') return Array.from(map.values());
        const ary: V[] = [];
        map.forEach(v => ary.push(v));
        return ary;

}