package dev.reverse.phantom.cli;

import dev.reverse.phantom.*;
import dev.reverse.phantom.backend.*;

import java.net.URI;
import java.nio.file.Path;
import java.util.*;

public final class Main {
    public static void main(String[] args) throws Exception {
        if (args.length == 0 || !args[0].equals("protect")) {
            System.err.println("Usage: protect --input FILE.jar --output FILE.jar --level light|medium|heavy [--package-prefix pkg.path] [--backend URL] [--seed N]");
            System.exit(2);
        }
        Map<String, String> options = parse(args);
        ProtectionConfig config = new ProtectionConfig(Path.of(required(options, "--input")), Path.of(required(options, "--output")),
                Profile.parse(required(options, "--level")), options.getOrDefault("--package-prefix", ""),
                options.containsKey("--backend") ? URI.create(options.get("--backend")) : null,
                Long.parseLong(options.getOrDefault("--seed", Long.toString(System.nanoTime()))));
        JarProtector.Result result = new JarProtector().protect(config);
        if (config.backend() != null) {
            VerificationBackend.Decision decision = new HttpVerificationBackend().verify(config.backend(), result.outputSha256(), config.profile().name());
            if (config.profile().strictBackend() && !decision.accepted()) throw new IllegalStateException("strict backend verification failed: " + decision.message());
            System.out.printf("backend.accepted=%s backend.buildId=%s%n", decision.accepted(), decision.buildId());
        } else if (config.profile().strictBackend()) throw new IllegalStateException("heavy profile requires --backend");
        System.out.printf("input.sha256=%s%noutput.sha256=%s%nclasses.changed=%d%nstrings.encrypted=%d%nmappings=%s%n",
                result.inputSha256(), result.outputSha256(), result.classesChanged(), result.stringsEncrypted(), result.mappingFile());
    }

    private static Map<String, String> parse(String[] args) {
        Map<String, String> result = new HashMap<>();
        for (int i = 1; i < args.length; i += 2) {
            if (i + 1 >= args.length || !args[i].startsWith("--")) throw new IllegalArgumentException("expected option and value: " + args[i]);
            result.put(args[i], args[i + 1]);
        }
        return result;
    }

    private static String required(Map<String, String> options, String key) {
        String value = options.get(key);
        if (value == null || value.isBlank()) throw new IllegalArgumentException("missing " + key);
        return value;
    }
}
