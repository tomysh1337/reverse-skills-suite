package dev.reverse.phantom;

import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.Type;
import org.objectweb.asm.commons.ClassRemapper;
import org.objectweb.asm.commons.Remapper;
import org.objectweb.asm.tree.*;
import org.objectweb.asm.util.CheckClassAdapter;

import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.jar.*;

public final class JarProtector {
    public record Result(String inputSha256, String outputSha256, int classesChanged, int stringsEncrypted,
                         Map<String, String> classMapping, Path mappingFile) {}

    private final MinecraftKeepRules keepRules = new MinecraftKeepRules();

    public Result protect(ProtectionConfig config) throws IOException {
        if (!Files.isRegularFile(config.input())) throw new FileNotFoundException("input JAR not found: " + config.input());
        Files.createDirectories(config.output().toAbsolutePath().getParent());
        String inputHash = sha256(config.input());
        int key = new Random(config.seed()).nextInt();
        Map<String, String> mappings = new TreeMap<>();
        Map<String, byte[]> entries = readEntries(config.input());
        for (var entry : entries.entrySet()) {
            String name = entry.getKey();
            if (!name.endsWith(".class")) continue;
            ClassReader reader = new ClassReader(entry.getValue());
            String className = reader.getClassName();
            if (keepRules.keep(name, entry.getValue())) continue;
            if (!config.packagePrefix().isBlank() && !className.startsWith(config.packagePrefix() + "/")) continue;
            if (config.profile().renameClasses()) mappings.put(className, renamed(className, config.seed()));
        }
        int changed = 0;
        int[] encrypted = {0};
        Map<String, byte[]> outputEntries = new TreeMap<>();
        for (var entry : entries.entrySet()) {
            String name = entry.getKey();
            byte[] bytes = entry.getValue();
            if (name.endsWith(".class")) {
                String internal = name.substring(0, name.length() - 6);
                boolean eligible = !keepRules.keep(name, bytes) && (config.packagePrefix().isBlank() || internal.startsWith(config.packagePrefix() + "/"));
                if (eligible) {
                    ClassNode node = new ClassNode();
                    new ClassReader(bytes).accept(node, 0);
                    encryptStrings(node, key, encrypted);
                    ClassWriter writer = new ClassWriter(ClassWriter.COMPUTE_MAXS);
                    if (config.profile().renameClasses()) {
                        Remapper remapper = new Remapper() {
                            @Override public String map(String internalName) { return mappings.getOrDefault(internalName, internalName); }
                        };
                        node.accept(new ClassRemapper(writer, remapper));
                    } else node.accept(writer);
                    bytes = writer.toByteArray();
                    verify(bytes);
                    changed++;
                    String mapped = mappings.get(internal);
                    if (mapped != null) name = mapped + ".class";
                }
            }
            outputEntries.put(name, bytes);
        }
        writeEntries(config.output(), outputEntries);
        Path mappingFile = config.output().resolveSibling(config.output().getFileName() + ".mapping.txt");
        List<String> mapLines = new ArrayList<>();
        mappings.forEach((from, to) -> mapLines.add(from.replace('/', '.') + " -> " + to.replace('/', '.') + ":"));
        Files.write(mappingFile, mapLines);
        return new Result(inputHash, sha256(config.output()), changed, encrypted[0], Map.copyOf(mappings), mappingFile);
    }

    private static void encryptStrings(ClassNode node, int key, int[] encrypted) {
        for (MethodNode method : node.methods) {
            InsnList replacement = new InsnList();
            for (AbstractInsnNode insn = method.instructions.getFirst(); insn != null; ) {
                AbstractInsnNode next = insn.getNext();
                if (insn instanceof LdcInsnNode ldc && ldc.cst instanceof String value && !value.isEmpty()) {
                    ldc.cst = StringCipher.encrypt(value, key);
                    replacement.add(new LdcInsnNode(ldc.cst));
                    replacement.add(new LdcInsnNode(key));
                    replacement.add(new MethodInsnNode(Opcodes.INVOKESTATIC, "dev/reverse/phantom/runtime/Strings", "decode", "(Ljava/lang/String;I)Ljava/lang/String;", false));
                    method.instructions.insertBefore(ldc, replacement);
                    method.instructions.remove(ldc);
                    replacement = new InsnList();
                    encrypted[0]++;
                }
                insn = next;
            }
        }
    }

    private static String renamed(String internalName, long seed) {
        int slash = internalName.lastIndexOf('/');
        String pkg = slash < 0 ? "" : internalName.substring(0, slash + 1);
        String shortName = slash < 0 ? internalName : internalName.substring(slash + 1);
        long hash = 0xcbf29ce484222325L ^ seed;
        for (char ch : shortName.toCharArray()) hash = (hash ^ ch) * 0x100000001b3L;
        return pkg + "C" + Long.toUnsignedString(hash, 36);
    }

    private static Map<String, byte[]> readEntries(Path input) throws IOException {
        Map<String, byte[]> result = new TreeMap<>();
        try (JarFile jar = new JarFile(input.toFile())) {
            Enumeration<JarEntry> enumeration = jar.entries();
            while (enumeration.hasMoreElements()) {
                JarEntry entry = enumeration.nextElement();
                if (entry.isDirectory() || entry.getName().equalsIgnoreCase("META-INF/MANIFEST.MF")) continue;
                try (InputStream stream = jar.getInputStream(entry)) { result.put(entry.getName(), stream.readAllBytes()); }
            }
        }
        return result;
    }

    private static void writeEntries(Path output, Map<String, byte[]> entries) throws IOException {
        try (JarOutputStream jar = new JarOutputStream(Files.newOutputStream(output))) {
            for (var entry : entries.entrySet()) {
                JarEntry item = new JarEntry(entry.getKey());
                item.setTime(0L);
                jar.putNextEntry(item);
                jar.write(entry.getValue());
                jar.closeEntry();
            }
        }
    }

    private static void verify(byte[] bytes) {
        ClassReader reader = new ClassReader(bytes);
        reader.accept(new CheckClassAdapter(new ClassWriter(0), true), ClassReader.EXPAND_FRAMES);
    }

    private static String sha256(Path file) throws IOException {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            try (InputStream in = Files.newInputStream(file)) {
                byte[] buffer = new byte[8192];
                for (int read; (read = in.read(buffer)) != -1;) digest.update(buffer, 0, read);
            }
            return HexFormat.of().formatHex(digest.digest());
        } catch (java.security.NoSuchAlgorithmException e) { throw new AssertionError(e); }
    }
}
