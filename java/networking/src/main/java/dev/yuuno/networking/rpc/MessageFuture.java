package dev.yuuno.networking.rpc;

import dev.yuuno.networking.Message;

import javax.annotation.Nonnull;
import java.util.Map;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

public class MessageFuture implements Future<Message> {

    private final CountDownLatch waiter = new CountDownLatch(1);
    private AtomicBoolean cancelled = new AtomicBoolean(false);
    private AtomicReference<Message> message = new AtomicReference<>();

    @Override
    public boolean cancel(boolean b) {
        if (isDone()) return false;
        cancelled.set(true);
        waiter.notifyAll();
        return true;
    }

    @Override
    public boolean isCancelled() {
        return cancelled.get();
    }

    @Override
    public boolean isDone() {
        return cancelled.get() || message.get() != null;
    }

    void deliver(Message message) {
        if (isDone()) return;
        this.message.set(message);
        waiter.countDown();
    }

    @SuppressWarnings("unchecked")
    private Message parseMessage() throws ExecutionException {
        if (isCancelled()) throw new CancellationException();

        Message raw = message.get();
        Map<String, Object> rawText = raw.getText();
        if (rawText.get("type") == "error") {
            throw new ExecutionException("RPC-Call failed.", new RpcCallFailed(rawText.get("message").toString()));
        }
        Map<String, Object> unwrapped = (Map<String, Object>)rawText.get("result");
        return new Message(unwrapped, raw.getBlocks());
    }

    @Override
    public Message get() throws InterruptedException, ExecutionException {
        if (isDone()) return parseMessage();
        waiter.await();
        return parseMessage();
    }

    @Override
    public Message get(long l, @Nonnull TimeUnit timeUnit) throws InterruptedException, ExecutionException, TimeoutException {
        if (isDone()) return parseMessage();
        waiter.await(l, timeUnit);
        if (!isDone()) throw new TimeoutException("This is taking too long.");
        return parseMessage();
    }
}
