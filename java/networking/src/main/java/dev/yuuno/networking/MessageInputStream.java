package dev.yuuno.networking;

import javax.annotation.Nullable;
import java.io.IOException;

public interface MessageInputStream extends AutoCloseable {

    /**
     * Read a message from the stream.
     *
     * @return A new message or null if closed.
     * @throws IOException If the reading fails.
     */
    @Nullable
    Message readMessage() throws IOException;

}
