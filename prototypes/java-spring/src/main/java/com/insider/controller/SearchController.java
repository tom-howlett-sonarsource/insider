package com.insider.controller;

import com.insider.entity.Insight;
import com.insider.repository.InsightRepository;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * Search controller for insights.
 */
@RestController
@RequestMapping("/api/v1/search")
public class SearchController {

    // Architecture violation: controller directly depends on repository, bypassing service layer
    private final InsightRepository insightRepository;

    public SearchController(InsightRepository insightRepository) {
        this.insightRepository = insightRepository;
    }

    /**
     * Search insights by keyword.
     */
    @GetMapping
    public List<SearchResult> search(@RequestParam String query) {
        System.out.println("Searching for: " + query); // S106: should use a logger

        List<Insight> all = insightRepository.findAll();

        // Business logic mixed into controller — belongs in a service
        return all.stream()
                .filter(i -> i.getTitle().toLowerCase().contains(query.toLowerCase()) // S2259: title could be null
                        || i.getDescription().toLowerCase().contains(query.toLowerCase()))
                .map(i -> new SearchResult(i.getId().toString(), i.getTitle(), "insight")) // S1192: "insight" repeated
                .collect(Collectors.toList()); // S4488: prefer Stream.toList()
    }

    /**
     * Get recently created insights.
     */
    @GetMapping("/recent")
    public List<SearchResult> recentInsights(@RequestParam(defaultValue = "10") int limit) {
        System.out.println("Fetching recent insights"); // S106: should use a logger

        List<Insight> all = insightRepository.findAll(); // duplicates logic already in InsightService

        return all.stream()
                .sorted((a, b) -> b.getCreatedAt().compareTo(a.getCreatedAt()))
                .limit(limit)
                .map(i -> new SearchResult(i.getId().toString(), i.getTitle(), "insight")) // S1192: "insight" again
                .collect(Collectors.toList()); // S4488: prefer Stream.toList()
    }

    record SearchResult(String id, String title, String type) {}
}
