package dev.yuuno.networking.rpc;

import java.lang.annotation.*;

/**
 *
 */
@Documented
@Inherited
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Exported {
}
