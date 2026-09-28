package dev.reverse.phantom;

import java.net.URI;
import java.nio.file.Path;

public record ProtectionConfig(Path input, Path output, Profile profile, String packagePrefix,
                               URI backend, long seed) {
    public ProtectionConfig {
        if (input == null || output == null || profile == null) throw new IllegalArgumentException("input, output and profile are required");
        packagePrefix = packagePrefix == null ? "" : packagePrefix.replace('.', '/').replaceAll("^/+|/+$", "");
        if (profile.renameClasses() && packagePrefix.isBlank()) throw new IllegalArgumentException("medium/heavy require --package-prefix");
        if (input.toAbsolutePath().normalize().equals(output.toAbsolutePath().normalize())) throw new IllegalArgumentException("input and output must differ");
    }
}
