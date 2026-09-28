package dev.reverse.phantom.backend;

import java.net.URI;

public interface VerificationBackend {
    record Decision(boolean accepted, String buildId, String message) {}
    Decision verify(URI endpoint, String sha256, String profile) throws Exception;
}
