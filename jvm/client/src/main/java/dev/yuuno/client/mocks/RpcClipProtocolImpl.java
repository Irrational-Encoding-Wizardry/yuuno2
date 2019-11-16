package dev.yuuno.client.mocks;

import dev.yuuno.client.Clip;
import dev.yuuno.client.Frame;
import dev.yuuno.client.RawFormat;
import dev.yuuno.client.RpcClip;
import dev.yuuno.networking.Message;

import java.util.*;

public class RpcClipProtocolImpl implements RpcClip.Protocol {

    private Clip source;

    public RpcClipProtocolImpl(Clip source) {
        this.source = source;
    }

    @Override
    @SuppressWarnings("unchecked")
    public Message metadata(Message message) {
        return new Message((Map<String, Object>)(Map)this.source.getMetadata());
    }

    @Override
    public Message length(Message message) {
        Map<String, Object> result = new HashMap<>();
        result.put("length", this.source.size());
        return new Message(result);
    }

    @SuppressWarnings("unchecked")
    private <T> T getParameter(Message m, String param) {
        return (T)m.getText().get(param);
    }

    private boolean hasParameter(Message m, String param) {
        return m.getText().containsKey(param);
    }

    private <T> T getParameter(Message m, String param, T def) {
        if (!hasParameter(m, param)) return def;
        return getParameter(m, param);
    }

    @Override
    public Message size(Message message) {
        int frame = getParameter(message, "frame");
        return new Message(this.source.getFrame(frame).getSize().toMessageFormat());
    }

    @Override
    public Message format(Message message) {
        int frame = getParameter(message, "frame");
        return new Message(this.source.getFrame(frame).getNativeFormat().toMessageFormat());
    }

    @Override
    @SuppressWarnings("unchecked")
    public Message render(Message message) {
        int frame = getParameter(message, "frame");
        List<Object> format = getParameter(message, "format", null);
        Object planes = getParameter(message, "planes", null);

        Map<String, Object> response = new HashMap<>();

        Frame f = this.source.getFrame(frame);
        response.put("size", f.getSize().toMessageFormat());

        if (planes == null || format == null) { return new Message(response); }
        RawFormat rf = RawFormat.fromMessageFormat(format);

        if (planes instanceof Number) planes = Collections.singletonList((Integer) planes);
        List<Integer> planeList = (List<Integer>)planes;

        if (!f.canRender(rf)) {
            response.put("size", null);
            return new Message(response);
        }

        byte[][] buffers = new byte[planeList.size()][];
        for (int i = 0; i<buffers.length; i++) {
            int requestedPlane = planeList.get(i);
            byte[] planeBuffer = new byte[rf.getPlaneSize(requestedPlane, f.getSize())];
            f.renderInto(planeBuffer, requestedPlane, rf);
            buffers[i] = planeBuffer;
        }

        return new Message(response, buffers);
    }

    @Override
    public void close() throws Exception { }
}
