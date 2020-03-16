package dev.yuuno.networking;

import javax.annotation.Nonnull;
import java.io.IOException;

public interface MessageOutputStream extends AutoCloseable {

    /**
     * Write a message to the underlying IO.
     *
     * @param message      The message to write.
     * @throws IOException If an IO-Operation fails.
     */
    void writeMessage(@Nonnull Message message) throws IOException;

}
