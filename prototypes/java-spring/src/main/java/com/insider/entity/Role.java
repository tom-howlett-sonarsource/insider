package com.insider.entity;

import com.fasterxml.jackson.annotation.JsonValue;

/**
 * User roles in the system.
 */
public enum Role {
    ADVOCATE("advocate"),
    PRODUCT_MANAGER("product_manager");

    private final String value;

    Role(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    public static Role fromValue(String value) {
        for (Role role : Role.values()) {
            if (role.value.equals(value)) {
                return role;
            }
        }
        throw new IllegalArgumentException("Unknown role: " + value);
    }
}
