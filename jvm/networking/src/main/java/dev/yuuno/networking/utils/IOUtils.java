package dev.yuuno.networking.utils;

import jdk.internal.jline.internal.Nullable;

import java.io.IOException;
import java.io.InputStream;

public final class IOUtils {

    @Nullable
    public static byte[] readNBytes(InputStream stream, int length) throws IOException
    {
        byte[] data = new byte[length];
        if (stream.read(data) < length) return null;
        return data;
    }
}
