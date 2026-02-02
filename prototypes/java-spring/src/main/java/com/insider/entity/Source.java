package com.insider.entity;

import com.fasterxml.jackson.annotation.JsonValue;

/**
 * Source of an insight.
 */
public enum Source {
    COMMUNITY_FORUM("community_forum"),
    CONFERENCE("conference"),
    SOCIAL_MEDIA("social_media"),
    MEETUP("meetup"),
    OTHER("other");

    private final String value;

    Source(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    public static Source fromValue(String value) {
        if (value == null) {
            return null;
        }
        for (Source source : Source.values()) {
            if (source.value.equals(value)) {
                return source;
            }
        }
        throw new IllegalArgumentException("Unknown source: " + value);
    }
}
