package com.insider.config;

import com.insider.entity.Role;
import com.insider.entity.User;
import com.insider.repository.UserRepository;
import java.util.UUID;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

/**
 * Configuration for seeding initial data on application startup.
 */
@Configuration
public class DataInitializer {

    private static final String DEFAULT_PASSWORD = "password123";

    @Bean
    public ApplicationRunner initializeData(
            UserRepository userRepository, PasswordEncoder passwordEncoder) {
        return args -> {
            if (userRepository.count() == 0) {
                String hashedPassword = passwordEncoder.encode(DEFAULT_PASSWORD);

                User advocate =
                        new User(
                                UUID.randomUUID(),
                                "advocate@example.com",
                                "Test Advocate",
                                hashedPassword,
                                Role.ADVOCATE);

                User productManager =
                        new User(
                                UUID.randomUUID(),
                                "pm@example.com",
                                "Test PM",
                                hashedPassword,
                                Role.PRODUCT_MANAGER);

                userRepository.save(advocate);
                userRepository.save(productManager);
            }
        };
    }
}
