---
name: validation
description: Bean Validation (Jakarta Validation 3.x) patterns for Spring Boot 4.x — @Validated on controller interfaces, @Valid on method arguments, constraint annotations on record/class fields, custom constraint validators, and how validation errors map to ApiError responses. Load this BEFORE writing or reviewing any controller interface, request model, or custom validator.
---

# Bean Validation — Spring Boot 4.x

## Setup

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

This pulls in `jakarta.validation-api` and Hibernate Validator (the reference implementation).

## Controller Interface

```java
@Validated                      // triggers method-level constraint processing
@Tag(name = "Orders")
@DefaultOpenApiErrorResponses
public interface OrderApi {

    @PostMapping(value = "/api/v1/orders", consumes = APPLICATION_JSON_VALUE)
    ResponseEntity<OrderResponse> createOrder(
        @RequestBody @Valid OrderRequest request);   // @Valid triggers cascade into request

    @GetMapping("/api/v1/orders/{orderId}")
    OrderResponse getOrder(
        @PathVariable("orderId") @NotBlank String orderId);

    @GetMapping("/api/v1/orders")
    List<OrderResponse> listOrders(
        @RequestParam("status")
        @ValidValues(allowedValues = {"PENDING", "CONFIRMED", "CANCELLED"})
        @NotEmpty Set<String> statuses);
}
```

- `@Validated` on the **interface** (not the `@RestController` impl) — Spring's AOP proxy
  applies validation to the interface.
- `@Valid` on the `@RequestBody` parameter cascades Bean Validation into the request object.
- Inline constraints (`@NotBlank`, `@NotEmpty`, custom) on path/query params are processed
  by the method-level validator when `@Validated` is present.

## Standard Constraint Annotations

Apply to record components or class fields — never to getters unless using class-level mode.

```java
public record BookingRequest(

    @NotBlank
    @Size(max = 64)
    @Schema(description = "Offer ID to convert to an Order.")
    String offerId,

    @NotNull
    @Valid                          // cascade into PassengerRequest
    List<@NotNull PassengerRequest> passengers,

    @Pattern(regexp = "[A-Z]{2}[0-9]{4}", message = "Must be IATA flight number format.")
    @Schema(description = "Preferred flight number filter.")
    String flightNumber,

    @Email
    @Size(max = 255)
    @Schema(description = "Contact email.")
    String contactEmail,

    @Positive
    @Max(9)
    @Schema(description = "Number of adults.", minimum = "1", maximum = "9")
    int adultCount
) {}
```

| Annotation | Notes |
|---|---|
| `@NotNull` | Rejects null. For `String` prefer `@NotBlank`. |
| `@NotBlank` | Rejects null, empty, and whitespace-only strings. |
| `@NotEmpty` | Rejects null and empty collections/strings (does not trim whitespace). |
| `@Size(min, max)` | Length/size bounds for strings and collections. |
| `@Pattern(regexp)` | Regex constraint on strings. Always add a readable `message`. |
| `@Email` | RFC-5321 email format. |
| `@Min` / `@Max` | Numeric bounds (integral types and `BigDecimal`). |
| `@Positive` / `@PositiveOrZero` | > 0 or ≥ 0. |
| `@Valid` | Cascades validation into a nested object or collection element. |

## Custom Constraint — @ValidValues

For enum-like string sets that are not Java enums (e.g., driven by configuration or
an upstream API list):

### Annotation

```java
@Target({FIELD, PARAMETER, ANNOTATION_TYPE})
@Retention(RUNTIME)
@Constraint(validatedBy = ValidValuesValidator.class)
@Documented
public @interface ValidValues {
    String[] allowedValues();
    String message() default "Value must be one of the allowed values.";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

### Validator

```java
public class ValidValuesValidator
        implements ConstraintValidator<ValidValues, Object> {

    private Set<String> allowed;

    @Override
    public void initialize(ValidValues annotation) {
        allowed = Set.of(annotation.allowedValues());
    }

    @Override
    public boolean isValid(Object value, ConstraintValidatorContext context) {
        if (value == null) return true;          // let @NotNull/@NotEmpty handle null
        if (value instanceof Collection<?> col) {
            return col.stream()
                .filter(Objects::nonNull)
                .map(Object::toString)
                .allMatch(allowed::contains);
        }
        return allowed.contains(value.toString());
    }
}
```

### Usage

```java
@RequestParam("status")
@ValidValues(allowedValues = {"PENDING", "CONFIRMED", "CANCELLED"})
@NotEmpty Set<String> statuses
```

## Custom Constraint — Class-Level

For cross-field validation (e.g., departure must be before arrival):

```java
@Target(TYPE)
@Retention(RUNTIME)
@Constraint(validatedBy = ValidDateRangeValidator.class)
public @interface ValidDateRange {
    String message() default "Departure must be before arrival.";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class ValidDateRangeValidator
        implements ConstraintValidator<ValidDateRange, FlightSearchRequest> {

    @Override
    public boolean isValid(FlightSearchRequest r, ConstraintValidatorContext ctx) {
        if (r.departure() == null || r.arrival() == null) return true;
        return r.departure().isBefore(r.arrival());
    }
}

@ValidDateRange
public record FlightSearchRequest(LocalDate departure, LocalDate arrival) {}
```

## Error Response

Spring Boot maps `MethodArgumentNotValidException` (from `@Valid` on `@RequestBody`) and
`ConstraintViolationException` (from inline `@Validated` params) to validation errors.
Wire a `@RestControllerAdvice` that maps both to `ApiError`:

```java
@RestControllerAdvice
class ValidationExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.UNPROCESSABLE_ENTITY)
    ApiError handleValidation(MethodArgumentNotValidException ex) {
        List<ApiError.FieldError> fieldErrors = ex.getBindingResult()
            .getFieldErrors().stream()
            .map(fe -> new ApiError.FieldError(fe.getField(), fe.getDefaultMessage()))
            .toList();
        return new ApiError(422, "VALIDATION_ERROR", "Request validation failed.", fieldErrors);
    }

    @ExceptionHandler(ConstraintViolationException.class)
    @ResponseStatus(HttpStatus.UNPROCESSABLE_ENTITY)
    ApiError handleConstraint(ConstraintViolationException ex) {
        List<ApiError.FieldError> fieldErrors = ex.getConstraintViolations().stream()
            .map(cv -> new ApiError.FieldError(
                cv.getPropertyPath().toString(), cv.getMessage()))
            .toList();
        return new ApiError(422, "VALIDATION_ERROR", "Request validation failed.", fieldErrors);
    }
}
```

- Always return `422 Unprocessable Entity` for validation failures (not `400 Bad Request`).
- Use `ApiError` — not `ProblemDetail`.

## Validation Groups (when needed)

Use groups when the same model is reused across operations with different required fields:

```java
public interface OnCreate {}
public interface OnUpdate {}

public record PassengerRequest(
    @NotBlank(groups = OnCreate.class)  String firstName,
    @NotBlank(groups = OnCreate.class)  String lastName,
    @NotNull(groups = {OnCreate.class, OnUpdate.class}) PassengerType type
) {}

// Controller — trigger a specific group:
@Validated(OnCreate.class)
ResponseEntity<PassengerResponse> createPassenger(@RequestBody @Valid PassengerRequest request);
```

Prefer narrower request records over groups when the create/update shapes diverge significantly.

## Related Skills

- [/openapi](../openapi/SKILL.md) — how validation annotations appear alongside @Schema on models
- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — full Spring Boot 4.x stack reference
