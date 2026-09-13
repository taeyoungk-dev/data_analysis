package dev.taeyoung.regionalinsight.health;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

public interface HealthAccessRepository extends JpaRepository<HealthAccessMetric, Long> {
    Optional<HealthAccessMetric> findByRegion(String region);
}

