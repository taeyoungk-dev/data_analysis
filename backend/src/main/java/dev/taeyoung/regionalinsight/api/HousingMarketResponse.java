package dev.taeyoung.regionalinsight.api;

import java.math.BigDecimal;
import java.io.Serializable;

import dev.taeyoung.regionalinsight.housing.HousingMarketMetric;

public record HousingMarketResponse(
        String region,
        long transactionCount,
        long medianTradePriceKrw,
        long medianPricePerSqmKrw,
        BigDecimal medianAreaSqm,
        BigDecimal priceCagrPct,
        BigDecimal marketHeatScore,
        String marketBand,
        String period) implements Serializable {

    static HousingMarketResponse from(HousingMarketMetric metric) {
        return new HousingMarketResponse(
                metric.getRegion(),
                metric.getTransactionCount(),
                metric.getMedianTradePriceKrw(),
                metric.getMedianPricePerSqmKrw(),
                metric.getMedianAreaSqm(),
                metric.getPriceCagrPct(),
                metric.getMarketHeatScore(),
                metric.getMarketBand(),
                metric.getPeriod());
    }
}
