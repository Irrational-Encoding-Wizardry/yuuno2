package dev.yuuno.client;

import java.awt.image.*;

public interface Frame extends MetadataContainer, AutoCloseable {

    /**
     * The size of the frame.
     */
    Size getSize();

    /**
     *  The native format of the frame.
     */
    RawFormat getNativeFormat();

    /**
     * Checks whether the format is supported by the backend of the frame.
     * @param format The format to check.
     * @return
     */
    boolean canRender(RawFormat format);

    /**
     * Renders a plane into the given buffer.
     * @param buffer The buffer to render into.
     * @param plane  The plane to render.
     * @param format The format of the image.
     * @param offset The offset where
     * @return How many bytes have been written.
     */
    int renderInto(byte[] buffer, int plane, RawFormat format, int offset);

    default int renderInto(byte[] buffer, int plane, RawFormat format) {
        return renderInto(buffer, plane, format, 0);
    }

    default BufferedImage render(int plane) {
        BufferedImage image = new BufferedImage(getSize().getWidth(), getSize().getHeight(), BufferedImage.TYPE_BYTE_GRAY);

        byte[] buffer = ((DataBufferByte)image.getData().getDataBuffer()).getData();
        assert buffer.length == RawFormat.RGB24.getPlaneSize(plane, getSize());
        renderInto(buffer, plane, RawFormat.RGB24);

        return image;
    }

    default BufferedImage render() {
        return ImageUtils.merge(render(0), render(1), render(2));
    }
}
