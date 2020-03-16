package dev.yuuno.networking.rpc;

public class RpcMalformattedException extends Exception {

    private Integer id;

    public RpcMalformattedException(String message) {
        this(null, message);
    }

    public RpcMalformattedException(Integer id, String message) {
        super(message);
        this.id = id;
    }

    public Integer getId() {
        return this.id;
    }
}
