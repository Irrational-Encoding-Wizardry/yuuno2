export declare type JSONSerializable = null | number | string | Array<JSONSerializable> | JSONObject;
export declare type JSONObject = {
    [name: string]: JSONSerializable;
};
export declare type ByteArray = Uint8Array;
