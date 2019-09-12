package dev.yuuno.networking.utils;

import java.util.Iterator;
import java.util.List;
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public final class StreamUtils {
    public interface ThrowingConsumer<T> {
        void execute(T obj) throws Exception;
    }

    public interface CheckedFunction<T, R, E extends Throwable> {
        R apply(T value) throws E;
    }

    public static <T> Stream<Exception> accumulateExceptions(Stream<T> stream, ThrowingConsumer<T> op) {
        return stream.map((v) -> {
            try
            {
                op.execute(v);
            } catch (Exception e)
            {
                return e;
            }
            return null;
        });
    }

    public static void throwExceptions(Stream<Exception> stream) throws Exception
    {
        List<Exception> exceptions = stream.filter(Objects::nonNull).collect(Collectors.toList());
        if (exceptions.size() == 0) return;
        Exception last = exceptions.remove(exceptions.size()-1);
        for (Exception t : exceptions) last.addSuppressed(t);
        throw last;
    }
}
