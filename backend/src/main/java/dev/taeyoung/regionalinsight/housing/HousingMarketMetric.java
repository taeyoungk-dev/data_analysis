package dev.taeyoung.regionalinsight.housing;

import java.math.BigDecimal;

import jakarta.persistence.Entity;
import jakarta.persistence.Column;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "housing_market_metric")
public class HousingMarketMetric {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "region")
    private String region;
    @Column(name = "transaction_count")
    private long transactionCount;
    @Column(name = "median_trade_price_krw")
    private long medianTradePriceKrw;
    @Column(name = "median_price_per_sqm_krw")
    private long medianPricePerSqmKrw;
    @Column(name = "median_area_sqm")
    private BigDecimal medianAreaSqm;
    @Column(name = "price_cagr_pct")
    private BigDecimal priceCagrPct;
    @Column(name = "market_heat_score")
    private BigDecimal marketHeatScore;
    @Column(name = "market_band")
    private String marketBand;
    @Column(name = "period")
    private String period;

    protected HousingMarketMetric() {}

    public Long getId() { return id; }
    public String getRegion() { return region; }
    public long getTransactionCount() { return transactionCount; }
    public long getMedianTradePriceKrw() { return medianTradePriceKrw; }
    public long getMedianPricePerSqmKrw() { return medianPricePerSqmKrw; }
    public BigDecimal getMedianAreaSqm() { return medianAreaSqm; }
    public BigDecimal getPriceCagrPct() { return priceCagrPct; }
    public BigDecimal getMarketHeatScore() { return marketHeatScore; }
    public String getMarketBand() { return marketBand; }
    public String getPeriod() { return period; }
}
