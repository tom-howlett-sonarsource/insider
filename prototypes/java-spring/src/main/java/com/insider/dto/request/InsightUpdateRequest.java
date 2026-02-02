package com.insider.dto.request;

import com.insider.entity.Source;
import jakarta.validation.constraints.Size;

/**
 * Request DTO for updating an insight.
 * All fields are optional for partial updates.
 */
public record InsightUpdateRequest(
        @Size(max = 200, message = "Title must be 200 characters or less") String title,
        String description,
        Source source) {}
