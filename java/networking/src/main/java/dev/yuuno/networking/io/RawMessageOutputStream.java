package dev.yuuno.networking.io;

import dev.yuuno.networking.Message;
import dev.yuuno.networking.MessageOutputStream;
import org.json.JSONObject;

import javax.annotation.Nonnull;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * A RawMessageOutputStream serializes messages written to
 * this object to the wrapped OutputStream object.
 */
public class RawMessageOutputStream implements MessageOutputStream {

    @Nonnull
    private DataOutputStream dos;

    public RawMessageOutputStream(@Nonnull OutputStream output) {
        this.dos = new DataOutputStream(output);
    }

    @Override
    public void writeMessage(@Nonnull Message message) throws IOException {
        String text = "";
        if (message.getText() != null)
            text = new JSONObject(message.getText()).toString();
        byte[] rawText = text.getBytes(StandardCharsets.UTF_8);

        this.dos.writeInt(message.getBlocks().length + 1);
        this.dos.writeInt(rawText.length);
        for (byte[] block : message.getBlocks())
            this.dos.writeInt(block.length);
        this.dos.write(rawText);
        for (byte[] block : message.getBlocks())
            this.dos.write(block);
    }

    @Override
    public void close() throws Exception {
        this.dos.close();
    }
}
