package dev.yuuno.client.mocks;

import dev.yuuno.client.ImageUtilsTest;
import dev.yuuno.client.RpcClip;
import dev.yuuno.networking.Message;
import org.junit.Before;
import org.junit.Test;

import javax.imageio.ImageIO;
import java.awt.*;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.*;

public class RpcClipProtocolImplTest {

    private MockClip clip;
    private RpcClip.Protocol protocol;

    private static Image loadImage() throws IOException {
        InputStream stream = ImageUtilsTest.class.getClassLoader().getResourceAsStream("ff8833.png");
        assert stream != null;
        return ImageIO.read(stream);
    }
    @Before
    public void setupClipAndProtocol() throws IOException {
        Map<String, String> metadata = new HashMap<>();
        metadata.put("object-id", "" + System.identityHashCode(this));

        Image img = loadImage();
        this.clip = new MockClip(new Image[]{img}, metadata);
        this.protocol = new RpcClipProtocolImpl(this.clip);
    }

    @Test
    public void metadata() {
        Message msg = this.protocol.metadata(new Message());
        assertTrue(msg.getText().containsKey("object-id"));
        assertEquals(System.identityHashCode(this), msg.getText().get("object-id"));
    }

    @Test
    public void length() {
    }

    @Test
    public void size() {
    }

    @Test
    public void format() {
    }

    @Test
    public void render() {
    }
}