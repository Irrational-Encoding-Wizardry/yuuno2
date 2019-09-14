package dev.yuuno.networking.rpc;

import dev.yuuno.networking.Connection;
import dev.yuuno.networking.Message;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.io.Writer;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.atomic.AtomicBoolean;

public class RpcServer extends Thread implements AutoCloseable {

    private Connection connection;

    private ExportedProcedures procedures;

    private AtomicBoolean closed = new AtomicBoolean(false);

    public RpcServer(Connection connection, ExportedProcedures procedures) {
        super();

        this.connection = connection;
        this.procedures = procedures;

        this.start();
    }

    public void run() {
        while (!this.closed.get()) {
            try {
                try {
                    runOnce();
                } catch (RpcMalformattedException e) {
                    Map<String, Object> result = new HashMap<>();
                    result.put("id", e.getId());
                    result.put("type", "error");
                    result.put("message", e.getMessage());
                    this.connection.writeMessage(new Message(result));
                }
            } catch (IOException e) {
                e.printStackTrace();
                break;
            }
        }

        this.closed.set(true);
        try {
            this.connection.close();
        } catch (Exception ignored) {
        }
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> extractJSONObject(Map<String, Object> obj, String key) {
        if (!obj.containsKey(key)) return Collections.emptyMap();
        Object val = obj.get(key);
        if (!(val instanceof Map)) return Collections.emptyMap();
        return (Map<String, Object>)val;
    }

    private void runOnce() throws IOException, RpcMalformattedException {
        Message msg = connection.readMessage();
        if (msg == null) {
            this.closed.set(true);
            return;
        }

        Map<String, Object> values = msg.getText();
        if (!values.containsKey("id"))
            throw new RpcMalformattedException(null, "Request-ID missing from message");
        int id = (int)values.get("id");

        if (!values.containsKey("type"))
            throw new RpcMalformattedException(id, "Message does not contain a valid type.");
        if (!"request".equals(values.get("type")))
            throw new RpcMalformattedException(id, "Unknown request type: " + values.get("type").toString());

        if (!values.containsKey("method"))
            throw new RpcMalformattedException(id, "Message does not contain a valid method.");
        if (!(values.get("method") instanceof String))
            throw new RpcMalformattedException(id, "Request-Method is not a String.");

        Map<String, Object> params = extractJSONObject(values, "params");

        Message resultMessage;
        try {
            resultMessage = handleRequest((String) values.get("method"), new Message(params, msg.getBlocks()));
        } catch (RpcMalformattedException e) {
            throw new RpcMalformattedException(id, e.getMessage());
        } catch (ExecutionException e) {
            Writer result = new StringWriter();
            PrintWriter printWriter = new PrintWriter(result);
            e.getCause().printStackTrace(printWriter);
            throw new RpcMalformattedException(id, "An error occured while executing the function:\n" + result.toString());
        }

        Map<String, Object> rawResult = new HashMap<>();
        rawResult.put("id", id);
        rawResult.put("type", "response");
        rawResult.put("result", resultMessage.getText());

        this.connection.writeMessage(new Message(rawResult, resultMessage.getBlocks()));
    }

    private Message handleRequest(String method, Message message) throws RpcMalformattedException, ExecutionException {
        Class<? extends ExportedProcedures> cls = procedures.getClass();
        Method methodInst;
        try {
            methodInst = cls.getMethod(method, Message.class);
            if (methodInst.getAnnotation(Exported.class) == null)
                throw new NoSuchMethodException(method);
        } catch (NoSuchMethodException e) {
            throw new RpcMalformattedException("Unknown method: " + method);
        }

        try {
            Object raw = methodInst.invoke(procedures, message);
            if (!(raw instanceof Message))
                throw new RpcMalformattedException("Result is not a message?");

            return (Message)raw;
        } catch (IllegalAccessException e) {
            throw new RpcMalformattedException("You cannot access this method.");
        } catch (InvocationTargetException e) {
            throw new ExecutionException(e.getCause());
        }
    }

    @Override
    public void close() throws Exception {
        if (this.closed.get()) return;
        this.closed.set(true);
        this.connection.close();
        this.join();
    }
}
