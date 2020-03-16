package dev.yuuno.networking.rpc;

public class RpcCallFailed extends RuntimeException {

    public RpcCallFailed(String message) {
        super(message);
    }

    public RpcCallFailed(String message, Throwable cause) {
        super(message, cause);
    }

}
