---
name: openapi
description: Code-first OpenAPI 3.1 with Spring Boot 4.x — controller interface annotations, HTTP status codes, response/error shapes, pagination, polymorphic schemas, @DefaultOpenApiErrorResponses, record DTOs, schema type rules, and springdoc-openapi setup. Load this BEFORE writing or reviewing any controller interface, request/response model, or OpenAPI annotation.
---

# Code-First OpenAPI — Spring Boot 4.x

The spec is generated from code; there are no hand-written YAML or JSON contract files.
The controller **interface** carries all OpenAPI annotations. The `@RestController`
implementation class is annotation-free — it only implements the interface.

## The Pattern in Three Layers

```
Controller interface   → @Operation, @Parameter, @ApiResponse, @Tag, @Validated,
                          @DefaultOpenApiErrorResponses
Record / class models  → @Schema, @JsonTypeInfo, validation annotations
@RestController impl   → @RequestMapping, @RestController — NOTHING else
```

## springdoc-openapi Setup

```xml
<dependency>
  <groupId>org.springdoc</groupId>
  <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
</dependency>
```

Global `info.description` (on `@OpenAPIDefinition` or an `OpenAPI` `@Bean`) **must**
document the domain model. For Order-native platforms: state that the Order ID is
canonical, PNR/e-ticket references are connector implementation details not surfaced in
this API, and that customers operate only on Order IDs for all servicing operations.

## HTTP Status Codes

### Success codes

| Method | Code | Required Headers | Body |
|--------|------|-----------------|------|
| `POST` (create) | **201 Created** | `Location: /api/v1/resource/{id}` | created resource |
| `POST` (async) | **202 Accepted** | `Location: /api/v1/jobs/{id}` | job resource |
| `PUT` / `PATCH` | **200 OK** | — | updated resource |
| `GET` (single) | **200 OK** | — | resource |
| `GET` (list) | **200 OK** | — | paginated collection |
| `DELETE` | **204 No Content** | — | empty |

### Error codes

| Code | Meaning | When to return |
|------|---------|----------------|
| `400` Bad Request | Malformed syntax | Unparseable JSON, wrong `Content-Type` |
| `401` Unauthorized | Missing or invalid token | No bearer token, expired, bad signature |
| `403` Forbidden | Authenticated, not permitted | Valid token, wrong scope/role |
| `404` Not Found | Resource does not exist | ID not found — use even when auth would also fail (no resource exposure) |
| `409` Conflict | State conflict | Duplicate create, resource in terminal state |
| `422` Unprocessable Entity | Valid format, failed validation | Missing required field, value out of range |
| `429` Too Many Requests | Rate limit exceeded | Always include `Retry-After` header |
| `500` Internal Server Error | Unhandled exception | Log full stack trace server-side; return safe message only |
| `502` Bad Gateway | Upstream dependency error | External service call failed |
| `503` Service Unavailable | System overloaded / dependency down | Include `Retry-After` if recoverable |

Annotate every non-obvious code on the operation. `@DefaultOpenApiErrorResponses` covers
400/401/403/404/422/500; add `409`/`429`/`502`/`503` per-operation when applicable.

```java
@Operation(...)
@ApiResponse(responseCode = "409",
    description = "Order already exists for this idempotency key.",
    content = @Content(schema = @Schema(implementation = ApiError.class)))
@ApiResponse(responseCode = "429",
    description = "Rate limit exceeded.",
    headers = @Header(name = "Retry-After", description = "Seconds until the limit resets."),
    content = @Content(schema = @Schema(implementation = ApiError.class)))
ResponseEntity<OrderResponse> createOrder(...);
```

## Controller Interface

```java
@Validated
@Tag(name = "Orders")
@DefaultOpenApiErrorResponses
public interface OrderApi {

    @PostMapping(value = "/api/v1/orders",
                 consumes = APPLICATION_JSON_VALUE,
                 produces = APPLICATION_JSON_VALUE)
    @Operation(
        summary = "Create an order.",
        description = """
            Creates an Order from a previously priced Offer. The Order ID returned is
            canonical for all servicing. Any airline-internal PNR is a connector
            implementation detail and is not exposed.
            """,
        parameters = @Parameter(
            name = "Idempotency-Key", in = HEADER, required = true,
            description = "Client-generated UUID v4. Safe to retry on network failure."),
        responses = @ApiResponse(
            responseCode = "201",
            description = "Order created.",
            headers = @Header(name = "Location",
                description = "URL of the newly created order."),
            content = @Content(
                schema = @Schema(implementation = OrderResponse.class),
                examples = @ExampleObject(name = "economy", value = ORDER_EXAMPLE))))
    ResponseEntity<OrderResponse> createOrder(
        @RequestBody @Valid OrderRequest request);

    @GetMapping(value = "/api/v1/orders/{orderId}", produces = APPLICATION_JSON_VALUE)
    @Operation(
        summary = "Retrieve an order.",
        parameters = @Parameter(name = "orderId", in = PATH, required = true,
            description = "Platform Order ID."),
        responses = @ApiResponse(responseCode = "200",
            content = @Content(schema = @Schema(implementation = OrderResponse.class))))
    OrderResponse getOrder(@PathVariable("orderId") @NotBlank String orderId);

    @GetMapping(value = "/api/v1/orders", produces = APPLICATION_JSON_VALUE)
    @Operation(
        summary = "List orders.",
        parameters = {
            @Parameter(name = "cursor", in = QUERY,
                description = "Opaque pagination cursor from the previous response."),
            @Parameter(name = "limit", in = QUERY,
                description = "Maximum items to return. Default 20, max 100.")
        },
        responses = @ApiResponse(responseCode = "200",
            content = @Content(schema = @Schema(implementation = OrderPage.class))))
    OrderPage listOrders(
        @RequestParam(required = false) String cursor,
        @RequestParam(defaultValue = "20") @Max(100) int limit);
}
```

**Rules:**
- `@Validated` on the interface, not the `@RestController` impl.
- Always set `produces` and `consumes` on the mapping annotation.
- Use `ResponseEntity<T>` only when you need to set headers (201 `Location`, etc.).
  Plain `T` is fine for GET.
- Example string constants (`ORDER_EXAMPLE`) are `static final String` fields on the
  interface. Keep them short; use `externalValue` for examples over ~30 lines.
- Every path/query/header parameter that cannot be inferred from the method signature
  must have an explicit `@Parameter`.
- `operationId` is derived from the method name by springdoc — name methods descriptively
  (`createOrder`, `getOrder`, `listOrders`) so the generated operationId is clean.

## @DefaultOpenApiErrorResponses

```java
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@ApiResponses({
    @ApiResponse(responseCode = "400",
        description = "Malformed request.",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "401",
        description = "Missing or invalid authentication token.",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "403",
        description = "Authenticated but not authorised for this operation.",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "404",
        description = "Resource not found.",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "422",
        description = "Request validation failed.",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "500",
        description = "Internal server error.",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
})
public @interface DefaultOpenApiErrorResponses {}
```

Apply at the interface type level. Override per-operation only when a specific operation
has a non-standard error contract (e.g. adds `409` or `429`).

## ApiError (custom — not ProblemDetail)

```java
@Schema(description = "API error response.")
public record ApiError(
    @Schema(description = "HTTP status code.") int status,
    @Schema(description = "Machine-readable error code (SCREAMING_SNAKE_CASE).") String code,
    @Schema(description = "Human-readable message. Never exposes stack traces or "
        + "internal IDs.") String message,
    @Schema(description = "Per-field validation errors. Present on 422 only.")
    List<FieldError> errors
) {
    public record FieldError(
        @Schema(description = "Dot-notation field path.") String field,
        @Schema(description = "Rejection reason.") String message
    ) {}
}
```

- Never use `org.springframework.http.ProblemDetail`.
- `code` is `SCREAMING_SNAKE_CASE` and machine-readable.
- `message` never contains stack traces, SQL, internal IDs.
- `errors` is populated only for `422`; null or empty for all other codes.

## Request/Response Models — Record DTOs

```java
@Schema(description = "Airline order.")
public record OrderResponse(

    @Schema(description = "Platform Order ID. Canonical identifier for all servicing.")
    @NotBlank
    String orderId,

    @Schema(description = "Order status.",
            allowableValues = {"PENDING", "CONFIRMED", "CANCELLED"})
    @NotNull
    OrderStatus status,

    @Schema(description = "ISO 8601 UTC creation timestamp. Example: 2024-01-15T10:30:00Z",
            format = "date-time")
    @NotNull
    Instant createdAt,

    @Schema(description = "Total fare amount in the smallest currency unit (cents).",
            example = "29999")
    @NotNull
    long totalAmountCents,

    @Schema(description = "ISO 4217 currency code.", example = "AUD")
    @NotBlank
    String currency,

    @Schema(description = "Passenger journeys.")
    @NotEmpty
    List<JourneyResponse> journeys
) {}
```

- Records are the default DTO type — immutable, no Lombok.
- Put `@Schema` and validation annotations on the same record component.
- For mutable classes (when records cannot be used), annotate the field.

## Schema Type Rules

| Data type | Java type | `@Schema` format |
|-----------|-----------|-----------------|
| Monetary amount | `long` (cents) or `BigDecimal` | `"integer"` (cents) — never `float`/`double` |
| UUID | `String` or `UUID` | `format = "uuid"` |
| Timestamp | `Instant` or `OffsetDateTime` | `format = "date-time"` — always UTC, `Z` suffix |
| Date only | `LocalDate` | `format = "date"` |
| Email | `String` | `format = "email"` |
| Enum | Java `enum` or `String` | `allowableValues = {…}` |
| Nullable field | include `nullable = true` in `@Schema` | — |

All timestamps: ISO 8601, UTC only, `Z` suffix. Example: `2024-01-15T10:30:00Z`.

Never use `float` or `double` for monetary values (floating-point rounding).

## Pagination

```java
@Schema(description = "Paginated collection of orders.")
public record OrderPage(
    @Schema(description = "Orders for this page.")
    List<OrderResponse> data,

    @Schema(description = "Opaque cursor for the next page. Null if this is the last page.")
    @Nullable String nextCursor,

    @Schema(description = "Whether more pages exist.")
    boolean hasMore
) {}
```

- Use **cursor-based** pagination. Offset pagination is discouraged (poor performance at
  scale and unstable under concurrent inserts).
- Cursors are opaque tokens (base64-encoded internal state).
- Default page size: 20. Maximum: 100.
- Return `400` if a cursor has expired or is malformed.

## Long-Running Operations (202 Accepted)

Operations expected to exceed 5 seconds respond with `202 Accepted` and a `Location`
header pointing to a job resource. Clients poll until the job reaches a terminal state.

```java
@PostMapping("/api/v1/exports")
@Operation(
    responses = @ApiResponse(responseCode = "202",
        description = "Export job accepted.",
        headers = @Header(name = "Location",
            description = "URL of the job resource to poll.")))
ResponseEntity<Void> startExport(@RequestBody @Valid ExportRequest request);

@GetMapping("/api/v1/exports/{jobId}")
@Operation(
    responses = @ApiResponse(responseCode = "200",
        content = @Content(schema = @Schema(implementation = ExportJob.class))))
ExportJob getExportJob(@PathVariable String jobId);
```

Job states: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`.

## Rate Limiting Headers

Document rate-limiting headers on operations that are rate-constrained:

```java
@ApiResponse(responseCode = "200",
    headers = {
        @Header(name = "RateLimit-Limit",     description = "Requests allowed per window."),
        @Header(name = "RateLimit-Remaining", description = "Requests remaining this window."),
        @Header(name = "RateLimit-Reset",     description = "Unix timestamp when the window resets.")
    })
```

On `429`, document the `Retry-After` header:

```java
@ApiResponse(responseCode = "429",
    headers = @Header(name = "Retry-After",
        description = "Seconds until the rate limit resets."))
```

## Polymorphic Types

Use when a field can be one of several concrete subtypes distinguished by a discriminator
property already present in the JSON payload (`EXISTING_PROPERTY`).

### Abstract base

```java
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "fareType",
    visible = true)          // keep the discriminator in the deserialized object
@JsonSubTypes({
    @JsonSubTypes.Type(value = PublishedFare.class,   name = "PUBLISHED"),
    @JsonSubTypes.Type(value = NegotiatedFare.class,  name = "NEGOTIATED"),
})
@Schema(
    description = "Fare. Subtyped by `fareType`.",
    discriminatorProperty = "fareType",
    discriminatorMapping = {
        @DiscriminatorMapping(schema = PublishedFare.class,  value = "PUBLISHED"),
        @DiscriminatorMapping(schema = NegotiatedFare.class, value = "NEGOTIATED"),
    },
    oneOf = {PublishedFare.class, NegotiatedFare.class})
public abstract class Fare {

    @NotBlank
    @Schema(description = "Fare type discriminator.",
            allowableValues = {"PUBLISHED", "NEGOTIATED"})
    public abstract String getFareType();
}
```

### Concrete subtype

```java
@Schema(description = "IATA published fare.")
public class PublishedFare extends Fare {

    @Override
    public String getFareType() { return "PUBLISHED"; }

    @NotNull
    @Schema(description = "Fare basis code.")
    private String fareBasisCode;
}
```

**Rules:**
- `visible = true` keeps the discriminator in the object so `getFareType()` returns
  the real value.
- `include = EXISTING_PROPERTY` — the discriminator is a regular field in the payload.
- All Jackson + OpenAPI annotations go on the abstract base only.
- For Jackson 3.x (Spring Boot 4): import from `tools.jackson.databind.annotation`.

## Multiple Examples

```java
@ApiResponse(
    responseCode = "200",
    content = @Content(
        schema = @Schema(implementation = SearchResponse.class),
        examples = {
            @ExampleObject(name = "direct-flight",     value = DIRECT_FLIGHT_EXAMPLE),
            @ExampleObject(name = "connecting-flight", value = CONNECTING_FLIGHT_EXAMPLE),
        }))
```

Example constants are `static final String` fields in the same interface.
Use `externalValue` for examples that exceed ~30 lines.

## @RestController Implementation

```java
@RestController
class OrderController implements OrderApi {

    private final OrderService orderService;

    OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @Override
    public ResponseEntity<OrderResponse> createOrder(OrderRequest request) {
        OrderResponse body = orderService.createOrder(request);
        URI location = URI.create("/api/v1/orders/" + body.orderId());
        return ResponseEntity.created(location).body(body);
    }

    @Override
    public OrderResponse getOrder(String orderId) {
        return orderService.getOrder(orderId);
    }

    @Override
    public OrderPage listOrders(String cursor, int limit) {
        return orderService.listOrders(cursor, limit);
    }
}
```

- No springdoc annotations here — the interface owns all of them.
- No `@Validated` here — it's on the interface.
- Package-private class; the interface is public.

## OpenAPI Completeness Checklist

Before merging a new controller interface, verify:

- [ ] `@Tag` on the interface
- [ ] `@Operation(summary, description)` on every operation
- [ ] `@Parameter` for every path, query, and non-trivial header param
- [ ] Success `@ApiResponse` with response schema and at least one `@ExampleObject`
- [ ] `@DefaultOpenApiErrorResponses` on the interface; extra codes (409, 429…) per op
- [ ] `Location` header documented on 201 operations
- [ ] `Idempotency-Key` header documented on POST create operations
- [ ] Pagination parameters documented on list operations
- [ ] All timestamps annotated `format = "date-time"` with UTC note
- [ ] Monetary fields typed as integer cents (never float/double)
- [ ] UUID fields annotated `format = "uuid"`
- [ ] Nullable fields have `nullable = true` in `@Schema`
- [ ] `allowableValues` present for string fields with a fixed value set

## Related Skills

- [/validation](../validation/SKILL.md) — Bean Validation annotations on models and controllers
- [/api-design](../api-design/SKILL.md) — URI design, versioning, idempotency, HTTP semantics, pagination rules
- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — full Spring Boot 4.x stack reference
