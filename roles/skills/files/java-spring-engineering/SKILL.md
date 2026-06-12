---
name: java-spring-engineering
description: Reference knowledge for modern Java/Spring backend engineering — Java 24+, Spring Boot 4.x, GraalVM Native, API development, design patterns, JVM performance tuning, testing stack, and the Maven toolchain. Load this BEFORE writing, reviewing, or designing any Java or Spring code. Persistence, messaging, and observability details live in the data-stores, event-messaging, and observability skills.
---

# Java & Spring Engineering Reference

Reference knowledge for backend implementation work on the modern Java stack.
Load this skill before writing, reviewing, or designing Java/Spring code.

## Java & JVM (Latest Stable)

- **Java 24+**: Virtual threads (Project Loom), structured concurrency, pattern matching, records, sealed classes, switch expressions, sequenced collections, string templates, unnamed patterns and variables
- **GraalVM Native Image**:
  - Ahead-of-time (AOT) compilation for instant startup and reduced memory footprint
  - Reflection configuration and reachability metadata
  - Build-time vs runtime initialization
  - Native testing with JUnit 5 Platform Native
  - Profile-guided optimizations (PGO)
- **Build Tools**: Maven only (multi-module builds, native build plugins) — no Gradle

## Spring Ecosystem (Latest Stable)

- **Spring Boot 4.x**: Enhanced auto-configuration, observability, virtual thread support, native image optimizations
- **Spring Native**: First-class GraalVM support, automatic native hints, AOT processing, millisecond startup, 50-90% memory reduction
- **Spring Framework 7.x**: Core container, AOP, data access, declarative transactions, virtual threads integration
- **Spring Data JPA**: Repository pattern, query methods, specifications, projections, entity graphs
- **Spring Data Redis**: Caching, session management, pub/sub, distributed locks with Redisson
- **Spring Security 7.x**: Security filter chain, method security, OAuth2 resource server, native image support
- **Spring WebFlux**: Reactive programming, non-blocking I/O for high-throughput scenarios
- **Spring Modulith**: Modular monolith architecture, event-driven modules, architectural verification
- **Spring Cloud**: Service discovery (Eureka, Consul), config server, circuit breakers (Resilience4j), distributed tracing

## API Development

- **RESTful APIs**:
  - Richardson Maturity Model Level 3, HATEOAS
  - OpenAPI 3.1/Swagger for documentation
  - Proper HTTP status codes (200, 201, 204, 400, 401, 403, 404, 409, 422, 500, 503)
  - Content negotiation, versioning strategies (URL, header, media type)
  - API rate limiting, throttling, pagination (cursor-based preferred)
- **gRPC**:
  - Protocol Buffers (proto3), service definitions
  - Streaming: unary, server-streaming, client-streaming, bidirectional
  - Interceptors for logging, auth, metrics
  - Error handling with status codes and metadata
  - Load balancing, retries, deadlines

## Cross-Cutting Topics (separate skills)

Persistence, messaging, and observability are platform-wide concerns shared with other
disciplines — load the topic skill when the work touches them:

- [/data-stores](../data-stores/SKILL.md) — PostgreSQL, Redis, MongoDB, MinIO, migrations, pooling, caching patterns
- [/event-messaging](../event-messaging/SKILL.md) — NATS JetStream (the platform standard — no Kafka/RabbitMQ), listeners/publishers, outbox, CDC
- [/observability](../observability/SKILL.md) — Micrometer/Prometheus, Loki logging, OpenTelemetry/Tempo, health checks, alerting
- [/sandpipers-platform](../sandpipers-platform/SKILL.md) — the private-cloud service map (what to use instead of each AWS managed service)

## Design Patterns

- **Creational**: Builder (with records for immutability), Factory Method, Abstract Factory, Singleton via Spring beans
- **Structural**: Adapter (external/legacy integration), Decorator (logging, caching), Facade, Proxy (lazy loading, access control)
- **Behavioral**: Strategy (interchangeable algorithms), Observer (Spring Events, brokers), Command (CQRS handlers), Template Method, Chain of Responsibility (filters, interceptors)
- **Enterprise**: Repository (interface in domain, implementation in infrastructure), Unit of Work (@Transactional), Service Layer (use cases), DTO & Mapper (MapStruct), Specification (JPA Specifications), CQRS for complex domains

## Performance & Scalability

- **Profiling**: async-profiler, JProfiler, YourKit; JVM Flight Recorder (`-XX:StartFlightRecording=filename=recording.jfr`)
- **JVM Tuning**: heap sizing (-Xms/-Xmx), GC selection (G1GC low latency, ZGC/Shenandoah ultra-low latency), virtual threads for high concurrency
- **Database**: batch operations (JDBC/JPA batch), fetch joins and entity graphs against N+1, read replicas for read-heavy workloads
- **Async Processing**: CompletableFuture, @Async with custom thread pools, virtual threads, reactive streams (WebFlux)
- **Resilience**: Resilience4j circuit breakers, fallbacks, retries; rate limiting via token bucket or sliding window (Bucket4j)

## Backend Security Practices

- **Input Validation**: Bean Validation (JSR 380) with @Valid, custom validators
- **SQL Injection Prevention**: Parameterized queries only (JPA, PreparedStatement), never string concatenation
- **Output Encoding**: Prevent XSS (escape HTML, sanitize JSON)
- **Password Security**: BCrypt (cost 12+) or Argon2id — never plain text or MD5/SHA
- **Transport**: TLS 1.2+ only, HSTS; secure headers (CSP, X-Frame-Options, X-Content-Type-Options)
- **Secrets**: Never commit secrets — Vault, Sealed Secrets, or environment variables
- **Authorization**: RBAC or ABAC, enforced at method level
- Authentication design and review: delegate to the identity-security-developer agent / the `auth-engineering` skill

## Build & Development Toolchain (run via Bash)

### Maven (required — no Gradle)

```bash
mvn clean install                        # Build project
mvn clean package -DskipTests            # Build without tests
mvn spring-boot:run                      # Run Spring Boot app
mvn native:compile -Pnative              # Build GraalVM native image
mvn test                                 # Run unit tests
mvn verify                               # Run integration tests
mvn dependency:tree                      # Show dependency tree
mvn versions:display-dependency-updates  # Check for dependency updates
mvn spotless:apply                       # Format code
```

### Static Analysis & Security

```bash
mvn checkstyle:check                     # Code style
mvn pmd:check                            # PMD static analysis
mvn spotbugs:check                       # SpotBugs analysis
mvn dependency-check:check               # OWASP Dependency-Check
mvn sonar:sonar -Dsonar.host.url=... -Dsonar.login=<token>   # SonarQube
```

### Quality Standards

- SonarQube quality gate, Checkstyle, PMD, SpotBugs all green
- Spotless-enforced formatting (Google Java Style)
- Mutation testing with PIT to verify test quality
- OWASP Dependency-Check / Snyk for CVE detection
- JavaDoc for public APIs; ADRs for architectural decisions

### Testing Stack

- **Unit (≥90%)**: JUnit 5, AssertJ, Mockito — AAA pattern, parameterized tests, edge cases; never test framework code
- **Integration (≥80%)**: Testcontainers (real PostgreSQL/Redis/NATS), Spring test slices (@WebMvcTest, @DataJpaTest, @SpringBootTest), WireMock/MockServer for external HTTP, RestAssured/WebTestClient
- **Architecture**: ArchUnit to verify Clean Architecture boundaries and forbid circular dependencies
- **Contract**: Spring Cloud Contract or Pact between services
- **Performance**: Gatling or JMeter for critical paths

### CI/CD & Review

```bash
gh pr view 123 && gh pr checks           # PR status via GitHub CLI
docker build -t myapp:latest . && docker compose up -d
```

- Pipeline stages: build → test (`mvn verify`) → quality (SonarQube gate) → security (Dependency-Check/Snyk) → optional native image → deploy
- Before committing, always run the [/run-quality-checks](../run-quality-checks/SKILL.md) skill

## Related Skills

- [/microservice-template](../microservice-template/SKILL.md) — the mandatory Maven multi-module project layout (client/service/infra) for new microservices and module/package placement decisions
- [/data-stores](../data-stores/SKILL.md) · [/event-messaging](../event-messaging/SKILL.md) · [/observability](../observability/SKILL.md) · [/sandpipers-platform](../sandpipers-platform/SKILL.md) — cross-cutting platform topics
