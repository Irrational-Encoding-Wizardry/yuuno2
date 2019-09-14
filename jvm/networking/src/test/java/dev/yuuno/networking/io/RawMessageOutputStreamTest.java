package dev.yuuno.networking.io;

import dev.yuuno.networking.Message;
import org.json.JSONObject;
import org.junit.Test;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.HashMap;

import static org.junit.Assert.*;

public class RawMessageOutputStreamTest {

    static class MockOutputStream extends OutputStream {
        boolean closed = false;

        @Override
        public void write(int i) throws IOException {

        }

        public void close() {
            closed = true;
        }

        public boolean isClosed() {
            return closed;
        }
    }

    private static byte[] serializeMessage(Message message) throws Exception {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        try(RawMessageOutputStream rmos = new RawMessageOutputStream(baos)) {
            rmos.writeMessage(message);
            return baos.toByteArray();
        }

    }

    private static byte[][] to2DBA(byte[]... data) {
        return data;
    }

    @Test
    public void writeMessage() throws Exception {
        HashMap<String, Object> empty = new HashMap<>();
        HashMap<String, Object> withData = new HashMap<>();
        withData.put("test", 1);

        assertArrayEquals(
                serializeMessage(new Message(empty)),
                new byte[]{0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x02, 0x7B, 0x7D}
        );

        assertArrayEquals(
                serializeMessage(new Message(withData)),
                new byte[]{0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x0A, 0x7B, 0x22, 0x74, 0x65, 0x73, 0x74, 0x22, 0x3A, 0x31, 0x7D}
        );

        assertArrayEquals(
                serializeMessage(new Message(empty, to2DBA(new byte[]{0x61, 0x62}))),
                new byte[]{0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x7B, 0x7D, 0x61, 0x62}
        );

        assertArrayEquals(
                serializeMessage(new Message(empty, to2DBA(new byte[]{0x61, 0x62}, new byte[]{0x63, 0x64}))),
                new byte[]{0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x7B, 0x7D, 0x61, 0x62, 0x63, 0x64}
        );

        assertArrayEquals(
                serializeMessage(new Message(withData, to2DBA(new byte[]{0x61, 0x62}, new byte[]{0x63, 0x64}))),
                new byte[]{0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x7B, 0x22, 0x74, 0x65, 0x73, 0x74, 0x22, 0x3A, 0x31, 0x7D, 0x61, 0x62, 0x63, 0x64}
        );
    }

    @Test
    public void close() throws Exception {
        MockOutputStream mos = new MockOutputStream();
        RawMessageOutputStream rmos = new RawMessageOutputStream(mos);
        rmos.close();
        assertTrue(mos.isClosed());
    }
}