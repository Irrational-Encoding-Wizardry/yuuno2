package dev.yuuno.networking.multiplex;

import dev.yuuno.networking.Connection;
import dev.yuuno.networking.Message;
import dev.yuuno.networking.utils.StreamUtils;

import javax.annotation.Nonnull;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;

public class Multiplexer extends Thread implements AutoCloseable {

    private Connection connection;
    private AtomicBoolean alive = new AtomicBoolean(true);
    private Map<String, Channel> channelMap = Collections.synchronizedMap(new HashMap<>());

    public Multiplexer(Connection connection) {
        this.connection = connection;
        this.start();
    }

    public Channel connect(@Nonnull  String name) {
        if (channelMap.containsKey(name)) return channelMap.get(name);
        Channel ch = new Channel(name, this);
        channelMap.put(name, ch);
        return ch;
    }

    void unregisterChannel(String name) {
        channelMap.remove(name);
    }

    void writePacket(@Nonnull String channel, @Nonnull String type, @Nonnull Message message) throws IOException {
        Map<String, Object> wrapped = new HashMap<>();
        wrapped.put("target", channel);
        wrapped.put("type", type);
        wrapped.put("payload", message.getText());

        this.connection.writeMessage(new Message(wrapped, message.getBlocks()));
    }

    @Override
    public void run() {
        while (this.alive.get()) {
            try {
                runOnce();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        try { this.close(); } catch (Exception ignored) { }
    }

    private void runOnce() throws IOException {
        Message msg = this.connection.readMessage();
        if (msg == null) {
            try {
                this.close();
            } catch (Exception e) {
                throw new IOException("Failed to properly close.");
            }
            return;
        }
        Map<String, Object> text = msg.getText();
        String channel = Message.extract(text, "target", String.class, "");
        if (!channelMap.containsKey(channel)) {
            this.writePacket(channel, "close", new Message());
            return;
        }

        Channel inst = channelMap.get(channel);
        inst.deliver(msg);
    }

    @Override
    public void close() throws Exception {
        if (!this.alive.getAndSet(false)) return;
        try {
            StreamUtils.throwExceptions(
                    StreamUtils.accumulateExceptions(
                            new ArrayList<>(this.channelMap.values()).stream(),
                            AutoCloseable::close
                    )
            );
        } finally {
            this.connection.close();
        }
        this.join();
    }
}
