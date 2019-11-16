package dev.yuuno.client;

import dev.yuuno.networking.Message;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class RpcFrame implements Frame {

    private final RpcClip source;
    private final int frameNumber;

    RpcFrame(RpcClip clip, int frameNumber) {
        this.source = clip;
        this.frameNumber = frameNumber;
    }

    private HashMap<String, Object> generateMessageContent() {
        HashMap<String, Object> arguments = new HashMap<>();
        arguments.put("frame", this.frameNumber);
        return arguments;
    }

    @Override
    public Size getSize() {
        List<Object> lo = this.source.getProtocol().size(new Message(generateMessageContent())).getTextAsList();
        if (lo == null) throw new RuntimeException("Did not get valid size object.");
        return Size.fromMessageFormat(lo);
    }

    @Override
    public RawFormat getNativeFormat() {
        List<Object> lo = this.source.getProtocol().format(new Message(generateMessageContent())).getTextAsList();
        if (lo == null) throw new RuntimeException("Did not get valid clip format.");
        return RawFormat.fromMessageFormat(lo);
    }

    @Override
    public boolean canRender(RawFormat format) {
        HashMap<String, Object> arguments = generateMessageContent();
        arguments.put("format", format.toMessageFormat());
        arguments.put("planes", null);
        Message response = this.source.getProtocol().render(new Message(arguments));
        return response.getText().get("size") instanceof List;
    }

    @Override
    public int renderInto(byte[] buffer, int plane, RawFormat format, int offset) {
        HashMap<String, Object> arguments = generateMessageContent();
        arguments.put("format", format.toMessageFormat());
        arguments.put("planes", null);
        Message response = this.source.getProtocol().render(new Message(arguments));
        if (!(response.getText().get("size") instanceof List))
            throw new IllegalArgumentException("Format not supported.");

        byte[] block = response.getBlocks()[0];
        int sz = block.length;
        if (sz > buffer.length-offset) sz = buffer.length-offset;
        System.arraycopy(block, 0, buffer, offset, sz);
        return sz;
    }

    @Override
    @SuppressWarnings("unchecked")
    public Map<String, String> getMetadata() {
        return (Map<String, String>)(Map)this.source.getProtocol().metadata(new Message(generateMessageContent())).getText();
    }

    @Override
    public void close() throws Exception { }
}
