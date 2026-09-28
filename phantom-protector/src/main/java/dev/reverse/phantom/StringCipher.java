package dev.reverse.phantom;

import java.nio.charset.StandardCharsets;
import java.util.Base64;

public final class StringCipher {
    private StringCipher() {}

    public static String encrypt(String value, int key) {
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        for (int i = 0; i < bytes.length; i++) bytes[i] ^= (byte) (key >>> ((i & 3) * 8));
        return Base64.getEncoder().encodeToString(bytes);
    }

    public static String decrypt(String value, int key) {
        byte[] bytes = Base64.getDecoder().decode(value);
        for (int i = 0; i < bytes.length; i++) bytes[i] ^= (byte) (key >>> ((i & 3) * 8));
        return new String(bytes, StandardCharsets.UTF_8);
    }
}
