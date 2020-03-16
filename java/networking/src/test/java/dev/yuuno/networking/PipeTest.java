package dev.yuuno.networking;

import dev.yuuno.networking.utils.Pair;
import org.junit.Test;

import java.io.IOException;
import java.util.concurrent.atomic.AtomicReference;

import static junit.framework.TestCase.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;

public class PipeTest {

    @Test
    public void bidirectional() throws Exception {
        Pair<Connection, Connection> bidi = Pipe.bidirectional();
        Connection a = bidi.getHead();
        Connection b = bidi.getTail();

        a.writeMessage(new Message());
        assertEquals(b.readMessage(), new Message());
        b.writeMessage(new Message());
        assertEquals(a.readMessage(), new Message());

        a.close();
        b.close();
    }

    @Test
    public void readMessage() throws Exception {
        Pipe p = new Pipe();
        p.writeMessage(new Message());
        assertEquals(p.readMessage(), new Message());
    }

    @Test
    public void close() throws Exception {
        final Pipe p = new Pipe();
        final AtomicReference<Message> ref = new AtomicReference<>(new Message());
        Thread t = new Thread(() -> {
            try {
                ref.set(p.readMessage());
            } catch (IOException e) {
                e.printStackTrace();
            }
        });
        t.start();
        p.close();
        t.join(1000);
        assertFalse(t.isAlive());
        assertNull(ref.get());
    }
}
