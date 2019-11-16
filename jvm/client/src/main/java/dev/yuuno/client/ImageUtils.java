package dev.yuuno.client;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import java.awt.image.Raster;

public final class ImageUtils {

    private ImageUtils(){}

    public static BufferedImage toBufferedImage(Image image) {
        BufferedImage target = new BufferedImage(image.getWidth(null), image.getHeight(null), BufferedImage.TYPE_3BYTE_BGR);
        Graphics g = target.getGraphics();
        g.drawImage(image, 0, 0, null);
        g.dispose();
        return target;
    }

    public static BufferedImage[] split(BufferedImage src) {
        int width = src.getWidth();
        int height = src.getHeight();

        BufferedImage r = new BufferedImage(width, height, BufferedImage.TYPE_BYTE_GRAY);
        BufferedImage g = new BufferedImage(width, height, BufferedImage.TYPE_BYTE_GRAY);
        BufferedImage b = new BufferedImage(width, height, BufferedImage.TYPE_BYTE_GRAY);

        Raster rr = r.getRaster();
        Raster rg = g.getRaster();
        Raster rb = b.getRaster();

        DataBufferByte dbbr = (DataBufferByte)rr.getDataBuffer();
        DataBufferByte dbbg = (DataBufferByte)rg.getDataBuffer();
        DataBufferByte dbbb = (DataBufferByte)rb.getDataBuffer();

        byte[] bar = dbbr.getData();
        byte[] bag = dbbg.getData();
        byte[] bab = dbbb.getData();

        eachPixel(src, (x, y) -> {
            int pos = (y*width)+x;
            int rgb = src.getRGB(x, y);
            bar[pos] = (byte) ((rgb&0x00FF0000)>>16);
            bag[pos] = (byte) ((rgb&0x0000FF00)>> 8);
            bab[pos] = (byte) ((rgb&0x000000FF));
        });
        return new BufferedImage[]{r, g, b};
    }

    public static BufferedImage merge(BufferedImage r, BufferedImage g, BufferedImage b) {
        int width = r.getWidth();
        int height = r.getHeight();

        BufferedImage rgb = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);

        Raster rr = r.getRaster();
        Raster rg = g.getRaster();
        Raster rb = b.getRaster();

        DataBufferByte dbbr = (DataBufferByte)rr.getDataBuffer();
        DataBufferByte dbbg = (DataBufferByte)rg.getDataBuffer();
        DataBufferByte dbbb = (DataBufferByte)rb.getDataBuffer();

        byte[] bar = dbbr.getData();
        byte[] bag = dbbg.getData();
        byte[] bab = dbbb.getData();

        byte[][] buffers = new byte[][]{bar, bag, bab};

        eachPixel(rgb, (x, y) -> {
            int pos = ((y*width)+x);
            int value = 0xFF;
            for (int i = 0; i<3; i++) {
                value = (value << 8) | buffers[i][pos];
            }
            rgb.setRGB(x, y, value);
        });
        return rgb;
    }

    private interface Function2I {
        void call(int a , int b);
    }

    private static void eachPixel(BufferedImage target, Function2I func) {
        int width = target.getWidth();
        int height = target.getHeight();

        for (int x = 0; x<width; x++) {
            for (int y = 0; y<height; y++) {
                func.call(x, y);
            }
        }
    }
}
