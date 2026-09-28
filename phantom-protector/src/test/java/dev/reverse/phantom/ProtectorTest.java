package dev.reverse.phantom;

import dev.reverse.phantom.backend.HttpVerificationBackend;
import dev.reverse.phantom.backend.MockVerificationServer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Opcodes;

import java.net.URI;
import java.net.URLClassLoader;
import java.nio.file.*;
import java.util.jar.*;

import static org.junit.jupiter.api.Assertions.*;

class ProtectorTest {
    @TempDir Path temp;

    @Test void transformsAndRunsFixtureJar() throws Exception {
        Path input = temp.resolve("fixture.jar");
        Path output = temp.resolve("protected.jar");
        byte[] fixture = fixtureClass();
        try (JarOutputStream jar = new JarOutputStream(Files.newOutputStream(input))) {
            jar.putNextEntry(new JarEntry("com/example/client/Hello.class")); jar.write(fixture); jar.closeEntry();
            jar.putNextEntry(new JarEntry("assets/test.txt")); jar.write("kept".getBytes()); jar.closeEntry();
        }
        JarProtector.Result result = new JarProtector().protect(new ProtectionConfig(input, output, Profile.MEDIUM, "com/example/client", null, 7));
        assertEquals(1, result.classesChanged());
        assertEquals(1, result.stringsEncrypted());
        assertTrue(result.classMapping().containsKey("com/example/client/Hello"));
        try (JarFile jar = new JarFile(output.toFile())) {
            assertNotNull(jar.getEntry(result.classMapping().get("com/example/client/Hello") + ".class"));
            assertEquals("kept", new String(jar.getInputStream(jar.getEntry("assets/test.txt")).readAllBytes()));
            try (URLClassLoader loader = new URLClassLoader(new java.net.URL[]{output.toUri().toURL()}, getClass().getClassLoader())) {
                Class<?> type = loader.loadClass(result.classMapping().get("com/example/client/Hello").replace('/', '.'));
                assertEquals("fixture-secret", type.getMethod("value").invoke(null));
            }
        }
    }

    @Test void backendFixtureAcceptsBuildContract() throws Exception {
        try (MockVerificationServer server = new MockVerificationServer(0)) {
            var decision = new HttpVerificationBackend().verify(URI.create("http://127.0.0.1:" + server.port()), "a".repeat(64), "medium");
            assertTrue(decision.accepted());
            assertTrue(decision.buildId().startsWith("fixture-"));
        }
    }

    private static byte[] fixtureClass() {
        ClassWriter writer = new ClassWriter(0);
        writer.visit(Opcodes.V21, Opcodes.ACC_PUBLIC, "com/example/client/Hello", null, "java/lang/Object", null);
        var method = writer.visitMethod(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC, "value", "()Ljava/lang/String;", null, null);
        method.visitCode(); method.visitLdcInsn("fixture-secret"); method.visitInsn(Opcodes.ARETURN); method.visitMaxs(1, 0); method.visitEnd();
        writer.visitEnd();
        return writer.toByteArray();
    }
}
