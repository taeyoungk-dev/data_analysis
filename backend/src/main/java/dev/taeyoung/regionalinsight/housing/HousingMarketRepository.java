package dev.taeyoung.regionalinsight.housing;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

public interface HousingMarketRepository extends JpaRepository<HousingMarketMetric, Long> {
    Optional<HousingMarketMetric> findByRegion(String region);
}

