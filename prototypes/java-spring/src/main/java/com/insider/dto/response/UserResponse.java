package com.insider.dto.response;

import com.insider.entity.User;

/**
 * Response DTO for user information.
 */
public record UserResponse(String id, String email, String name, String role) {

    public static UserResponse fromEntity(User user) {
        return new UserResponse(
                user.getId().toString(), user.getEmail(), user.getName(), user.getRole().getValue());
    }
}
