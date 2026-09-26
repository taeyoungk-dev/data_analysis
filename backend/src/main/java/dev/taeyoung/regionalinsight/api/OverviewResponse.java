package dev.taeyoung.regionalinsight.api;

import java.io.Serializable;

public record OverviewResponse(
        long healthRegions,
        long highPriorityRegions,
        long activeClinics,
        long housingRegions,
        HealthAccessResponse highestHealthPriority,
        HousingMarketResponse hottestHousingMarket,
        String generatedFrom) implements Serializable {}
