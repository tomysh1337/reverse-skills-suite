package dev.reverse.phantom;

public enum Profile {
    LIGHT, MEDIUM, HEAVY;

    public static Profile parse(String value) {
        return Profile.valueOf(value.toUpperCase(java.util.Locale.ROOT));
    }

    public boolean renameClasses() {
        return this != LIGHT;
    }

    public boolean strictBackend() {
        return this == HEAVY;
    }
}
