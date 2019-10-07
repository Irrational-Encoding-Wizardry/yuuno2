package dev.yuuno.client;

/**
 * Reprensents a basic clip.
 */
public interface Clip extends MetadataContainer, AutoCloseable {

    int size();

    Frame getFrame();

}
