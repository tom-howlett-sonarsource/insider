package com.insider.exception;

/**
 * Exception thrown when user is not authorized to perform an action.
 */
public class ForbiddenException extends RuntimeException {

    public ForbiddenException(String message) {
        super(message);
    }
}
