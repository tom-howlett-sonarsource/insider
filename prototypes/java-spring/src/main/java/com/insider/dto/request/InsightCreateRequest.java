package com.insider.dto.request;

import com.insider.entity.Source;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Request DTO for creating an insight.
 */
public record InsightCreateRequest(
        @NotBlank(message = "Title cannot be empty")
                @Size(max = 200, message = "Title must be 200 characters or less")
                String title,
        @NotBlank(message = "Description cannot be empty") String description,
        Source source) {}
