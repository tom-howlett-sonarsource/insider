package com.insider.service;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withServerError;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.client.RestClientTest;
import org.springframework.test.web.client.MockRestServiceServer;

@RestClientTest(WebhookClientImpl.class)
class WebhookClientImplTest {

    @Autowired
    private WebhookClient webhookClient;

    @Autowired
    private MockRestServiceServer server;

    @Test
    void notifyExport_ReturnsTrue_OnSuccess() {
        server.expect(requestTo("https://hooks.example.com/notify"))
                .andRespond(withSuccess());

        boolean result = webhookClient.notifyExport(5);

        assertTrue(result);
    }

    @Test
    void notifyExport_ReturnsFalse_OnServerError() {
        server.expect(requestTo("https://hooks.example.com/notify"))
                .andRespond(withServerError());

        boolean result = webhookClient.notifyExport(5);

        assertFalse(result);
    }
}
