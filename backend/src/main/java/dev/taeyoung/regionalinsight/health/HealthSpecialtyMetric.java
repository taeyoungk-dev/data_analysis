package dev.taeyoung.regionalinsight.health;

import java.math.BigDecimal;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "health_specialty_metric")
public class HealthSpecialtyMetric {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "region")
    private String region;
    @Column(name = "specialty")
    private String specialty;
    @Column(name = "disease_rank")
    private int diseaseRank;
    @Column(name = "disease_patient_count")
    private long diseasePatientCount;
    @Column(name = "disease_share_pct")
    private BigDecimal diseaseSharePct;
    @Column(name = "active_clinics")
    private long activeClinics;
    @Column(name = "clinics_per_10k_elderly")
    private BigDecimal clinicsPer10kElderly;
    @Column(name = "source_scope")
    private String sourceScope;
    @Column(name = "source_period")
    private String sourcePeriod;

    protected HealthSpecialtyMetric() {}

    public Long getId() { return id; }
    public String getRegion() { return region; }
    public String getSpecialty() { return specialty; }
    public int getDiseaseRank() { return diseaseRank; }
    public long getDiseasePatientCount() { return diseasePatientCount; }
    public BigDecimal getDiseaseSharePct() { return diseaseSharePct; }
    public long getActiveClinics() { return activeClinics; }
    public BigDecimal getClinicsPer10kElderly() { return clinicsPer10kElderly; }
    public String getSourceScope() { return sourceScope; }
    public String getSourcePeriod() { return sourcePeriod; }
}
