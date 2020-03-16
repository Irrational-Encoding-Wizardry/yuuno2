package dev.yuuno.networking;

import dev.yuuno.networking.utils.AtomicCounter;
import dev.yuuno.networking.utils.Pair;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Pipes are predominantly used for tests.
 *
 * They allow to test correct message handling without needing to serialize the
 * message.
 *
 * This decouples the actual implementations for message management from
 * the serialization code.
 */
public class Pipe implements Connection {

    private BlockingQueue<Optional<Message>> messageQueue = new LinkedBlockingQueue<>();

    private AtomicCounter waitCounter = new AtomicCounter();
    private AtomicBoolean closed = new AtomicBoolean();

    public Pipe() {}

    public static Pair<Connection, Connection> bidirectional() {
        Pipe a = new Pipe();
        Pipe b = new Pipe();

        return new Pair<>(new SimpleConnection(a, b), new SimpleConnection(b, a));
    }

    @Nullable
    @Override
    public Message readMessage() throws IOException {
        if (this.closed.get()) return null;

        try(AtomicCounter.CountResource c = waitCounter.incrementInside()) {
            return messageQueue.take().orElse(null);
        } catch (InterruptedException e) {
            throw new IOException("IO Operation was interrupted.");
        }
    }

    @Override
    public void writeMessage(@Nonnull Message message) throws IOException {
        if (this.closed.get()) return;
        if (!Objects.nonNull(message)) throw new IllegalArgumentException("Message must be non-null.");

        try {
            messageQueue.put(Optional.of(message));
        } catch (InterruptedException e) {
            throw new IOException("Message delivery was interrupted.");
        }
    }

    public boolean isEmpty() {
        return this.messageQueue.size() == 0;
    }

    public boolean isClosed() {
        return this.closed.get();
    }

    @Override
    public void close() throws Exception {
        if (this.closed.get()) return;
        this.closed.set(true);
        int count = waitCounter.get();
        if (count == 0) return;
        for (int i = 0; i<count; i++)
            this.messageQueue.put(Optional.empty());
    }
}
