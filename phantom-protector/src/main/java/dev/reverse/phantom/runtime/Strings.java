package dev.reverse.phantom.runtime;

import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class Strings {
    private Strings() {}
    public static String decode(String value, int key) {
        byte[] bytes = Base64.getDecoder().decode(value);
        for (int i = 0; i < bytes.length; i++) bytes[i] ^= (byte) (key >>> ((i & 3) * 8));
        return new String(bytes, StandardCharsets.UTF_8);
    }
}
