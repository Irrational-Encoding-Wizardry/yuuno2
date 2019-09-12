package dev.yuuno.networking;

import dev.yuuno.networking.utils.StreamUtils;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import java.io.IOException;
import java.util.stream.Stream;

public class SimpleConnection implements Connection {

    @Nonnull
    private MessageInputStream input;

    @Nonnull
    private MessageOutputStream output;

    public SimpleConnection(@Nonnull MessageInputStream input, @Nonnull MessageOutputStream output) {
        this.input = input;
        this.output = output;
    }

    @Nullable
    @Override
    public Message readMessage() throws IOException {
        return this.input.readMessage();
    }

    @Override
    public void writeMessage(@Nonnull Message message) throws IOException {
        this.output.writeMessage(message);
    }

    @Override
    public void close() throws Exception {
        StreamUtils.throwExceptions(StreamUtils.accumulateExceptions(Stream.of(input, output), AutoCloseable::close));
    }
}
