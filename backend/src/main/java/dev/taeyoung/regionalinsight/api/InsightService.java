package dev.taeyoung.regionalinsight.api;

import java.util.List;

import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import dev.taeyoung.regionalinsight.health.HealthAccessRepository;
import dev.taeyoung.regionalinsight.housing.HousingMarketRepository;

@Service
public class InsightService {

    private final HealthAccessRepository healthRepository;
    private final HousingMarketRepository housingRepository;

    public InsightService(
            HealthAccessRepository healthRepository, HousingMarketRepository housingRepository) {
        this.healthRepository = healthRepository;
        this.housingRepository = housingRepository;
    }

    @Cacheable("overview")
    public OverviewResponse overview() {
        var health = health(1);
        var housing = housing(1);
        return new OverviewResponse(
                healthRepository.count(),
                housingRepository.count(),
                health.isEmpty() ? null : health.getFirst(),
                housing.isEmpty() ? null : housing.getFirst(),
                "Korean public data, 2020-2025");
    }

    @Cacheable(value = "health", key = "#limit")
    public List<HealthAccessResponse> health(int limit) {
        return healthRepository.findAll(Sort.by(Sort.Direction.DESC, "priorityScore")).stream()
                .limit(limit)
                .map(HealthAccessResponse::from)
                .toList();
    }

    @Cacheable(value = "housing", key = "#limit")
    public List<HousingMarketResponse> housing(int limit) {
        return housingRepository.findAll(Sort.by(Sort.Direction.DESC, "marketHeatScore")).stream()
                .limit(limit)
                .map(HousingMarketResponse::from)
                .toList();
    }

    @Cacheable(value = "health-region", key = "#region")
    public HealthAccessResponse healthRegion(String region) {
        return healthRepository
                .findByRegion(region)
                .map(HealthAccessResponse::from)
                .orElseThrow(() -> notFound("health-access", region));
    }

    @Cacheable(value = "housing-region", key = "#region")
    public HousingMarketResponse housingRegion(String region) {
        return housingRepository
                .findByRegion(region)
                .map(HousingMarketResponse::from)
                .orElseThrow(() -> notFound("housing", region));
    }

    private ResponseStatusException notFound(String domain, String region) {
        return new ResponseStatusException(
                HttpStatus.NOT_FOUND, "No " + domain + " metric found for region: " + region);
    }
}

