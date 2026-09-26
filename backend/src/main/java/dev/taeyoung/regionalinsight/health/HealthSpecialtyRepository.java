package dev.taeyoung.regionalinsight.health;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

public interface HealthSpecialtyRepository extends JpaRepository<HealthSpecialtyMetric, Long> {
    List<HealthSpecialtyMetric> findByRegionOrderByDiseaseRankAsc(String region);
}
