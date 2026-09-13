package dev.taeyoung.regionalinsight.health;

import java.math.BigDecimal;

import jakarta.persistence.Entity;
import jakarta.persistence.Column;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "health_access_metric")
public class HealthAccessMetric {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "region")
    private String region;
    @Column(name = "population")
    private long population;
    @Column(name = "elderly_population")
    private long elderlyPopulation;
    @Column(name = "active_clinics")
    private long activeClinics;
    @Column(name = "elderly_share_pct")
    private BigDecimal elderlySharePct;
    @Column(name = "clinics_per_10k_elderly")
    private BigDecimal clinicsPer10kElderly;
    @Column(name = "priority_score")
    private BigDecimal priorityScore;
    @Column(name = "priority_band")
    private String priorityBand;
    @Column(name = "period")
    private String period;

    protected HealthAccessMetric() {}

    public Long getId() { return id; }
    public String getRegion() { return region; }
    public long getPopulation() { return population; }
    public long getElderlyPopulation() { return elderlyPopulation; }
    public long getActiveClinics() { return activeClinics; }
    public BigDecimal getElderlySharePct() { return elderlySharePct; }
    public BigDecimal getClinicsPer10kElderly() { return clinicsPer10kElderly; }
    public BigDecimal getPriorityScore() { return priorityScore; }
    public String getPriorityBand() { return priorityBand; }
    public String getPeriod() { return period; }
}
