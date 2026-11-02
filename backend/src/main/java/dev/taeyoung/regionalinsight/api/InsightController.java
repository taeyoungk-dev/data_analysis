package dev.taeyoung.regionalinsight.api;

import java.util.List;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Size;

import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/v1")
public class InsightController {

    /** Matches the VARCHAR(40) region columns; longer values can never match a row. */
    static final int MAX_REGION_LENGTH = 40;

    private final InsightService service;

    public InsightController(InsightService service) {
        this.service = service;
    }

    @GetMapping("/overview")
    public OverviewResponse overview() {
        return service.overview();
    }

    @GetMapping("/health-access")
    public List<HealthAccessResponse> healthAccess(
            @RequestParam(defaultValue = "10") @Min(1) @Max(31) int limit) {
        return service.health(limit);
    }

    @GetMapping("/health-access/{region}")
    public HealthAccessResponse healthAccessRegion(
            @PathVariable @Size(max = MAX_REGION_LENGTH) String region) {
        return service.healthRegion(region);
    }

    @GetMapping("/health-access/{region}/specialties")
    public List<HealthSpecialtyResponse> healthAccessSpecialties(
            @PathVariable @Size(max = MAX_REGION_LENGTH) String region) {
        return service.healthSpecialties(region);
    }

    @GetMapping("/housing")
    public List<HousingMarketResponse> housing(
            @RequestParam(defaultValue = "10") @Min(1) @Max(25) int limit) {
        return service.housing(limit);
    }

    @GetMapping("/housing/{region}")
    public HousingMarketResponse housingRegion(
            @PathVariable @Size(max = MAX_REGION_LENGTH) String region) {
        return service.housingRegion(region);
    }
}
