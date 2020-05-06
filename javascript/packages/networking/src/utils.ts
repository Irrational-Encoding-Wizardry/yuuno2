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
export const makeCounter: (start?: number, step?:number)=>()=>number = (function(start: number=0, step: number=1){
    return function counter() {
        let count: number = start;
        return function __increment() {
            const previous = count;
            count = count+step;
            return previous;
        }
    }
})();


export class PromiseDelegate<T> {

    private _promise: Promise<T>;
    private _deferred: ((rs: (val: T) => void, rj: (err: any) => void) => void) | null = null;
    private _resolve: (val: T) => void | null = null;
    private _reject: (err: any) => void | null = null;

    constructor() {
        this._deferred = null;
        this._resolve = null;
        this._reject = null;

        this._promise = new Promise<T>((rs, rj) => {
            this._resolve = (r) => rs(r);
            this._reject = (r) => rj(r);

            if (this._deferred !== null) {
                this._deferred(this._resolve, this._reject);
            }
        });
    }

    resolve(t: T) : void {
        if (this._resolve === null) {
            this._deferred = (rs, rj) => {rs(t)};
        } else {
            this._resolve(t);
        }
    }

    reject(reason: any) {
        if (this._reject === null) {
            this._deferred = (rs, rj) => {rj(reason)};
        } else {
            this._reject(reason);
        }
    }

    get promise() : Promise<T> {
        return this._promise;
    }
}