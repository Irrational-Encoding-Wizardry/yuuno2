package dev.yuuno.networking.multiplex;

import dev.yuuno.networking.Connection;
import dev.yuuno.networking.Message;
import dev.yuuno.networking.Pipe;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import java.io.IOException;
import java.util.Collections;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;

public class Channel implements Connection {

    @Nonnull
    private String name;

    private Pipe pipe = new Pipe();

    @Nonnull
    private Multiplexer multiplexer;

    public Channel(@Nonnull String name, @Nonnull Multiplexer multiplexer) {
        this.name = name;
        this.multiplexer = multiplexer;
    }

    private void ensureStillOpen() throws IOException {
        if (isClosed()) throw new IOException("Channel closed.");
    }

    @SuppressWarnings("unchecked")
    void deliver(Message message) throws IOException {
        ensureStillOpen();

        Map<String, Object> frame = message.getText();
        switch((String)frame.getOrDefault("type", "message")) {
            case "illegal":
            case "close":
                try {
                    this.performClose(false);
                } catch (Exception e) {
                    throw new IOException("Failed to deliver failure packet.", e);
                }
                break;

            case "message":
                Map<String, Object> text = message.getText();
                Object rawPayload = text.get("payload");
                Map<String, Object> payload;
                if (!(rawPayload instanceof Map)) {
                    payload = (Map<String, Object>)Collections.EMPTY_MAP;
                } else {
                    payload = (Map<String, Object>)rawPayload;
                }
                this.pipe.writeMessage(new Message(payload, message.getBlocks()));
                break;

            default:
                try {
                    this.performClose(true);
                } catch (Exception e) {
                    throw new IOException("Failed to deliver failure packed.", e);
                }
        }
    }

    @Nullable
    @Override
    public Message readMessage() throws IOException {
        if (isClosed()) return null;
        return this.pipe.readMessage();
    }

    @Override
    public void writeMessage(@Nonnull Message message) throws IOException {
        ensureStillOpen();
        this.multiplexer.writePacket(this.name, "message", message);
    }

    @Override
    public void close() throws Exception {
        performClose(true);
    }

    public boolean isClosed() {
        return this.pipe.isClosed();
    }

    private void performClose(boolean notify) throws Exception {
        if (this.pipe.isClosed()) return;
        this.multiplexer.unregisterChannel(this.name);
        if (notify) this.multiplexer.writePacket(this.name, "close", new Message());
        this.pipe.close();
    }
}
