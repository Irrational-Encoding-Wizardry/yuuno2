package dev.yuuno.client;

import java.awt.image.SampleModel;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;

public class RawFormat implements MessageSerializable {

    public static final RawFormat GRAY8 = new RawFormat(8, 1, ColorFamily.GREY, SampleType.INTEGER);
    public static final RawFormat RGB24 = new RawFormat(8, 3, ColorFamily.RGB, SampleType.INTEGER);
    public static final RawFormat RGBA32 = new RawFormat(8, 4, ColorFamily.RGB, SampleType.INTEGER);

    public enum SampleType {
        INTEGER,
        FLOAT
    }

    public enum ColorFamily {
        GREY,
        RGB,
        YUV
    }

    private final int bitsPerSample;
    private final int numFields;
    private final ColorFamily colorFamily;
    private final SampleType sampleType;
    private final int subsamplingH;
    private final int subsamplingW;
    private final boolean packed;
    private final boolean planar;

    public RawFormat(int bitsPerSample, int numFields, ColorFamily colorFamily, SampleType sampleType, int subsamplingH, int subsamplingW, boolean packed, boolean planar) {
        this.bitsPerSample = bitsPerSample;
        this.numFields = numFields;
        this.colorFamily = colorFamily;
        this.sampleType = sampleType;
        this.subsamplingH = subsamplingH;
        this.subsamplingW = subsamplingW;
        this.packed = packed;
        this.planar = planar;
    }

    public RawFormat(int bitsPerSample, int numFields, ColorFamily colorFamily, SampleType sampleType) {
        this(bitsPerSample, numFields, colorFamily, sampleType, 0, 0, true, true);
    }

    public int getBitsPerSample() {
        return bitsPerSample;
    }

    public int getNumFields() {
        return numFields;
    }

    public ColorFamily getColorFamily() {
        return colorFamily;
    }

    public SampleType getSampleType() {
        return sampleType;
    }

    public int getSubsamplingH() {
        return subsamplingH;
    }

    public int getSubsamplingW() {
        return subsamplingW;
    }

    public boolean isPacked() {
        return packed;
    }

    public boolean isPlanar() {
        return planar;
    }

    public int getBytesPerSample() {
        return ((this.bitsPerSample+7) / 8);
    }

    public int getNumPlanes() {
        if (this.planar) return this.numFields;
        return 1;
    }

    public Size getPlaneDimensions(int plane, Size size) {
        if (!this.planar) return size;

        int w = size.getWidth();
        int h = size.getHeight();

        if (0 < plane && plane < 4) {
            w >>= this.subsamplingW;
            h >>= this.subsamplingH;
        }

        return new Size(w, h);
    }

    public int getStride(int plane, Size size) {
        int stride = getPlaneDimensions(plane, size).getWidth();
        if (!this.packed)
            stride += stride%4;
        return stride;
    }

    public int getPlaneSize(int plane, Size size) {
        if (!this.planar)
            return this.getBytesPerSample() * this.numFields * size.getWidth() * size.getHeight();

        Size planeDimensions = getPlaneDimensions(plane, size);

        int width = planeDimensions.getWidth();
        int height = planeDimensions.getHeight();

        int stride = width * this.getBytesPerSample();
        if (!this.packed)
            stride += stride % 4;

        return height*stride;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        RawFormat rawFormat = (RawFormat) o;
        return bitsPerSample == rawFormat.bitsPerSample &&
                numFields == rawFormat.numFields &&
                subsamplingH == rawFormat.subsamplingH &&
                subsamplingW == rawFormat.subsamplingW &&
                packed == rawFormat.packed &&
                planar == rawFormat.planar &&
                colorFamily == rawFormat.colorFamily &&
                sampleType == rawFormat.sampleType;
    }

    @Override
    public int hashCode() {
        return Objects.hash(bitsPerSample, numFields, colorFamily, sampleType, subsamplingH, subsamplingW, packed, planar);
    }

    @Override
    public String toString() {
        return "RawFormat{" +
                "bitsPerSample=" + bitsPerSample +
                ", numFields=" + numFields +
                ", colorFamily=" + colorFamily +
                ", sampleType=" + sampleType +
                ", subsamplingH=" + subsamplingH +
                ", subsamplingW=" + subsamplingW +
                ", packed=" + packed +
                ", planar=" + planar +
                '}';
    }

    public static RawFormat fromMessageFormat(List<Object> message) {
        if (!"v1".equals(message.get(message.size()-1)))
            throw new IllegalArgumentException("This is not a format-object.");

        return new RawFormat(
                (int)message.get(0),
                (int)message.get(1),
                ColorFamily.values()[(int)message.get(2)],
                SampleType.values()[(int)message.get(3)],
                (int)message.get(4),
                (int)message.get(5),
                (boolean)message.get(6),
                (boolean)message.get(7)
        );
    }

    @Override
    public List<Object> toMessageFormat() {
        return Arrays.asList(
                this.bitsPerSample,
                this.numFields,
                this.colorFamily.ordinal(),
                this.sampleType.ordinal(),
                this.subsamplingH,
                this.subsamplingW,
                this.packed,
                this.planar,
                "v1"
        );
    }
}
