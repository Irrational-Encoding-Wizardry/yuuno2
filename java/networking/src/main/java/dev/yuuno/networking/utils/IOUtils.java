package dev.yuuno.networking.utils;

import javax.annotation.Nonnull;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;

public final class IOUtils {

    @Nonnull
    public static byte[] readNBytes(InputStream stream, int length) throws IOException
    {
        int pos = 0;
        byte[] data = new byte[length];
        while (pos < length) {
            int read = stream.read(data, pos, length-pos);
            if (read < 0) throw new EOFException();
            pos += read;
        }
        return data;
    }
}
