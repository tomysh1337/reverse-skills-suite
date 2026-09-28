package dev.reverse.phantom.backend;

import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;

public final class MockVerificationServer implements AutoCloseable {
    private final HttpServer server;

    public MockVerificationServer(int port) throws IOException {
        server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);
        server.createContext("/v1/status", exchange -> respond(exchange, 200, "{\"available\":true,\"protocol\":1}"));
        server.createContext("/v1/builds", exchange -> {
            if (!exchange.getRequestMethod().equalsIgnoreCase("POST")) {
                respond(exchange, 405, "{\"accepted\":false,\"message\":\"POST required\"}");
                return;
            }
            byte[] body = exchange.getRequestBody().readAllBytes();
            if (!new String(body, StandardCharsets.UTF_8).matches("(?s).*\\\"sha256\\\":\\\"[0-9a-f]{64}\\\".*")) {
                respond(exchange, 400, "{\"accepted\":false,\"message\":\"sha256 required\"}");
                return;
            }
            respond(exchange, 200, "{\"accepted\":true,\"buildId\":\"fixture-" + Long.toUnsignedString(new SecureRandom().nextLong(), 36) + "\"}");
        });
        server.start();
    }

    public int port() { return server.getAddress().getPort(); }
    @Override public void close() { server.stop(0); }

    private static void respond(com.sun.net.httpserver.HttpExchange exchange, int code, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(code, bytes.length);
        try (var out = exchange.getResponseBody()) { out.write(bytes); }
    }
}
