package com.insider.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.insider.entity.Insight;
import com.insider.entity.Source;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Response DTO for insight information.
 */
public record InsightResponse(
        UUID id,
        String title,
        String description,
        Source source,
        @JsonProperty("created_at") LocalDateTime createdAt,
        @JsonProperty("updated_at") LocalDateTime updatedAt) {

    public static InsightResponse fromEntity(Insight insight) {
        return new InsightResponse(
                insight.getId(),
                insight.getTitle(),
                insight.getDescription(),
                insight.getSource(),
                insight.getCreatedAt(),
                insight.getUpdatedAt());
    }
}
