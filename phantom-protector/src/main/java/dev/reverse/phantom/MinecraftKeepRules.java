package dev.reverse.phantom;

import org.objectweb.asm.ClassReader;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.ClassNode;

import java.util.Set;

public final class MinecraftKeepRules {
    private static final Set<String> RESERVED_PREFIXES = Set.of(
            "net/minecraft/", "net/fabricmc/", "net/minecraftforge/", "cpw/mods/",
            "org/spongepowered/", "org/objectweb/asm/");

    public boolean keep(String entryName, byte[] bytes) {
        if (!entryName.endsWith(".class")) return true;
        String name = entryName.substring(0, entryName.length() - 6);
        if (name.equals("module-info") || name.endsWith("/module-info") || name.equals("package-info") || name.endsWith("/package-info")) return true;
        if (RESERVED_PREFIXES.stream().anyMatch(name::startsWith)) return true;
        ClassNode node = new ClassNode();
        new ClassReader(bytes).accept(node, ClassReader.SKIP_CODE | ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
        if (node.visibleAnnotations != null && !node.visibleAnnotations.isEmpty()) return true;
        if (node.invisibleAnnotations != null && !node.invisibleAnnotations.isEmpty()) return true;
        return (node.access & (Opcodes.ACC_ANNOTATION | Opcodes.ACC_ENUM | Opcodes.ACC_MODULE)) != 0;
    }
}
