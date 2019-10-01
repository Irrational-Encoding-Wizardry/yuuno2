package dev.yuuno.networking.rpc;

import dev.yuuno.networking.Connection;
import dev.yuuno.networking.Message;

import javax.annotation.Nonnull;
import java.io.IOException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

public class RpcClient extends Thread implements AutoCloseable {

    private static final Method HASH_CODE_METHOD = getMethod(Object.class, "hashCode");
    private static final Method EQUALS_METHOD = getMethod(Object.class, "equals", Object.class);
    private static final Method TO_STRING_METHOD = getMethod(Object.class, "toString");
    private static final Method CLOSE_METHOD = getMethod(AutoCloseable.class, "close");

    private static Method getMethod(Class<?> src, String name, Class<?>... params) {
        try {
            return src.getMethod(name, params);
        } catch (NoSuchMethodException e) {
            e.printStackTrace();
            return null;
        }
    }

    private Connection connection;

    private AtomicBoolean closed = new AtomicBoolean(false);
    private AtomicInteger counter = new AtomicInteger(0);

    private Map<Integer, MessageFuture> waits = Collections.synchronizedMap(new HashMap<>());

    public RpcClient(Connection connection) {
        this.connection = connection;
        this.start();
    }

    public static <T extends ExportedProcedures> T forConnection(Connection conn, Class<T> cls) {
        RpcClient client = new RpcClient(conn);
        return client.makeProxy(cls);
    }

    public static <T extends ExportedProcedures> T forConnection(Connection conn, Class<T> cls, long t, TimeUnit tu) {
        RpcClient client = new RpcClient(conn);
        return client.makeProxy(cls, t, tu);
    }

    private void deliver(int id, Message message) {
        if (!waits.containsKey(id)) return;
        MessageFuture future = waits.remove(id);
        future.deliver(message);
    }

    private void deliverFailure(int id, String message) {
        Map<String, Object> fakeResult = new HashMap<>();
        fakeResult.put("id", id);
        fakeResult.put("type", "error");
        fakeResult.put("message", message);
        deliver(id, new Message(fakeResult));
    }

    public void run() {
        while (!this.closed.get())
            runOnce();
    }

    private void runOnce() {
        Message msg;
        try {
            msg = this.connection.readMessage();
        } catch (IOException e) {
            e.printStackTrace();
            this.closed.set(true);
            return;
        }

        if (msg == null) {
            this.closed.set(true);
            return;
        }

        Map<String, Object> value = msg.getText();
        if (!value.containsKey("id")) return;
        if (!(value.get("id") instanceof Integer)) return;
        int id = (Integer) value.get("id");

        if (!value.containsKey("type")) {
            deliverFailure(id, "No message type given.");
            return;
        }
        Object type = value.get("type");
        if (!(type instanceof String)) {
            deliverFailure(id, "Unexpected message type: " + type);
            return;
        }

        switch((String)type) {
            case "error":
                if (!value.containsKey("message"))
                    value.put("message", "");
                break;

            case "response":
                if (!value.containsKey("result"))
                    value.put("result", Collections.emptyMap());
                break;

            default:
                deliverFailure(id, "Unexpected message type: " + type);
                return;
        }

        msg.setText(value);
        deliver(id, msg);
    }

    public MessageFuture call(String method, Message value) {
        if (closed.get()) throw new RuntimeException("Connection closed.");
        MessageFuture result = new MessageFuture();
        int id = counter.incrementAndGet();
        waits.put(id, result);

        Map<String, Object> wrapped = new HashMap<>();
        wrapped.put("id", id);
        wrapped.put("type", "request");
        wrapped.put("method", method);
        wrapped.put("params", value.getText());

        try {
            this.connection.writeMessage(new Message(wrapped, value.getBlocks()));
        } catch (IOException|RuntimeException e) {
            deliverFailure(id, "Exception during message delivery: " + e.toString());
        }

        return result;
    }

    @SuppressWarnings("unchecked")
    public <T extends ExportedProcedures> T makeProxy(@Nonnull Class<T> procs, long t, @Nonnull  TimeUnit tu) {
        return (T) Proxy.newProxyInstance(procs.getClassLoader(), new Class<?>[]{procs, AutoCloseable.class}, (object, method, params) -> {
            if (method.equals(CLOSE_METHOD)) {
                close();
                return null;
            } else if (method.equals(EQUALS_METHOD)) {
                return object == params[0];
            } else if (method.equals(HASH_CODE_METHOD)) {
                return System.identityHashCode(object);
            } else if (method.equals(TO_STRING_METHOD)) {
                return "RpcProxy<Routing to " + RpcClient.this.toString() + ">";
            } else {
                MessageFuture mf = call(method.getName(), (Message) params[0]);
                if (t == 0)
                    return mf.get();
                else {
                    try {
                        return mf.get(t, tu);
                    } catch (TimeoutException e) {
                        throw new RpcCallFailed(e.getMessage(), e);
                    } catch (ExecutionException e) {
                        if (e.getCause() instanceof RpcCallFailed)
                            throw e.getCause();
                        return e;
                    }
                }
            }
        });
    }

    public <T extends ExportedProcedures> T makeProxy(@Nonnull Class<T> procs) {
        return makeProxy(procs, 0, TimeUnit.SECONDS);
    }

    @Override
    public void close() throws Exception {
        this.closed.get();
        this.connection.close();
        this.join();
    }
}
