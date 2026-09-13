package dev.taeyoung.regionalinsight.api;

import java.math.BigDecimal;
import java.io.Serializable;

import dev.taeyoung.regionalinsight.health.HealthAccessMetric;

public record HealthAccessResponse(
        String region,
        long population,
        long elderlyPopulation,
        long activeClinics,
        BigDecimal elderlySharePct,
        BigDecimal clinicsPer10kElderly,
        BigDecimal priorityScore,
        String priorityBand,
        String period) implements Serializable {

    static HealthAccessResponse from(HealthAccessMetric metric) {
        return new HealthAccessResponse(
                metric.getRegion(),
                metric.getPopulation(),
                metric.getElderlyPopulation(),
                metric.getActiveClinics(),
                metric.getElderlySharePct(),
                metric.getClinicsPer10kElderly(),
                metric.getPriorityScore(),
                metric.getPriorityBand(),
                metric.getPeriod());
    }
}
