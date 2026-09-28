package dev.reverse.phantom.backend;

import java.net.URI;
import java.net.http.*;
import java.time.Duration;

public final class HttpVerificationBackend implements VerificationBackend {
    private final HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build();

    @Override public Decision verify(URI endpoint, String sha256, String profile) throws Exception {
        try {
            HttpRequest status = HttpRequest.newBuilder(endpoint.resolve("/v1/status")).timeout(Duration.ofSeconds(5)).GET().build();
            HttpResponse<String> statusResponse = client.send(status, HttpResponse.BodyHandlers.ofString());
            if (statusResponse.statusCode() != 200 || !statusResponse.body().contains("\"available\":true"))
                return new Decision(false, "", "verification backend is unavailable");
            String json = "{\"sha256\":\"" + sha256 + "\",\"profile\":\"" + profile.toLowerCase() + "\"}";
            HttpRequest request = HttpRequest.newBuilder(endpoint.resolve("/v1/builds")).timeout(Duration.ofSeconds(5))
                    .header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(json)).build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200) return new Decision(false, "", "backend rejected build registration: HTTP " + response.statusCode());
            boolean accepted = response.body().contains("\"accepted\":true");
            String buildId = field(response.body(), "buildId");
            return new Decision(accepted, buildId, accepted ? "accepted" : "rejected");
        } catch (java.io.IOException | InterruptedException error) {
            if (error instanceof InterruptedException) Thread.currentThread().interrupt();
            return new Decision(false, "", "verification backend connection failed: " + error.getClass().getSimpleName());
        }
    }

    private static String field(String json, String name) {
        String marker = "\"" + name + "\":\"";
        int start = json.indexOf(marker);
        if (start < 0) return "";
        start += marker.length();
        int end = json.indexOf('"', start);
        return end < 0 ? "" : json.substring(start, end);
    }
}
