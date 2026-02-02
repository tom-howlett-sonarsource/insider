package com.insider.controller;

import com.insider.dto.request.InsightCreateRequest;
import com.insider.dto.request.InsightUpdateRequest;
import com.insider.dto.response.InsightListResponse;
import com.insider.dto.response.InsightResponse;
import com.insider.security.UserPrincipal;
import com.insider.service.InsightService;
import jakarta.validation.Valid;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * Controller for insight endpoints.
 */
@RestController
@RequestMapping("/api/v1/insights")
public class InsightController {

    private final InsightService insightService;

    public InsightController(InsightService insightService) {
        this.insightService = insightService;
    }

    /**
     * List all insights with pagination.
     */
    @GetMapping
    public ResponseEntity<InsightListResponse> listInsights(
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(defaultValue = "0") int offset,
            @AuthenticationPrincipal UserPrincipal currentUser) {

        InsightListResponse response = insightService.getAllInsights(limit, offset);
        return ResponseEntity.ok(response);
    }

    /**
     * Create a new insight.
     */
    @PostMapping
    public ResponseEntity<InsightResponse> createInsight(
            @Valid @RequestBody InsightCreateRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {

        InsightResponse response = insightService.createInsight(request, currentUser);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Get an insight by ID.
     */
    @GetMapping("/{id}")
    public ResponseEntity<InsightResponse> getInsight(
            @PathVariable UUID id, @AuthenticationPrincipal UserPrincipal currentUser) {

        InsightResponse response = insightService.getInsightById(id);
        return ResponseEntity.ok(response);
    }

    /**
     * Update an insight.
     */
    @PutMapping("/{id}")
    public ResponseEntity<InsightResponse> updateInsight(
            @PathVariable UUID id,
            @Valid @RequestBody InsightUpdateRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {

        InsightResponse response = insightService.updateInsight(id, request, currentUser);
        return ResponseEntity.ok(response);
    }

    /**
     * Delete an insight.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteInsight(
            @PathVariable UUID id, @AuthenticationPrincipal UserPrincipal currentUser) {

        insightService.deleteInsight(id, currentUser);
        return ResponseEntity.noContent().build();
    }
}
