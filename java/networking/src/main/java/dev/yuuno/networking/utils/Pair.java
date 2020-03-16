package dev.yuuno.networking.utils;

import java.util.Objects;

public class Pair<A, B> {

    private final A head;
    private final B tail;

    public Pair(A head, B tail) {
        this.head = head;
        this.tail = tail;
    }

    public B getTail() {
        return tail;
    }

    public A getHead() {
        return head;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Pair<?, ?> pair = (Pair<?, ?>) o;
        return head.equals(pair.head) &&
                tail.equals(pair.tail);
    }

    @Override
    public int hashCode() {
        return Objects.hash(head, tail);
    }
}
