package dev.taeyoung.regionalinsight.api;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

/**
 * Full-stack API checks against the real Flyway schema and generated seed (H2 in PostgreSQL mode).
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class InsightApiIntegrationTests {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void overviewSummarisesTheSeededMarts() throws Exception {
        mockMvc.perform(get("/api/v1/overview"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.healthRegions").value(31))
                .andExpect(jsonPath("$.highPriorityRegions").value(7))
                .andExpect(jsonPath("$.activeClinics").value(12140))
                .andExpect(jsonPath("$.housingRegions").value(25))
                .andExpect(jsonPath("$.highestHealthPriority.region").value("연천군"))
                .andExpect(jsonPath("$.hottestHousingMarket.region").value("서초구"));
    }

    @Test
    void healthRankingIsLimitedAndBreaksScoreTiesByRegion() throws Exception {
        mockMvc.perform(get("/api/v1/health-access").param("limit", "31"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(31))
                .andExpect(jsonPath("$[0].region").value("연천군"))
                .andExpect(jsonPath("$[0].latitude").isNumber())
                // 양주시 and 의정부시 share a 58.33 score; order must not depend on row storage.
                .andExpect(jsonPath("$[10].region").value("양주시"))
                .andExpect(jsonPath("$[11].region").value("의정부시"));

        mockMvc.perform(get("/api/v1/health-access").param("limit", "3"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(3));
    }

    @Test
    void housingRankingUsesMarketHeatScore() throws Exception {
        mockMvc.perform(get("/api/v1/housing").param("limit", "25"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(25))
                .andExpect(jsonPath("$[0].region").value("서초구"))
                .andExpect(jsonPath("$[1].region").value("강남구"));
    }

    @Test
    void specialtiesAreReturnedInDiseaseRankOrder() throws Exception {
        mockMvc.perform(get("/api/v1/health-access/연천군/specialties"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(7))
                .andExpect(jsonPath("$[0].diseaseRank").value(1))
                .andExpect(jsonPath("$[0].region").value("연천군"));
    }

    @Test
    void unknownRegionReturnsProblemDetails() throws Exception {
        mockMvc.perform(get("/api/v1/housing/없는구"))
                .andExpect(status().isNotFound())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON))
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.detail").value(containsString("없는구")));

        mockMvc.perform(get("/api/v1/health-access/없는시/specialties"))
                .andExpect(status().isNotFound());
    }

    @Test
    void invalidParametersAreRejectedWithBadRequest() throws Exception {
        mockMvc.perform(get("/api/v1/health-access").param("limit", "abc"))
                .andExpect(status().isBadRequest())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON));
        mockMvc.perform(get("/api/v1/health-access").param("limit", "0"))
                .andExpect(status().isBadRequest());
        mockMvc.perform(get("/api/v1/housing").param("limit", "26"))
                .andExpect(status().isBadRequest());
        mockMvc.perform(get("/api/v1/health-access/" + "가".repeat(41)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void onlyHealthAndInfoActuatorEndpointsArePublic() throws Exception {
        mockMvc.perform(get("/actuator/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"));
        mockMvc.perform(get("/actuator/info")).andExpect(status().isOk());
        mockMvc.perform(get("/actuator/metrics")).andExpect(status().isNotFound());
    }

    @Test
    void staticAssetsAreRevalidatedSoRedeploysArePickedUp() throws Exception {
        mockMvc.perform(get("/app.js"))
                .andExpect(status().isOk())
                .andExpect(header().string("Cache-Control", containsString("no-cache")));
    }
}
