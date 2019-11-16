package dev.yuuno.client.mocks;

import dev.yuuno.client.Frame;
import dev.yuuno.client.ImageUtils;
import dev.yuuno.client.RawFormat;
import dev.yuuno.client.Size;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import java.util.Collections;
import java.util.Map;

public class MockFrame implements Frame {

    private BufferedImage image;

    public MockFrame(Image image) {
        this.image = ImageUtils.toBufferedImage(image);
    }

    @Override
    public Size getSize() {
        return new Size(image.getWidth(), image.getHeight());
    }

    @Override
    public RawFormat getNativeFormat() {
        return RawFormat.RGB24;
    }

    @Override
    public boolean canRender(RawFormat format) {
        return RawFormat.RGB24.equals(format);
    }

    @Override
    public int renderInto(byte[] buffer, int plane, RawFormat format, int offset) {
        BufferedImage split = ImageUtils.split(image)[plane];
        byte[] src = ((DataBufferByte)split.getRaster().getDataBuffer()).getData();
        int targetLength = src.length;
        if (buffer.length - offset < targetLength) targetLength = buffer.length - offset;
        System.arraycopy(src, 0, buffer, offset, targetLength);
        return targetLength;
    }

    @Override
    public Map<String, String> getMetadata() {
        return Collections.emptyMap();
    }

    @Override
    public void close() throws Exception { }
}
