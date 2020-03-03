const { NamedScriptProvider } = require('../lib/providers/named');


class FakeScript {
    constructor(options) {
        this.open = true;
        this.options = options;
    }

    async getConfig(name) {
        return this.options[name];
    }

    async close() {
        this.open = false;
    };
}


class FakedScriptProvider {

    constructor() {
    }

    async get(options) {
        return new FakeScript(options);
    }

    async close() {

    }

}


describe('@yuuno2/clips', () => {
    describe('The NamedScriptProvider', () => {
        it('should cache the scripts by name', async () => {
            let provider = new NamedScriptProvider(new FakedScriptProvider());
            await expect((await provider.get({name: "test1", id: 1})).getConfig("id")).resolves.toBe(1);
            await expect((await provider.get({name: "test1", id: 2})).getConfig("id")).resolves.toBe(1);

            await expect((await provider.get({name: "test2", id: 3})).getConfig("id")).resolves.toBe(3);
            await expect((await provider.get({name: "test2", id: 4})).getConfig("id")).resolves.toBe(3);

            await expect((await provider.get({name: "test1", id: 1})).getConfig("id")).resolves.toBe(1);
        });


        it('should be able different option names', async() => {
            let provider = new NamedScriptProvider(new FakedScriptProvider(), "test");

            await expect((await provider.get({test: "test1", id: 1})).getConfig("id")).resolves.toBe(1);
            await expect((await provider.get({test: "test1", id: 2})).getConfig("id")).resolves.toBe(1);
        });

        it('should be able ignore missing names', async()=>{
            let provider = new NamedScriptProvider(new FakedScriptProvider());

            await expect((await provider.get({id: 1})).getConfig("id")).resolves.toBe(1);
            await expect((await provider.get({id: 2})).getConfig("id")).resolves.toBe(2);
        });

        it('should be able to handle closes', async()=>{
            let provider = new NamedScriptProvider(new FakedScriptProvider());

            let script = await provider.get({name: "test", id: 1});
            await script.close();
            await expect((await provider.get({name: "test", id: 2})).getConfig("id")).resolves.toBe(2);
            await (await provider.get({name: "test", id:3})).close();

            await expect((await provider.get({name: "test", id: 3})).getConfig("id")).resolves.toBe(3);
        });
    })
})