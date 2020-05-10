import { Message } from '@yuuno2/networking'
import { WidgetModel } from '@jupyter-widgets/base'
import { ExternalConnection } from './base';


export class WidgetConnection extends ExternalConnection {
    private model: WidgetModel;

    constructor(model: WidgetModel) {
        super();

        this.model = model;
        this.model.on("msg:custom", this._receive, this);
    }

    private _receive(content: any, buffers: ArrayBuffer|ArrayBuffer[]) {
        if (content.type !== "yuuno2.message") return;
        if (!(buffers instanceof Array)) buffers = [buffers];

        this.receive({text: content.payload, blobs: buffers});
    }
    
    async send(message: Message): Promise<void> {
        this.model.send({type: "yuuno2.message", payload: message.text}, message.blobs);
    }

    async close(): Promise<void> {
        this.model.off("msg:custom", this._receive, this);
        await super.close();
    }

}