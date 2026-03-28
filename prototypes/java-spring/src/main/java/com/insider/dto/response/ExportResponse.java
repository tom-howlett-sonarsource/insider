package com.insider.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Response DTO for insight export.
 */
public record ExportResponse(
        int exported,
        @JsonProperty("webhook_notified") boolean webhookNotified) {}
