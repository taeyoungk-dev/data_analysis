package dev.taeyoung.regionalinsight.api;

import java.io.Serializable;

public record OverviewResponse(
        long healthRegions,
        long housingRegions,
        HealthAccessResponse highestHealthPriority,
        HousingMarketResponse hottestHousingMarket,
        String generatedFrom) implements Serializable {}
