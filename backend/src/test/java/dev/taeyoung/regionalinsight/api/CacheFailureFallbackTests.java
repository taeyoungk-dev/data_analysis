package dev.taeyoung.regionalinsight.api;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.cache.Cache;
import org.springframework.cache.CacheManager;
import org.springframework.cache.concurrent.ConcurrentMapCache;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;

/**
 * Simulates an unavailable cache (for example Redis being down): every cache read and write
 * throws. Queries must still be answered from the database instead of failing with HTTP 500.
 */
@SpringBootTest
@ActiveProfiles("test")
@Import(CacheFailureFallbackTests.BrokenCacheConfiguration.class)
class CacheFailureFallbackTests {

    @Autowired
    private InsightService service;

    @Test
    void readsFromTheDatabaseWhenTheCacheIsUnavailable() {
        assertThat(service.health(3)).hasSize(3);
        assertThat(service.housingRegion("서초구").region()).isEqualTo("서초구");
        assertThat(service.overview().healthRegions()).isEqualTo(31);
    }

    @TestConfiguration
    static class BrokenCacheConfiguration {

        @Bean
        CacheManager cacheManager() {
            return new ConcurrentMapCacheManager() {
                @Override
                protected Cache createConcurrentMapCache(String name) {
                    return new BrokenCache(name);
                }
            };
        }
    }

    static class BrokenCache extends ConcurrentMapCache {

        BrokenCache(String name) {
            super(name);
        }

        @Override
        public ValueWrapper get(Object key) {
            throw new IllegalStateException("cache unavailable");
        }

        @Override
        public void put(Object key, Object value) {
            throw new IllegalStateException("cache unavailable");
        }
    }
}
