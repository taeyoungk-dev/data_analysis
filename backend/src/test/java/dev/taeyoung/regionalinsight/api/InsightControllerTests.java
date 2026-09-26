package dev.taeyoung.regionalinsight.api;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.math.BigDecimal;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(InsightController.class)
class InsightControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private InsightService service;

    @Test
    void returnsRankedHealthAccessResults() throws Exception {
        when(service.health(1)).thenReturn(List.of(new HealthAccessResponse(
                "가평군", 62_000, 19_000, 40, new BigDecimal("30.64"),
                new BigDecimal("21.05"), new BigDecimal("91.20"), "HIGH", "2025-04",
                new BigDecimal("37.81"), new BigDecimal("127.49"))));

        mockMvc.perform(get("/api/v1/health-access").param("limit", "1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].region").value("가평군"))
                .andExpect(jsonPath("$[0].priorityBand").value("HIGH"));
    }

    @Test
    void returnsSpecialtyProfileForRegion() throws Exception {
        when(service.healthSpecialties("가평군")).thenReturn(List.of(new HealthSpecialtyResponse(
                "가평군", "내과", 1, 687_781, new BigDecimal("41.751182"), 31,
                new BigDecimal("15.31"), "고령층 다빈도질병 진료과목 참고자료", "기준연도 미기재")));

        mockMvc.perform(get("/api/v1/health-access/가평군/specialties"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].specialty").value("내과"))
                .andExpect(jsonPath("$[0].activeClinics").value(31));
    }

    @Test
    void rejectsOutOfRangeLimit() throws Exception {
        mockMvc.perform(get("/api/v1/health-access").param("limit", "99"))
                .andExpect(status().isBadRequest());
    }
}
