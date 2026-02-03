package com.insider.service;

import com.insider.dto.response.UserResponse;
import com.insider.entity.User;
import com.insider.exception.ResourceNotFoundException;
import com.insider.repository.UserRepository;
import java.util.UUID;
import org.springframework.stereotype.Service;

/**
 * Service for user operations.
 */
@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    /**
     * Get user by ID.
     *
     * @throws ResourceNotFoundException if user not found
     */
    public User getUserById(UUID id) {
        return userRepository
                .findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));
    }

    /**
     * Get user response by ID.
     */
    public UserResponse getUserResponseById(UUID id) {
        return UserResponse.fromEntity(getUserById(id));
    }
}
