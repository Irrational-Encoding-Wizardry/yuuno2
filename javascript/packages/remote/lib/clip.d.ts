import { Connection, RpcServer } from '@yuuno2/networking';
import { Clip } from '@yuuno2/clips';
export declare const RemoteClipServer: {
    create(connection: Connection, clip: Clip): RpcServer;
};
