package dev.yuuno.networking.rpc;

import dev.yuuno.networking.Connection;
import dev.yuuno.networking.Message;
import dev.yuuno.networking.Pipe;
import dev.yuuno.networking.utils.Pair;
import org.junit.Test;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;

import static org.junit.Assert.*;

public class RpcClientTest {

    interface TestInterface extends ExportedProcedures {
        Message succeed(Message in);
        Message fail(Message in) throws Exception;
    }

    class TestExport implements TestInterface {
        @Override
        @Exported
        public Message succeed(Message in) {
            return in;
        }

        @Override
        @Exported
        public Message fail(Message in) throws Exception {
            throw new IOException("Lolz.");
        }
    }

    @Test
    public void call() throws Exception {
        Pair<Connection, Connection> pipe = Pipe.bidirectional();
        try(RpcServer unused = new RpcServer(pipe.getHead(), new TestExport())) {
            try(RpcClient client = new RpcClient(pipe.getTail())) {
                Map<String, Object> data = new HashMap<>();
                data.put("someData", 54321);

                Message result = client.call("succeed", new Message(data)).get(5, TimeUnit.SECONDS);
                assertEquals(result.getText().get("someData"), 54321);

                try {
                    client.call("fail", new Message(data)).get(5, TimeUnit.SECONDS);
                    fail("Did not throw an exception.");
                } catch (ExecutionException rcf) {
                    assertTrue(rcf.getCause().getMessage().contains("Lolz"));
                }
            }
        }
    }

    @Test
    public void makeProxy() throws Exception {
        Pair<Connection, Connection> pipe = Pipe.bidirectional();
        try(RpcServer unused = new RpcServer(pipe.getHead(), new TestExport())) {
            try (RpcClient client = new RpcClient(pipe.getTail())) {
                Map<String, Object> data = new HashMap<>();
                data.put("someData", 54321);

                TestInterface ti = client.makeProxy(TestInterface.class, 5, TimeUnit.SECONDS);
                assertEquals(ti.succeed(new Message(data)), new Message(data));

                try {
                    ti.fail(new Message(data));
                    fail("Did not throw an exception.");
                } catch (RpcCallFailed rcf) {
                    assertTrue(rcf.getMessage().contains("Lolz"));
                }
            }
        }
    }

    @Test
    public void fastDeclaration() throws Exception {
        Pair<Connection, Connection> pipe = Pipe.bidirectional();
        try(RpcServer unused = new RpcServer(pipe.getHead(), new TestExport())) {
            TestInterface ti;
            try(AutoCloseable u = (AutoCloseable)(ti = RpcClient.forConnection(pipe.getTail(), TestInterface.class, 5, TimeUnit.SECONDS))) {
                Map<String, Object> data = new HashMap<>();
                data.put("someData", 54321);

                assertEquals(ti.succeed(new Message(data)), new Message(data));

                try {
                    ti.fail(new Message(data));
                    fail("Did not throw an exception.");
                } catch (RpcCallFailed rcf) {
                    assertTrue(rcf.getMessage().contains("Lolz"));
                }
            }
        }
    }
}