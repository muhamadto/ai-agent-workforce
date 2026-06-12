---
name: quality-engineering
description: Reference knowledge for quality engineering — test strategy and the test pyramid, unit/integration/API/E2E testing stacks (JUnit 5, Testcontainers, RestAssured, Playwright), BDD with Cucumber, performance testing with Gatling/k6/JMeter, CI/CD quality gates, test data management, test tooling commands, and the quality-focused code review checklist. Load this BEFORE planning tests, writing or reviewing test automation, defining quality gates, or assessing test coverage.
---

# Quality Engineering Reference

Reference knowledge for test strategy, test automation, and quality gate enforcement.
Load this skill before planning, writing, or reviewing tests and quality gates.

## Test Strategy

- **Test pyramid**: Unit → Integration → E2E — heavy base, light top
- **Risk-based testing**: Prioritise critical paths and high-risk areas
- **Shift-left quality**: Catch defects early in development, not after deployment
- **Coverage targets**: ≥90% unit, ≥80% integration, 100% of critical user journeys in E2E
- **Test data management**: Factories, fixtures, seeded datasets — never production data in tests
- **Defect lifecycle**: Reproduce → isolate → document → verify fix → regression test

## Test Types

| Type | Scope | Tools |
|------|-------|-------|
| Unit | Individual classes/functions | JUnit 5, AssertJ, Mockito |
| Integration | Component interactions | Testcontainers, @DataJpaTest, @WebMvcTest |
| API | REST/gRPC contract | RestAssured, Karate, gRPC testing |
| E2E | Full user journey | Playwright, Selenium, Cypress |
| Performance | Load and stress | Gatling, k6, JMeter |
| Security | Vulnerability scanning | OWASP ZAP, Burp Suite |
| Accessibility | WCAG compliance | Axe, Lighthouse |
| Contract | API compatibility | Pact (consumer-driven contract testing) |

## Unit Testing (Mandatory)

- **Arrange-Act-Assert (AAA)**: Structure every test with clear setup, execution, and verification
- **One assertion per test**: Focused tests that fail for one reason
- **Descriptive names**: `should_returnUser_when_validIdProvided()` — clearly state given/when/then
- **Boundary testing**: Nulls, empty strings, zero, max values, edge cases
- **Negative testing**: Invalid inputs, expired tokens, missing required fields
- **Mock only external dependencies**: Keep business logic tests isolated from infrastructure
- **No sleep/wait in unit tests**: Deterministic, millisecond execution

## Integration Testing (Mandatory)

- **Testcontainers**: Real databases (PostgreSQL, MySQL, MongoDB), real message brokers (NATS JetStream), real caches (Redis)
- **Spring test slices**: `@WebMvcTest` for controllers, `@DataJpaTest` for repositories, `@SpringBootTest` for full context
- **Database state isolation**: Each test in its own transaction with rollback, or truncate tables in `@BeforeEach`
- **RestAssured**: Fluent HTTP assertions for REST API integration tests
- **WireMock**: Mock external HTTP dependencies in integration tests

## BDD (Behaviour-Driven Development)

```gherkin
Feature: User registration

  Scenario: Successful registration with valid data
    Given the user provides a valid email "user@example.com"
    And a password meeting strength requirements
    When the user submits the registration form
    Then the account is created successfully
    And a verification email is sent to "user@example.com"

  Scenario: Registration fails with duplicate email
    Given a user already exists with email "user@example.com"
    When a new user attempts to register with the same email
    Then the registration is rejected
    And the error message is "Email already in use"
```

- **Cucumber + JUnit 5**: Feature files in `src/test/resources/features/`
- **Step definitions**: Thin glue code — delegate to service/helper classes
- **Scenarios as living documentation**: Readable by non-technical stakeholders

## Performance Testing

### Load Testing Tools

- **Gatling**: Scala-based, high-throughput load simulation, HTML reports
- **k6**: JavaScript, developer-friendly, cloud execution
- **JMeter**: Enterprise-grade, GUI and CLI mode

### Performance Targets

- **P95 response time**: < 200ms for read endpoints, < 500ms for write endpoints
- **Throughput**: Define RPS targets per endpoint based on SLAs
- **Error rate**: < 0.1% under normal load
- **Degradation**: Graceful under 2× expected peak load

### Gatling Example

```scala
class UserApiSimulation extends Simulation {
  val httpProtocol = http.baseUrl("http://localhost:8080")

  val scn = scenario("User API Load Test")
    .exec(http("Get User")
      .get("/api/users/1")
      .check(status.is(200))
      .check(responseTimeInMillis.lt(200)))

  setUp(scn.inject(
    rampUsers(100).during(30.seconds),
    constantUsersPerSec(50).during(60.seconds)
  )).protocols(httpProtocol)
    .assertions(
      global.responseTime.percentile(95).lt(200),
      global.failedRequests.percent.lt(1)
    )
}
```

## CI/CD Quality Gates (Mandatory)

```yaml
# Quality gate checks — all must pass before merge
quality-gate:
  - unit-tests: coverage ≥ 90%
  - integration-tests: coverage ≥ 80%
  - sast: no high-severity findings (SonarQube, CodeQL)
  - sca: no critical CVEs (OWASP Dependency-Check, Snyk)
  - performance: P95 < 200ms, error rate < 0.1%
  - contract-tests: all consumer contracts satisfied
```

- **Fail fast**: Run fastest tests first (unit → integration → E2E)
- **Parallel execution**: Parallelise independent test suites
- **Flaky test policy**: Flaky tests are bugs — fix or quarantine, never ignore
- **Test reports**: JUnit XML, Allure, or HTML reports as CI artifacts

## Test Data Management

- **Object mothers / test data builders**: Reusable factories, not duplicated setup
- **Database seeding**: Liquibase/Flyway changesets for test data
- **Sensitive data**: Anonymised or synthetic data — never production PII
- **Isolation**: Tests must not depend on execution order
- **Cleanup**: Tear down test data after every test or use database transactions

## Test Tooling (run via Bash)

```bash
# Run tests
mvn test                            # unit tests
mvn verify                          # unit + integration tests
mvn test -Dtest=UserServiceTest     # single test class
mvn test -Dgroups=integration       # by JUnit 5 tag

# Coverage
mvn jacoco:report                   # generate coverage report
open target/site/jacoco/index.html  # view in browser

# Performance
mvn gatling:test                    # run Gatling simulations
k6 run src/test/k6/load-test.js     # run k6 load test

# Contract testing
mvn pact:verify                     # verify consumer contracts
mvn pact:publish                    # publish pacts to broker
```

## Code Review Checklist (Quality Focus)

- [ ] Test names clearly describe scenario and expected outcome?
- [ ] AAA pattern followed in unit tests?
- [ ] Boundary and negative cases covered?
- [ ] Testcontainers used for real infrastructure in integration tests?
- [ ] No production data or hardcoded credentials in tests?
- [ ] Tests are independent (no execution-order dependency)?
- [ ] Coverage targets met (≥90% unit, ≥80% integration)?
- [ ] Flaky tests eliminated (no sleep, deterministic assertions)?
- [ ] Performance tests cover critical paths?
- [ ] CI/CD quality gates updated?
- [ ] BDD scenarios readable by non-technical stakeholders?

## Related Skills

- [/test-plan](../test-plan/SKILL.md) — produce a structured test plan covering unit, integration, E2E, performance, and security scope for a feature or story
- [/run-quality-checks](../run-quality-checks/SKILL.md) — detect the build tool and run the full pre-commit quality gate (format, lint, test, SAST, SCA)
- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — the backend stack reference, including its testing stack (JUnit 5, Testcontainers, ArchUnit, Pact, Gatling)
- [/git-commit](../git-commit/SKILL.md) — Conventional Commits compliant commits
