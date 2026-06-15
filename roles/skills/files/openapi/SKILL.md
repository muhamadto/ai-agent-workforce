---
name: openapi
description: Code-first OpenAPI 3.1 with Spring Boot 4.x — controller interface annotations, polymorphic schema types, @DefaultOpenApiErrorResponses, record DTOs, springdoc-openapi setup, and example objects. Load this BEFORE writing or reviewing any controller interface, request/response model, or OpenAPI annotation.
---

# Code-First OpenAPI — Spring Boot 4.x

The spec is generated from code; there are no hand-written YAML or JSON contract files.
The controller **interface** carries all OpenAPI annotations. The `@RestController`
implementation class is annotation-free — it only implements the interface.

## The Pattern in Three Layers

```
Controller interface   → all @Operation, @Parameter, @ApiResponse, @Tag
                          + @Validated, @DefaultOpenApiErrorResponses
Record / class models  → all @Schema, @JsonTypeInfo, validation annotations
@RestController impl   → @RequestMapping, @RestController — NOTHING else
```

## springdoc-openapi Setup

```xml
<dependency>
  <groupId>org.springdoc</groupId>
  <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
</dependency>
```

Global `info.description` (in the `@OpenAPIDefinition` on the Spring Boot main class, or a
`@Configuration` bean returning an `OpenAPI` object) **must** explain the domain model:
the platform's Order ID is canonical — any PNR or e-ticket an airline's PSS creates
behind its NDC API is an implementation detail of that airline's connector and never
surfaces in this API.

## Controller Interface

```java
@Validated
@Tag(name = "Orders")
@DefaultOpenApiErrorResponses
public interface OrderApi {

    @PostMapping(value = "/api/v1/orders", consumes = APPLICATION_JSON_VALUE,
                 produces = APPLICATION_JSON_VALUE)
    @Operation(
        summary = "Create an order.",
        description = """
            Creates an Order from a previously priced Offer. The Order ID returned is
            canonical — it is the only identifier used for all subsequent servicing
            operations. Airline-internal PNR or e-ticket references, if any, are
            implementation details of the connector and are not exposed.
            """,
        parameters = @Parameter(
            name = "Idempotency-Key", in = HEADER, required = true,
            description = "Client-generated UUID v4. Safe to retry on network failure."),
        responses = @ApiResponse(
            responseCode = "201",
            description = "Order created.",
            content = @Content(
                schema = @Schema(implementation = OrderResponse.class),
                examples = @ExampleObject(name = "economy", value = ORDER_EXAMPLE))))
    ResponseEntity<OrderResponse> createOrder(
        @RequestBody @Valid OrderRequest request);

    @GetMapping(value = "/api/v1/orders/{orderId}", produces = APPLICATION_JSON_VALUE)
    @Operation(
        summary = "Retrieve an order.",
        parameters = @Parameter(
            name = "orderId", in = PATH, required = true,
            description = "The platform Order ID."),
        responses = @ApiResponse(
            responseCode = "200",
            description = "Order details.",
            content = @Content(schema = @Schema(implementation = OrderResponse.class))))
    OrderResponse getOrder(
        @PathVariable("orderId") @NotBlank String orderId);
}
```

**Rules:**
- `@Validated` goes on the interface, not the `@RestController` impl.
- Path/query/header parameters that cannot be inferred from the method signature must have
  explicit `@Parameter`. Do not duplicate what Spring can infer.
- Always set `produces`/`consumes` on the mapping annotation.
- Example constants (`ORDER_EXAMPLE`) are `static final String` fields in the interface.
- Use `ResponseEntity<T>` only when you need to control headers (e.g. `Location` on 201).
  Plain `T` return type is fine for GET.

## @DefaultOpenApiErrorResponses

A meta-annotation that DRYs up the standard error responses. Define it once per project:

```java
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@ApiResponses({
    @ApiResponse(responseCode = "400",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "401",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "403",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "404",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "422",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
    @ApiResponse(responseCode = "500",
        content = @Content(schema = @Schema(implementation = ApiError.class))),
})
public @interface DefaultOpenApiErrorResponses {}
```

Use `ApiError` — NOT `ProblemDetail`. Apply `@DefaultOpenApiErrorResponses` at the
interface type level so it covers all operations; override per-operation only when a
specific operation has a distinct error contract.

## Response/Request Models — Record DTOs

```java
@Schema(description = "Airline order.")
public record OrderResponse(

    @Schema(description = "Platform Order ID. Canonical identifier for all servicing operations.")
    @NotBlank
    String orderId,

    @Schema(description = "Current order status.", allowableValues = {"PENDING", "CONFIRMED", "CANCELLED"})
    @NotNull
    OrderStatus status,

    @Schema(description = "Passenger journeys within the order.")
    @NotEmpty
    List<JourneyResponse> journeys
) {}
```

- Records are the default DTO type — immutable, no Lombok required.
- Put `@Schema` on the record class AND on each component (field/accessor).
- Put Bean Validation annotations on the same line as `@Schema` for the same component.
- For mutable classes (when a record cannot be used), annotate the field, not the getter.

## Polymorphic Types

Use when a response field can be one of several concrete subtypes distinguished by a
discriminator property present in the JSON payload.

### Abstract base

```java
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "fareType",
    visible = true)
@JsonSubTypes({
    @JsonSubTypes.Type(value = PublishedFare.class, name = "PUBLISHED"),
    @JsonSubTypes.Type(value = NegotiatedFare.class, name = "NEGOTIATED"),
})
@Schema(
    description = "Base fare. Subtyped by `fareType`: PUBLISHED | NEGOTIATED.",
    discriminatorProperty = "fareType",
    discriminatorMapping = {
        @DiscriminatorMapping(schema = PublishedFare.class, value = "PUBLISHED"),
        @DiscriminatorMapping(schema = NegotiatedFare.class, value = "NEGOTIATED"),
    },
    oneOf = {PublishedFare.class, NegotiatedFare.class})
public abstract class Fare {

    @NotBlank
    @Schema(description = "Fare type discriminator.", allowableValues = {"PUBLISHED", "NEGOTIATED"})
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
- `visible = true` on `@JsonTypeInfo` keeps the discriminator field in the deserialized
  object so `getFareType()` returns the real value rather than null.
- `include = EXISTING_PROPERTY` means the discriminator is already in the payload as a
  regular field — do not add it as a wrapper.
- Put `@JsonTypeInfo` + `@JsonSubTypes` + `@Schema` on the abstract base class only.
- The discriminator property must also appear as an annotated abstract method on the base.
- For Jackson 3.x (Spring Boot 4): import from `tools.jackson.databind.annotation`.

## Multiple Examples

```java
@ApiResponse(
    responseCode = "200",
    content = @Content(
        schema = @Schema(implementation = SearchResponse.class),
        examples = {
            @ExampleObject(name = "direct-flight",    value = DIRECT_FLIGHT_EXAMPLE),
            @ExampleObject(name = "connecting-flight", value = CONNECTING_FLIGHT_EXAMPLE),
        }))
```

Example constants are `static final String` fields in the same interface. Keep them short:
reference an external file via `externalValue` if the JSON exceeds ~30 lines.

## @RestController Implementation

```java
@RestController
@RequestMapping          // NO path here — it's on the interface mapping annotations
class OrderController implements OrderApi {

    private final OrderService orderService;

    OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @Override
    public ResponseEntity<OrderResponse> createOrder(OrderRequest request) {
        OrderResponse response = orderService.createOrder(request);
        URI location = URI.create("/api/v1/orders/" + response.orderId());
        return ResponseEntity.created(location).body(response);
    }

    @Override
    public OrderResponse getOrder(String orderId) {
        return orderService.getOrder(orderId);
    }
}
```

- No `@Operation`, `@Tag`, `@Schema`, `@Parameter`, or any springdoc annotation here.
- No `@Validated` here — it's on the interface.
- Package-private class; the interface is public.

## ApiError (custom — not ProblemDetail)

```java
@Schema(description = "API error response.")
public record ApiError(
    @Schema(description = "HTTP status code.") int status,
    @Schema(description = "Machine-readable error code.") String code,
    @Schema(description = "Human-readable message.") String message,
    @Schema(description = "Per-field validation errors, if any.")
    List<FieldError> errors
) {
    public record FieldError(
        @Schema(description = "Field path.") String field,
        @Schema(description = "Rejection reason.") String message
    ) {}
}
```

Use `ApiError` everywhere — never `org.springframework.http.ProblemDetail`.

## Related Skills

- [/validation](../validation/SKILL.md) — Bean Validation annotations on models and controllers
- [/api-design](../api-design/SKILL.md) — URI design, versioning, HTTP semantics, pagination
- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — full Spring Boot 4.x stack reference
