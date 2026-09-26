package dev.taeyoung.regionalinsight.health;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface HealthAccessRepository extends JpaRepository<HealthAccessMetric, Long> {
    Optional<HealthAccessMetric> findByRegion(String region);

    long countByPriorityBand(String priorityBand);

    @Query("select coalesce(sum(metric.activeClinics), 0) from HealthAccessMetric metric")
    long sumActiveClinics();
}
