package com.insider.service;

import java.util.Map;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

/**
 * RestClient-backed implementation of the analytics webhook client.
 */
@Service
public class WebhookClientImpl implements WebhookClient {

    private static final String WEBHOOK_URL = "https://hooks.example.com/notify";

    private final RestClient restClient;

    public WebhookClientImpl(RestClient.Builder restClientBuilder) {
        this.restClient = restClientBuilder.build();
    }

    @Override
    public boolean notifyExport(int count) {
        try {
            restClient
                    .post()
                    .uri(WEBHOOK_URL)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of("event", "export_completed", "count", count))
                    .retrieve()
                    .toBodilessEntity();
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
