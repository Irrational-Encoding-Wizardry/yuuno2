package dev.yuuno.networking;

import org.json.JSONObject;
import org.junit.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.*;

public class MessageTest {
    private static byte[][] to2DBA(byte[]... data) {
        return data;
    }

    private static Map<String, Object> empty() {
        return Collections.emptyMap();
    }

    private static Map<String, Object> withData() {
        Map<String, Object> withData = new HashMap<>();
        withData.put("test", 1);
        return withData;
    }

    private static byte[][] noBlock() {
        return to2DBA();
    }

    private static byte[][] oneBlock() {
        return to2DBA(new byte[]{0x61, 0x62});
    }

    private static byte[][] twoBlocks() {
        return to2DBA(new byte[]{0x61, 0x62}, new byte[]{0x63, 0x63});
    }

    @Test
    public void testArraySupport() {
        Map<String, Object> v = new Message(Arrays.<Object>asList(1, 2, 3)).getText();
        assertTrue(v.containsKey(""));
        assertEquals(Arrays.asList(1,2,3), v.get(""));
    }

    @Test
    public void testEquals() {
        ///
        // Ensure that values return the correct equality.
        assertEquals(empty(), empty());
        assertEquals(withData(), withData());
        assertNotEquals(empty(), withData());
        assertNotEquals(withData(), empty());

        assertTrue(Arrays.deepEquals(noBlock(), noBlock()));
        assertTrue(Arrays.deepEquals(oneBlock(), oneBlock()));
        assertTrue(Arrays.deepEquals(twoBlocks(), twoBlocks()));

        assertFalse(Arrays.deepEquals(noBlock(), oneBlock()));
        assertFalse(Arrays.deepEquals(noBlock(), twoBlocks()));
        assertFalse(Arrays.deepEquals(oneBlock(), noBlock()));
        assertFalse(Arrays.deepEquals(oneBlock(), twoBlocks()));
        assertFalse(Arrays.deepEquals(twoBlocks(), noBlock()));
        assertFalse(Arrays.deepEquals(twoBlocks(), oneBlock()));

        ///
        // Actual Test
        assertEquals(new Message(empty(), noBlock()), new Message(empty(), noBlock()));
        assertEquals(new Message(empty(), oneBlock()), new Message(empty(), oneBlock()));
        assertEquals(new Message(empty(), twoBlocks()), new Message(empty(), twoBlocks()));
        assertEquals(new Message(withData(), noBlock()), new Message(withData(), noBlock()));
        assertEquals(new Message(withData(), oneBlock()), new Message(withData(), oneBlock()));
        assertEquals(new Message(withData(), twoBlocks()), new Message(withData(), twoBlocks()));

        assertNotEquals(new Message(empty(), noBlock()), new Message(empty(), oneBlock()));
        assertNotEquals(new Message(empty(), noBlock()), new Message(empty(), twoBlocks()));
        assertNotEquals(new Message(empty(), noBlock()), new Message(withData(), noBlock()));
        assertNotEquals(new Message(empty(), noBlock()), new Message(withData(), oneBlock()));
        assertNotEquals(new Message(empty(), noBlock()), new Message(withData(), twoBlocks()));
        assertNotEquals(new Message(empty(), oneBlock()), new Message(empty(), noBlock()));
        assertNotEquals(new Message(empty(), oneBlock()), new Message(empty(), twoBlocks()));
        assertNotEquals(new Message(empty(), oneBlock()), new Message(withData(), noBlock()));
        assertNotEquals(new Message(empty(), oneBlock()), new Message(withData(), oneBlock()));
        assertNotEquals(new Message(empty(), oneBlock()), new Message(withData(), twoBlocks()));
        assertNotEquals(new Message(empty(), twoBlocks()), new Message(empty(), noBlock()));
        assertNotEquals(new Message(empty(), twoBlocks()), new Message(empty(), oneBlock()));
        assertNotEquals(new Message(empty(), twoBlocks()), new Message(withData(), noBlock()));
        assertNotEquals(new Message(empty(), twoBlocks()), new Message(withData(), oneBlock()));
        assertNotEquals(new Message(empty(), twoBlocks()), new Message(withData(), twoBlocks()));
        assertNotEquals(new Message(withData(), noBlock()), new Message(empty(), noBlock()));
        assertNotEquals(new Message(withData(), noBlock()), new Message(empty(), oneBlock()));
        assertNotEquals(new Message(withData(), noBlock()), new Message(empty(), twoBlocks()));
        assertNotEquals(new Message(withData(), noBlock()), new Message(withData(), oneBlock()));
        assertNotEquals(new Message(withData(), noBlock()), new Message(withData(), twoBlocks()));
        assertNotEquals(new Message(withData(), oneBlock()), new Message(empty(), noBlock()));
        assertNotEquals(new Message(withData(), oneBlock()), new Message(empty(), oneBlock()));
        assertNotEquals(new Message(withData(), oneBlock()), new Message(empty(), twoBlocks()));
        assertNotEquals(new Message(withData(), oneBlock()), new Message(withData(), noBlock()));
        assertNotEquals(new Message(withData(), oneBlock()), new Message(withData(), twoBlocks()));
        assertNotEquals(new Message(withData(), twoBlocks()), new Message(empty(), noBlock()));
        assertNotEquals(new Message(withData(), twoBlocks()), new Message(empty(), oneBlock()));
        assertNotEquals(new Message(withData(), twoBlocks()), new Message(empty(), twoBlocks()));
        assertNotEquals(new Message(withData(), twoBlocks()), new Message(withData(), noBlock()));
        assertNotEquals(new Message(withData(), twoBlocks()), new Message(withData(), oneBlock()));
    }
}