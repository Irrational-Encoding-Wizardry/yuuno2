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
