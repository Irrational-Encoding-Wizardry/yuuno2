package dev.yuuno.networking.io;

import dev.yuuno.networking.Message;
import org.json.JSONObject;
import org.junit.Test;

import java.io.ByteArrayInputStream;
import java.util.HashMap;

import static org.junit.Assert.*;

public class RawMessageInputStreamTest {

    private static Message readMessage(byte[] rawData) throws Exception {
        ByteArrayInputStream bais = new ByteArrayInputStream(rawData);
        try(RawMessageInputStream rmis = new RawMessageInputStream(bais)) {
            return rmis.readMessage();
        }
    }

    private static byte[][] to2DBA(byte[]... data) {
        return data;
    }

    @Test
    public void readMessage() throws Exception {
        HashMap<String, Object> empty = new HashMap<>();
        HashMap<String, Object> withData = new HashMap<>();
        withData.put("test", 1);

        byte[][] oneBlock = to2DBA(new byte[]{0x61, 0x62});
        byte[][] twoBlocks = to2DBA(new byte[]{0x61, 0x62}, new byte[]{0x63, 0x64});

        assertEquals(
                readMessage(new byte[]{0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x02, 0x7B, 0x7D}),
                new Message(empty)
        );

        assertEquals(
                readMessage(new byte[]{0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x0A, 0x7B, 0x22, 0x74, 0x65, 0x73, 0x74, 0x22, 0x3A, 0x31, 0x7D}),
                new Message(withData)
        );

        assertEquals(
                readMessage(new byte[]{0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x7B, 0x7D, 0x61, 0x62}),
                new Message(empty, oneBlock)
        );

        assertEquals(
                readMessage(new byte[]{0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x7B, 0x7D, 0x61, 0x62, 0x63, 0x64}),
                new Message(empty, twoBlocks)
        );

        assertEquals(
                readMessage(new byte[]{0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x7B, 0x22, 0x74, 0x65, 0x73, 0x74, 0x22, 0x3A, 0x31, 0x7D, 0x61, 0x62, 0x63, 0x64}),
                new Message(withData, twoBlocks)
        );

    }

    @Test
    public void close() {
    }
}