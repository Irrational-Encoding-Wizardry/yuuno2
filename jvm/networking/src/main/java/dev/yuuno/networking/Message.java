package dev.yuuno.networking;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import java.util.Arrays;
import java.util.Collections;
import java.util.Map;
import java.util.Objects;

/**
 * A Message object represent a bit of data that is transmitted to or from
 * a Yuuno-Instance.
 *
 * A message contains a text-part and an arbitrary amount of binary buffers.
 *
 * The text part must always be representable by a JSONObject; however the underlying transports
 * may choose to serialize it in a different format.
 */
public final class Message {

    @Nonnull
    private Map<String, Object> text;

    @Nonnull
    private byte[][] blocks;

    public Message(@Nonnull Map<String, Object> text, @Nonnull  byte[][] blocks) {
        this.text = text;
        this.blocks = blocks;
    }

    public Message(@Nonnull Map<String, Object> text) {
        this(text, new byte[][]{});
    }

    public Message() {
        this(Collections.emptyMap());
    }

    @Nonnull
    public Map<String, Object> getText() {
        return text;
    }

    public void setText(@Nonnull Map<String, Object> text) {
        this.text = text;
    }

    @Nonnull
    public byte[][] getBlocks() {
        return blocks;
    }

    public void setBlocks(@Nonnull byte[][] blocks) {
        this.blocks = blocks;
    }

    @SuppressWarnings("unchecked")
    public static <T> T extract(Map<String, Object> map, String key, Class<T> type, T def) {
        if (!map.containsKey(key)) return def;
        Object value = map.get(key);
        if (value == null) return def;
        if (!type.isInstance(value)) return def;
        return (T)value;
    }

    public static <T> T extract(Map<String, Object> map, String key, Class<T> type) {
        return extract(map, key, type, null);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Message message = (Message) o;
        return Objects.equals(text, message.text) &&
                Arrays.deepEquals(blocks, message.blocks);
    }

    @Override
    public int hashCode() {
        int result = Objects.hash(text);
        result = 31 * result + Arrays.deepHashCode(blocks);
        return result;
    }

    @Override
    public String toString() {
        return "Message{" +
                "text=" + text +
                ", blocks=" + Arrays.deepToString(blocks) +
                '}';
    }
}
