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
                new BigDecimal("21.05"), new BigDecimal("91.20"), "HIGH", "2025-04")));

        mockMvc.perform(get("/api/v1/health-access").param("limit", "1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].region").value("가평군"))
                .andExpect(jsonPath("$[0].priorityBand").value("HIGH"));
    }

    @Test
    void rejectsOutOfRangeLimit() throws Exception {
        mockMvc.perform(get("/api/v1/health-access").param("limit", "99"))
                .andExpect(status().isBadRequest());
    }
}

