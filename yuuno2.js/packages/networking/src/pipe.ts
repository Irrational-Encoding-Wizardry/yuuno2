import {Connection} from './base';
import {MessageBus} from './messagebus';
import {SimpleConnection} from './connection';


export function pipe() : {first: Connection, second: Connection} {
    let bus1 = new MessageBus();
    let bus2 = new MessageBus();

    return {
        first: new SimpleConnection(bus1, bus2),
        second: new SimpleConnection(bus2, bus1)
    }
};