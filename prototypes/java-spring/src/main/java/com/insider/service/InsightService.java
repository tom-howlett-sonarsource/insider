package com.insider.service;

import com.insider.dto.request.InsightCreateRequest;
import com.insider.dto.request.InsightUpdateRequest;
import com.insider.dto.response.AnalyticsResponse;
import com.insider.dto.response.ExportResponse;
import com.insider.dto.response.InsightListResponse;
import com.insider.dto.response.InsightResponse;
import com.insider.dto.response.WeeklyCount;
import com.insider.entity.Insight;
import com.insider.exception.ForbiddenException;
import com.insider.exception.ResourceNotFoundException;
import com.insider.repository.InsightRepository;
import com.insider.security.UserPrincipal;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Service for insight operations.
 */
@Service
@Transactional
public class InsightService {

    private static final String INSIGHT_NOT_FOUND = "Insight not found";
    private static final String NOT_AUTHORIZED = "Not authorized to modify this insight";
    private static final DateTimeFormatter WEEK_FORMATTER =
            DateTimeFormatter.ofPattern("YYYY-ww", Locale.ROOT);

    private final InsightRepository insightRepository;
    private final WebhookClient webhookClient;

    public InsightService(InsightRepository insightRepository, WebhookClient webhookClient) {
        this.insightRepository = insightRepository;
        this.webhookClient = webhookClient;
    }

    /**
     * Get all insights with pagination.
     */
    @Transactional(readOnly = true)
    public InsightListResponse getAllInsights(int limit, int offset) {
        int page = offset / limit;
        PageRequest pageRequest = PageRequest.of(page, limit);

        Page<Insight> insightPage = insightRepository.findAllByOrderByCreatedAtDesc(pageRequest);

        List<InsightResponse> items =
                insightPage.getContent().stream().map(InsightResponse::fromEntity).toList();

        return new InsightListResponse(items, insightPage.getTotalElements(), limit, offset);
    }

    /**
     * Get insight by ID.
     *
     * @throws ResourceNotFoundException if insight not found
     */
    @Transactional(readOnly = true)
    public InsightResponse getInsightById(UUID id) {
        Insight insight =
                insightRepository
                        .findById(id)
                        .orElseThrow(() -> new ResourceNotFoundException(INSIGHT_NOT_FOUND));

        return InsightResponse.fromEntity(insight);
    }

    /**
     * Create a new insight.
     */
    public InsightResponse createInsight(InsightCreateRequest request, UserPrincipal currentUser) {
        Insight insight =
                new Insight(currentUser.getId(), request.title(), request.description(), request.source());

        Insight saved = insightRepository.save(insight);
        return InsightResponse.fromEntity(saved);
    }

    /**
     * Update an existing insight.
     *
     * @throws ResourceNotFoundException if insight not found
     * @throws ForbiddenException if user is not the author
     */
    public InsightResponse updateInsight(
            UUID id, InsightUpdateRequest request, UserPrincipal currentUser) {
        Insight insight =
                insightRepository
                        .findById(id)
                        .orElseThrow(() -> new ResourceNotFoundException(INSIGHT_NOT_FOUND));

        if (!insight.getAuthorId().equals(currentUser.getId())) {
            throw new ForbiddenException(NOT_AUTHORIZED);
        }

        if (request.title() != null) {
            if (request.title().isBlank()) {
                throw new IllegalArgumentException("Title cannot be empty");
            }
            insight.setTitle(request.title());
        }
        if (request.description() != null) {
            insight.setDescription(request.description());
        }
        if (request.source() != null) {
            insight.setSource(request.source());
        }

        Insight updated = insightRepository.save(insight);
        return InsightResponse.fromEntity(updated);
    }

    /**
     * Delete an insight.
     *
     * @throws ResourceNotFoundException if insight not found
     * @throws ForbiddenException if user is not the author
     */
    public void deleteInsight(UUID id, UserPrincipal currentUser) {
        Insight insight =
                insightRepository
                        .findById(id)
                        .orElseThrow(() -> new ResourceNotFoundException(INSIGHT_NOT_FOUND));

        if (!insight.getAuthorId().equals(currentUser.getId())) {
            throw new ForbiddenException(NOT_AUTHORIZED);
        }

        insightRepository.delete(insight);
    }

    /**
     * Return aggregated analytics statistics for all insights.
     */
    @Transactional(readOnly = true)
    public AnalyticsResponse getAnalytics() {
        List<Insight> all = insightRepository.findAll();

        Map<String, Integer> bySource = new LinkedHashMap<>();
        Map<String, Integer> byAuthor = new LinkedHashMap<>();
        for (Insight insight : all) {
            String sourceKey = insight.getSource() != null
                    ? insight.getSource().getValue() : "unspecified";
            bySource.merge(sourceKey, 1, Integer::sum);
            byAuthor.merge(insight.getAuthorId().toString(), 1, Integer::sum);
        }

        LocalDateTime cutoff = LocalDateTime.now(ZoneOffset.UTC).minusWeeks(8);
        Map<String, Integer> weeklyMap = new TreeMap<>();
        for (Insight insight : all) {
            if (insight.getCreatedAt() != null && insight.getCreatedAt().isAfter(cutoff)) {
                String week = insight.getCreatedAt().format(WEEK_FORMATTER);
                weeklyMap.merge(week, 1, Integer::sum);
            }
        }

        List<WeeklyCount> weekly = weeklyMap.entrySet().stream()
                .map(e -> new WeeklyCount(e.getKey(), e.getValue()))
                .toList();

        return new AnalyticsResponse(all.size(), bySource, byAuthor, weekly);
    }

    /**
     * Export all insights to CSV format and notify the analytics webhook.
     */
    public ExportResponse exportInsights() {
        List<Insight> insights = insightRepository.findAll(
                Sort.by(Sort.Direction.DESC, "createdAt"));
        boolean notified = webhookClient.notifyExport(insights.size());
        return new ExportResponse(insights.size(), notified);
    }
}
