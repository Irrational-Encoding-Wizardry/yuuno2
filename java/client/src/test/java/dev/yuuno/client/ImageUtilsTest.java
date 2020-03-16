package dev.yuuno.client;

import org.junit.Test;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.color.ColorSpace;
import java.awt.image.*;
import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.Collections;
import java.util.Hashtable;

import static org.junit.Assert.*;

public class ImageUtilsTest {

    private static Image loadImage() throws IOException {
        InputStream stream = ImageUtilsTest.class.getClassLoader().getResourceAsStream("ff8833.png");
        assert stream != null;
        return ImageIO.read(stream);
    }

    private static int getSample(BufferedImage bi, int x, int y, int b) {
        return bi.getSampleModel().getSample(x, y, b, bi.getData().getDataBuffer());
    }

    private static BufferedImage gray8Simple(int width, int height, byte sample) {
        byte[] buffer = new byte[width*height];
        Arrays.fill(buffer, sample);

        ColorSpace cs = ColorSpace.getInstance(ColorSpace.CS_GRAY);
        ColorModel cm = new ComponentColorModel(cs, new int[]{8}, false, true, Transparency.OPAQUE, DataBuffer.TYPE_BYTE);
        SampleModel sm = cm.createCompatibleSampleModel(width, height);
        DataBufferByte dbb = new DataBufferByte(buffer, width*height);
        WritableRaster wr = Raster.createWritableRaster(sm, dbb, null);
        return new BufferedImage(cm, wr, false, null);
    }

    @Test
    public void toBufferedImage() throws Exception {
        Image src = loadImage();
        BufferedImage bi = ImageUtils.toBufferedImage(src);
        assertEquals(bi.getRGB(0, 0), 0xFFFF8833);
    }

    @Test
    public void split() throws Exception {
        Image base = loadImage();
        BufferedImage src = ImageUtils.toBufferedImage(base);
        BufferedImage[] imgs = ImageUtils.split(src);
        assertEquals(getSample(imgs[0], 0, 0, 0), 0xFF);
        assertEquals(getSample(imgs[1], 0, 0, 0), 0x88);
        assertEquals(getSample(imgs[2], 0, 0, 0), 0x33);
    }

    @Test
    public void merge() {
        BufferedImage r = gray8Simple(200, 200, (byte)0xFF);
        BufferedImage g = gray8Simple(200, 200, (byte)0x88);
        BufferedImage b = gray8Simple(200, 200, (byte)0x33);

        BufferedImage merged = ImageUtils.merge(r, g, b);
        assertEquals(merged.getRGB(0, 0), 0xFFFF8833);
    }
}