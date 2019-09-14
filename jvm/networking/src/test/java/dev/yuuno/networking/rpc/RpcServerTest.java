package dev.yuuno.networking.rpc;

import dev.yuuno.networking.Connection;
import dev.yuuno.networking.Message;
import dev.yuuno.networking.Pipe;
import dev.yuuno.networking.utils.Pair;
import org.junit.Test;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.*;

public class RpcServerTest {

    class TestExport implements ExportedProcedures {
        @Exported
        public Message succeed(Message in) {
            return in;
        }

        @Exported
        public Message fail(Message in) throws Exception {
            throw new IOException("Lolz.");
        }

        public Message unmarked(Message message) {
            return message;
        }
    }

    private static Message call(String methodName, Message message) {
        Map<String, Object> data = new HashMap<>();
        data.put("id", 12345);
        data.put("type", "request");
        data.put("method", methodName);
        data.put("params", message.getText());
        return new Message(data, message.getBlocks());
    }

    @Test
    public void rpcMissingId() throws Exception {
        Pair<Connection, Connection> connection = Pipe.bidirectional();
        Connection tail = connection.getTail();
        try(RpcServer server = new RpcServer(connection.getHead(), new TestExport())) {
            tail.writeMessage(new Message());
            Message msg = tail.readMessage();
            Map<String, Object> result = msg.getText();
            assertNull(result.get("id"));
            assertEquals(result.get("type"), "error");
        }
    }

    @Test
    public void rpcUnmarkedMethod() throws Exception {
        Pair<Connection, Connection> connection = Pipe.bidirectional();
        Connection tail = connection.getTail();
        try(RpcServer server = new RpcServer(connection.getHead(), new TestExport())) {
            tail.writeMessage(call("unmarked", new Message()));
            Message msg = tail.readMessage();
            Map<String, Object> result = msg.getText();
            assertEquals(result.get("id"), 12345);
            assertEquals(result.get("type"), "error");
        }
    }

    @Test
    public void rpcFail() throws Exception {
        Pair<Connection, Connection> connection = Pipe.bidirectional();
        Connection tail = connection.getTail();
        try(RpcServer server = new RpcServer(connection.getHead(), new TestExport())) {
            tail.writeMessage(call("fail", new Message()));
            Message msg = tail.readMessage();
            Map<String, Object> result = msg.getText();
            assertEquals(result.get("id"), 12345);
            assertEquals(result.get("type"), "error");
            assertTrue(result.get("message") instanceof String);
            assertTrue(((String) result.get("message")).contains("Lolz"));
        }
    }

    @Test
    public void rpcSucceed() throws Exception {
        Pair<Connection, Connection> connection = Pipe.bidirectional();
        Connection tail = connection.getTail();
        try(RpcServer server = new RpcServer(connection.getHead(), new TestExport())) {
            Map<String, Object> in = new HashMap<>();
            in.put("test", 34567);

            tail.writeMessage(call("succeed", new Message(in)));
            Message msg = tail.readMessage();
            Map<String, Object> result = msg.getText();
            assertEquals(result.get("id"), 12345);
            assertEquals(result.get("type"), "response");
            assertEquals(result.get("result"), in);
        }
    }
}