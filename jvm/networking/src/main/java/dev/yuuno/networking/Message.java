package dev.yuuno.networking;

import org.json.JSONObject;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import java.util.Arrays;
import java.util.Objects;

public final class Message {

    @Nullable
    private JSONObject text;

    @Nonnull
    private byte[][] blocks;

    public Message(@Nullable JSONObject text, @Nonnull  byte[][] blocks) {
        this.text = text;
        this.blocks = blocks;
    }

    public Message(@Nullable JSONObject text) {
        this(text, new byte[][]{});
    }

    public Message() {
        this(null);
    }

    @Nullable
    public JSONObject getText() {
        return text;
    }

    public void setText(@Nullable JSONObject text) {
        this.text = text;
    }

    @Nonnull
    public byte[][] getBlocks() {
        return blocks;
    }

    public void setBlocks(@Nonnull byte[][] blocks) {
        this.blocks = blocks;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Message message = (Message) o;
        return Objects.equals(text, message.text) &&
                Arrays.equals(blocks, message.blocks);
    }

    @Override
    public int hashCode() {
        int result = Objects.hash(text);
        result = 31 * result + Arrays.hashCode(blocks);
        return result;
    }

    @Override
    public String toString() {
        return "Message{" +
                "text=" + text +
                ", blocks=" + Arrays.toString(blocks) +
                '}';
    }
}
