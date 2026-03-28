package com.insider.service;

/**
 * Client for sending webhook notifications.
 */
public interface WebhookClient {

    /**
     * Notify the analytics webhook that an export completed.
     *
     * @param count number of insights exported
     * @return true if the webhook acknowledged successfully
     */
    boolean notifyExport(int count);
}
