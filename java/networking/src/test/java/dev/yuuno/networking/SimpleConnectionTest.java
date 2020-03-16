package dev.yuuno.networking;

import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.*;

public class SimpleConnectionTest {

    private static class MockInputStream implements MessageInputStream {
        private boolean closed = false;
        private int reads = 0;

        @Override
        public Message readMessage() throws IOException {
            reads++;
            return null;
        }

        @Override
        public void close() throws Exception {
            this.closed = true;
        }

        public int getReads() {
            return reads;
        }

        public boolean isClosed() {
            return closed;
        }
    }

    private static class MockOutputSteam implements MessageOutputStream {
        private boolean closed = false;
        private int writes = 0;

        @Override
        public void writeMessage(Message message) throws IOException {
            this.writes++;
        }

        @Override
        public void close() throws Exception {
            this.closed = true;
        }

        public int getWrites() {
            return this.writes;
        }

        public boolean isClosed() {
            return closed;
        }
    }

    @Test
    public void testReadMessage() throws Exception {
        MockInputStream mis = new MockInputStream();
        MockOutputSteam mos = new MockOutputSteam();

        SimpleConnection sc = new SimpleConnection(mis, mos);
        sc.readMessage();
        assertEquals(mis.getReads(), 1);
    }

    @Test
    public void testWriteMessage() throws Exception {
        MockInputStream mis = new MockInputStream();
        MockOutputSteam mos = new MockOutputSteam();

        SimpleConnection sc = new SimpleConnection(mis, mos);
        sc.writeMessage(new Message());
        assertEquals(mos.getWrites(), 1);
    }

    @Test
    public void close() throws Exception {
        MockInputStream mis = new MockInputStream();
        MockOutputSteam mos = new MockOutputSteam();

        SimpleConnection sc = new SimpleConnection(mis, mos);
        sc.close();
        assertTrue(mis.isClosed());
        assertTrue(mos.isClosed());
    }
}