package com.insider.controller;

import com.insider.dto.response.UserResponse;
import com.insider.security.UserPrincipal;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Controller for user endpoints.
 */
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    /**
     * Get current authenticated user information.
     */
    @GetMapping("/me")
    public ResponseEntity<UserResponse> getCurrentUser(
            @AuthenticationPrincipal UserPrincipal currentUser) {
        UserResponse response =
                new UserResponse(
                        currentUser.getId().toString(),
                        currentUser.getEmail(),
                        currentUser.getName(),
                        currentUser.getRole());

        return ResponseEntity.ok(response);
    }
}
