/**
 * Yuuno - IPython + VapourSynth
 * Copyright (C) 2020 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
import {makeCounter} from './utils';


export class AggregateError extends Error
{
    private errors: any[];

    constructor(errors: any[])
    {
        super("Aggregated Exceptions from Handler: \n  " + errors.map(e => AggregateError.makeNice(e)).join("\n"));
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

export class Handler<T> {
    public static errorHandler: (error: any) => void = null;

    static idCounter: ()=>number = makeCounter();

    private handlers: {[id: number]: (ev: T)=>void} = {};

    public register(cb: (ev: T)=>Promise<void>|void): number {
        const newId = Handler.idCounter();
        this.handlers[newId] = cb;
        return newId;
    }

    public unregister(token: number) {
        delete this.handlers[token];
    }

    public async emit(ev: T): Promise<void> {
        let errors: any[] = [];
        let asyncEmits: Promise<any>[] = [];

        for (let cb of Object.values(this.handlers)) {
            let res: any = undefined;
            try {
                res = cb(ev);
            } catch (e) {
                errors.push(e);
                continue;
            }

            if (res instanceof Promise || (!!res && typeof res.then === 'function')) {
                asyncEmits.push(res.then(()=>{}, (err: any) => errors.push(err)));
            } else if (res instanceof Error) {
                errors.push(res);
            }
        }

        if (asyncEmits.length > 0) {
            await Promise.all(asyncEmits);
        }
        this.propagateError(errors);
    }


    private propagateError(errors: any[]): void {
        if (errors.length == 0) return;
        throw new AggregateError(errors);
    }

    public clear(): void {
        this.handlers = {};
    }
}