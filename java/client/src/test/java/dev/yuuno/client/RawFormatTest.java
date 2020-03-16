package dev.yuuno.client;

import org.junit.Test;

import static org.junit.Assert.*;

public class RawFormatTest {

    @Test
    public void getBytesPerSample() {
        for (int i = 1; i<8; i++) {
            assertEquals(i,           new RawFormat((i*8-1), 1, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER).getBytesPerSample());
            assertEquals(i,           new RawFormat(i*8, 1, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER).getBytesPerSample());
            assertEquals(i+1, new RawFormat((i*8)+1, 1, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER).getBytesPerSample());

            assertEquals(i,           new RawFormat((i*8-1), 1, RawFormat.ColorFamily.RGB, RawFormat.SampleType.FLOAT).getBytesPerSample());
            assertEquals(i,           new RawFormat(i*8, 1, RawFormat.ColorFamily.RGB, RawFormat.SampleType.FLOAT).getBytesPerSample());
            assertEquals(i+1, new RawFormat((i*8)+1, 1, RawFormat.ColorFamily.RGB, RawFormat.SampleType.FLOAT).getBytesPerSample());
        }
    }

    @Test
    public void getNumPlanes() {
        assertEquals(1, new RawFormat(8, 1, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER, 0, 0, true, false).getNumPlanes());
        assertEquals(2, new RawFormat(8, 2, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER, 0, 0, true, false).getNumPlanes());
        assertEquals(1, new RawFormat(8, 1, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER, 0, 0, true, true).getNumPlanes());
        assertEquals(1, new RawFormat(8, 2, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER, 0, 0, true, true).getNumPlanes());
    }

    @Test
    public void getPlaneDimensions() {
        int[] subsamplingSizes = new int[]{200, 100};
        Size baseSize = new Size(subsamplingSizes[0], subsamplingSizes[0]);

        for (int sw = 0; sw<2; sw++) {
            for (int sh = 0; sh<2; sh++) {
                RawFormat yuvssf = new RawFormat(8, 3, RawFormat.ColorFamily.YUV, RawFormat.SampleType.INTEGER, sh, sw, false, true);
                assertEquals(yuvssf.getPlaneDimensions(0, baseSize), baseSize);
                assertEquals(yuvssf.getPlaneDimensions(1, baseSize), new Size(subsamplingSizes[sw], subsamplingSizes[sh]));
                assertEquals(yuvssf.getPlaneDimensions(2, baseSize), new Size(subsamplingSizes[sw], subsamplingSizes[sh]));
            }
        }
    }

    @Test
    public void getStride() {
        Size[] sizes = new Size[]{
                new Size(200, 200),
                new Size(201, 200),
                new Size(202, 200),
                new Size(203, 200)
        };
        int[] strides = new int[]{200, 204, 204, 204};

        RawFormat packed = new RawFormat(8, 1, RawFormat.ColorFamily.GREY, RawFormat.SampleType.INTEGER, 0, 0, true, true);
        RawFormat unpacked = new RawFormat(8, 1, RawFormat.ColorFamily.GREY, RawFormat.SampleType.INTEGER, 0, 0, false, true);
        for (int i = 0; i<4; i++) {
            assertEquals(strides[i], unpacked.getStride(0, sizes[i]));
            assertEquals(sizes[i].getWidth(), packed.getStride(0, sizes[i]));
        }
    }

    @Test
    public void getPlaneSize() {
        Size[] sizes = new Size[]{
                new Size(200, 200),
                new Size(201, 200),
                new Size(202, 200),
                new Size(203, 200)
        };

        for (int b = 1; b<5; b++) {
            RawFormat packed = new RawFormat(8*b, 1, RawFormat.ColorFamily.GREY, RawFormat.SampleType.INTEGER, 0, 0, true, true);
            RawFormat unpacked = new RawFormat(8*b, 1, RawFormat.ColorFamily.GREY, RawFormat.SampleType.INTEGER, 0, 0, false, true);

            for (int i = 0; i<4; i++) {
                Size sz = sizes[i];
                int stride = unpacked.getStride(0, sizes[i]);
                assertEquals(sz.getHeight()*stride*b, unpacked.getPlaneSize(0, sizes[i]));
                assertEquals(sz.getWidth() * sz.getHeight() * b, packed.getPlaneSize(0, sizes[i]));
            }
        }
    }

    @Test
    public void messageFormat() {
        assertEquals(RawFormat.RGB24, RawFormat.fromMessageFormat(RawFormat.RGB24.toMessageFormat()));
    }
}