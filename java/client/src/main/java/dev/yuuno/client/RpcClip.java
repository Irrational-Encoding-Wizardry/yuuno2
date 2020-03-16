package dev.yuuno.client;

import dev.yuuno.networking.Message;
import dev.yuuno.networking.rpc.Exported;

import java.util.List;
import java.util.Map;

public class RpcClip implements Clip {

    public interface Protocol extends AutoCloseable {

        @Exported
        Message metadata(Message message);

        @Exported
        Message length(Message message);

        @Exported
        Message size(Message message);

        @Exported
        Message format(Message message);

        @Exported
        Message render(Message message);

    }

    private Protocol protocol;

    public RpcClip(Protocol protocol) {
        this.protocol = protocol;
    }

    Protocol getProtocol() {
        return this.protocol;
    }

    @Override
    public int size() {
        Message message = this.protocol.length(new Message());
        return (int)message.getText().get("length");
    }

    @Override
    public Frame getFrame(int frameno) {
        if (frameno >= size()) return null;
        return new RpcFrame(this, frameno);
    }

    @Override
    @SuppressWarnings("unchecked")
    public Map<String, String> getMetadata() {
        return (Map<String, String>)(Map)this.protocol.metadata(new Message()).getText();
    }

    @Override
    public void close() throws Exception {
        this.protocol.close();
    }

}
