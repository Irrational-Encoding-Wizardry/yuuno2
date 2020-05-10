import { MessageBus, Message, Connection } from '@yuuno2/networking'


export abstract class ExternalConnection implements Connection {
    private bus: MessageBus|null = new MessageBus();

    protected receive(msg: Message) {
        this.bus.send(msg).catch(console.log);
    }

    public registerMessageHandler(callback: (msg: Message) => void): number {
        return this.bus.registerMessageHandler(callback);
    }

    public unregisterMessageHandler(token: number): void {
        this.bus.unregisterMessageHandler(token);
    }
    
    public abstract send(message: Message): Promise<void>;

    public async close() : Promise<void> {
        if (this.bus !== null) {
            await this.bus.close();
        }
        this.bus = null;
    };

}