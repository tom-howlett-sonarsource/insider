package com.insider.dto.response;

import java.util.List;

/**
 * Response DTO for paginated list of insights.
 */
public record InsightListResponse(List<InsightResponse> items, long total, int limit, int offset) {}
