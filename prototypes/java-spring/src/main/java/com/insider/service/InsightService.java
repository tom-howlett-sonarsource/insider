package com.insider.service;

import com.insider.dto.request.InsightCreateRequest;
import com.insider.dto.request.InsightUpdateRequest;
import com.insider.dto.response.InsightListResponse;
import com.insider.dto.response.InsightResponse;
import com.insider.entity.Insight;
import com.insider.exception.ForbiddenException;
import com.insider.exception.ResourceNotFoundException;
import com.insider.repository.InsightRepository;
import com.insider.security.UserPrincipal;
import java.util.List;
import java.util.UUID;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
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

    private final InsightRepository insightRepository;

    public InsightService(InsightRepository insightRepository) {
        this.insightRepository = insightRepository;
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
}
