package dev.taeyoung.regionalinsight.api;

import jakarta.validation.ConstraintViolationException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

/**
 * Returns RFC 9457 Problem Details for every API error.
 *
 * <p>The base class maps Spring MVC exceptions (404 for unknown regions via
 * {@code ResponseStatusException}, 400 for type mismatches such as {@code limit=abc}, 405, ...)
 * with their correct status and title. Anything unexpected becomes a generic 500 whose body
 * never contains internal exception messages.
 */
@RestControllerAdvice
public class ApiExceptionHandler extends ResponseEntityExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(ApiExceptionHandler.class);

    @ExceptionHandler(ConstraintViolationException.class)
    ProblemDetail handleConstraintViolation(ConstraintViolationException exception) {
        var problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.BAD_REQUEST, "Request parameter validation failed");
        problem.setTitle("Invalid request");
        return problem;
    }

    @ExceptionHandler(Exception.class)
    ProblemDetail handleUnexpected(Exception exception) {
        log.error("Unhandled API error", exception);
        var problem = ProblemDetail.forStatusAndDetail(
                HttpStatus.INTERNAL_SERVER_ERROR, "An unexpected error occurred");
        problem.setTitle("Internal server error");
        return problem;
    }
}
