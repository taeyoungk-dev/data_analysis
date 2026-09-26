package dev.taeyoung.regionalinsight.api;

import java.io.Serializable;
import java.math.BigDecimal;

import dev.taeyoung.regionalinsight.health.HealthSpecialtyMetric;

public record HealthSpecialtyResponse(
        String region,
        String specialty,
        int diseaseRank,
        long diseasePatientCount,
        BigDecimal diseaseSharePct,
        long activeClinics,
        BigDecimal clinicsPer10kElderly,
        String sourceScope,
        String sourcePeriod) implements Serializable {

    static HealthSpecialtyResponse from(HealthSpecialtyMetric metric) {
        return new HealthSpecialtyResponse(
                metric.getRegion(),
                metric.getSpecialty(),
                metric.getDiseaseRank(),
                metric.getDiseasePatientCount(),
                metric.getDiseaseSharePct(),
                metric.getActiveClinics(),
                metric.getClinicsPer10kElderly(),
                metric.getSourceScope(),
                metric.getSourcePeriod());
    }
}
