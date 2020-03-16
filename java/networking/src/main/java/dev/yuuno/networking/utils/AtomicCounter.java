package dev.yuuno.networking.utils;

import java.util.concurrent.atomic.AtomicInteger;

public class AtomicCounter extends AtomicInteger {

    public class CountResource implements AutoCloseable {

        private final int value;
        private boolean closed = false;

        public CountResource() {
            value = AtomicCounter.this.incrementAndGet();
        }

        public int valueAtStart() {
            return value;
        }

        @Override
        public void close() {
            if (closed) return;
            closed = true;
            AtomicCounter.this.decrementAndGet();
        }
    }

    private AtomicInteger integer = new AtomicInteger();

    public CountResource incrementInside() {
        return new CountResource();
    }

}
