export type JSONSerializable = null|number|string|Array<JSONSerializable>|JSONObject;
export type JSONObject = {[name: string]: JSONSerializable};
export type ByteArray = Uint8Array;