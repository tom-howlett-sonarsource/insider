package com.insider.repository;

import com.insider.entity.Insight;
import java.util.UUID;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * Repository for Insight entity operations.
 */
@Repository
public interface InsightRepository extends JpaRepository<Insight, UUID> {

    Page<Insight> findAllByOrderByCreatedAtDesc(Pageable pageable);
}
