package dev.yuuno.networking.utils;

import java.util.concurrent.atomic.AtomicBoolean;

public class OptimisticLock {

    public interface ThrowingRunnable<T extends Throwable> {
        void run() throws T;
    }

    public class Lock implements AutoCloseable {

        private boolean closed = false;

        @Override
        public void close() {
            if (closed) return;
            closed = true;
            set.set(false);
            wake();
        }
    }

    private final AtomicBoolean set = new AtomicBoolean(false);

    public Lock acquire() throws IllegalMonitorStateException {
        if (set.getAndSet(true)) throw new IllegalMonitorStateException();
        return new Lock();
    }

    public <T extends Throwable> void when(ThrowingRunnable<T> acquired, ThrowingRunnable<T> notAcquired) throws T {
        if (set.getAndSet(true)) {
            try(Lock unused = new Lock()) {
                acquired.run();
            }
        } else {
            notAcquired.run();
        }
    }

    private void wake() {
        synchronized (set) {
            set.notify();
        }
    }

    public void wakeAll() {
        synchronized (set) {
            set.notifyAll();
        }
    }

    public void await() throws InterruptedException {
        synchronized (set) {
            while (!set.get())
                set.wait();
        }
    }
}
