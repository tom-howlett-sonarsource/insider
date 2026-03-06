package com.insider.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

/**
 * Response DTO for insight analytics statistics.
 */
public record AnalyticsResponse(
        int total,
        @JsonProperty("by_source") Map<String, Integer> bySource,
        @JsonProperty("by_author") Map<String, Integer> byAuthor,
        List<WeeklyCount> weekly) {}
