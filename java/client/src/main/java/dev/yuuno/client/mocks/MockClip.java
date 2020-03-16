package dev.yuuno.client.mocks;

import dev.yuuno.client.Clip;
import dev.yuuno.client.Frame;

import java.awt.*;
import java.util.Map;

public class MockClip implements Clip {

    Image[] images;
    Map<String, String> metadata;

    public MockClip(Image[] images, Map<String, String> metadata) {
        this.images = images;
        this.metadata = metadata;
    }

    @Override
    public int size() {
        return this.images.length;
    }

    @Override
    public Frame getFrame(int frameno) {
        if (frameno >= this.images.length) return null;
        return new MockFrame(images[frameno]);
    }

    @Override
    public Map<String, String> getMetadata() {
        return metadata;
    }

    @Override
    public void close() throws Exception { }
}
