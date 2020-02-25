let makeCounter: (start?: number, step?:number)=>()=>number = (function(start: number=0, step: number=1){
    return function counter() {
        let count: number = start;
        return function __increment() {
            const previous = count;
            count+=step;
            return previous;
        }
    }
})();


export class Handler<T> {
    static idCounter: ()=>number = makeCounter();

    private handlers: {[id: number]: (ev: T)=>void} = {};

    public register(cb: (ev: T)=>void): number {
        const newId = Handler.idCounter();
        this.handlers[newId] = cb;
        return newId;
    }

    public unregister(token: number) {
        delete this.handlers[token];
    }

    public async emit(ev: T): Promise<any[]|null> {
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

            if (res instanceof Promise || typeof res.then === 'function') {
                asyncEmits.push(res);
                res.then(()=>{}, (err: any) => errors.push(err));
            } else if (res instanceof Error) {
                errors.push(res);
            }
        }

        if (asyncEmits.length == 0) {
            return Promise.resolve(errors.length == 0 ? null : errors);
        } else {
            return Promise.all(asyncEmits.map((p) => new Promise((rs) => p.then(rs, rs)))).then(() => errors.length==0 ? null : errors);
        }
    }

    public clear(): void {
        this.handlers = {};
    }
}