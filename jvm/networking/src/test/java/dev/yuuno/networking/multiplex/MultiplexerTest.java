package dev.yuuno.networking.multiplex;

import dev.yuuno.networking.*;
import dev.yuuno.networking.utils.Pair;
import org.graalvm.compiler.nodes.memory.MemoryCheckpoint;
import org.junit.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.*;

public class MultiplexerTest {

    class ShieldedSimpleConnection extends SimpleConnection {

        ShieldedSimpleConnection(MessageInputStream input, MessageOutputStream output) {
            super(input, output);
        }

        public void close() {}
    }

    private Message makeMessage(String channel, String type, Message payload) {
        if (payload == null) payload = new Message();
        Map<String, Object> text = new HashMap<>();
        text.put("target", channel);
        text.put("type", type);
        text.put("payload", payload.getText());
        return new Message(text, payload.getBlocks());
    }

    private Message generateBase() {
        Map<String, Object> text = new HashMap<>();
        text.put("time", System.currentTimeMillis());
        return new Message(text);
    }

    @Test(timeout=1000)
    public void connect() throws Exception {
        Pair<Connection, Connection> pipe = Pipe.bidirectional();
        try(Multiplexer multiplexer = new Multiplexer(pipe.getHead())) {
            Connection remote_side = pipe.getTail();
            try(Channel channel = multiplexer.connect("test-channel")) {
                Message msg = generateBase();
                remote_side.writeMessage(makeMessage("test-channel", "message", msg));
                assertEquals(msg, channel.readMessage());

                channel.writeMessage(msg);
                assertEquals(makeMessage("test-channel", "message", msg), remote_side.readMessage());
            }

            assertEquals(makeMessage("test-channel", "close", new Message()), remote_side.readMessage());
        }
    }

    @Test(timeout = 1000)
    public void unknown() throws Exception {
        Pair<Connection, Connection> pipe = Pipe.bidirectional();
        try(Multiplexer multiplexer = new Multiplexer(pipe.getHead())) {
            Connection remote_side = pipe.getTail();
            remote_side.writeMessage(makeMessage("unknown-channel", "message", new Message()));
            assertEquals(remote_side.readMessage(), makeMessage("unknown-channel", "close", new Message()));
        }
    }

    @Test(timeout = 1000)
    public void remoteClose() throws Exception {
        Pair<Connection, Connection> pipe = Pipe.bidirectional();
        try (Multiplexer multiplexer = new Multiplexer(pipe.getHead())) {
            Connection remote_side = pipe.getTail();
            try(Channel channel = multiplexer.connect("test-channel")) {
                remote_side.writeMessage(makeMessage("test-channel", "close", new Message()));
                Thread.sleep(100);
                assertTrue(channel.isClosed());
            }
        }
    }

    @Test(timeout = 1000)
    public void routing() throws Exception {
        Pair<Connection, Connection> pipe = Pipe.bidirectional();
        Connection remote_side = pipe.getTail();

        try (Multiplexer multiplexer = new Multiplexer(pipe.getHead())) {
            Channel c1 = multiplexer.connect("channel-1");
            Channel c2 = multiplexer.connect("channel-2");

            Message base1 = generateBase();

            remote_side.writeMessage(makeMessage("channel-1", "message", base1));
            assertEquals(c1.readMessage(), base1);

            Message base2 = generateBase();
            remote_side.writeMessage(makeMessage("channel-2", "message", base2));
            assertEquals(c2.readMessage(), base2);
        }
    }

    @Test(timeout=1000)
    public void massClose() throws Exception {
        Pair<Connection, Connection> pipe = Pipe.bidirectional();
        Connection remote_side = pipe.getTail();

        try (Multiplexer multiplexer = new Multiplexer(pipe.getHead())) {
            try (Multiplexer main = new Multiplexer(multiplexer.connect("additional"))) {
                try(Channel c1 = main.connect("channel-1")) {
                    try(Channel c2 = main.connect("channel-2")) {}
                }
            }

            Message close1 = remote_side.readMessage();
            Message close2 = remote_side.readMessage();

            assertNotNull(close1);
            assertNotNull(close2);
            assertNotEquals(close1, close2);
            assertTrue(
                    close1.equals(makeMessage("additional", "message", makeMessage("channel-1", "close", new Message()))) ||
                            close1.equals(makeMessage("additional", "message", makeMessage("channel-2", "close", new Message())))
            );
            assertTrue(
                    close2.equals(makeMessage("additional", "message", makeMessage("channel-1", "close", new Message()))) ||
                            close2.equals(makeMessage("additional", "message", makeMessage("channel-2", "close", new Message())))
            );
        }


    }
}