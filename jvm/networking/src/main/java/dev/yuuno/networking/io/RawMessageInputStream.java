package dev.yuuno.networking.io;

import dev.yuuno.networking.Message;
import dev.yuuno.networking.MessageInputStream;
import dev.yuuno.networking.utils.IOUtils;
import org.json.JSONArray;
import org.json.JSONObject;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * A RawMessageInputStream-object wraps an input stream
 * and deserializes its messages.
 */
public class RawMessageInputStream implements MessageInputStream {

    @Nonnull
    private DataInputStream stream;

    public RawMessageInputStream(@Nonnull InputStream stream) {
        this.stream = new DataInputStream(stream);
    }

    @Nullable
    private LinkedList<byte[]> readPacket() throws IOException {
        int[] szBlocks = new int[stream.readShort()];
        LinkedList<byte[]> data = new LinkedList<>();
        for (int i = 0; i<szBlocks.length; i++) {
            szBlocks[i] = stream.readInt();
        }
        for (int length : szBlocks) {
            data.add(IOUtils.readNBytes(this.stream, length));
        }
        return data;
    }

    private Object fromJSON(@Nullable Object object) {
        if (object instanceof JSONObject)
            return fromJSONObject((JSONObject) object);
        else if (object instanceof JSONArray)
            return fromJSONArray((JSONArray) object);
        else
            return fromJSONScalar(object);
    }

    private Object fromJSONScalar(@Nullable Object object) {
        if (object == JSONObject.NULL) return null;
        return object;
    }

    private List<Object> fromJSONArray(JSONArray array) {
        ArrayList<Object> lst = new ArrayList<>(array.length());
        for (Object p : array)
            lst.add(fromJSON(p));
        return lst;
    }

    private Map<String, Object> fromJSONObject(JSONObject object) {
        HashMap<String, Object> map = new HashMap<>();
        for (String k : object.keySet())
            map.put(k, fromJSON(object.get(k)));
        return map;
    }

    @Nullable
    @Override
    public Message readMessage() throws IOException {
        for (;;) {
            LinkedList<byte[]> packet = this.readPacket();
            if (packet.size() < 1) continue;

            byte[] rawText = packet.removeFirst();
            JSONObject text = null;
            if (rawText.length > 0)
                text = new JSONObject(new String(rawText, StandardCharsets.UTF_8));

            return new Message(text==null?null:fromJSONObject(text), packet.toArray(new byte[0][]));
        }
    }

    @Override
    public void close() throws Exception {
        this.stream.close();
    }
}
