---
name: microservice-template
description: Standard Maven multi-module layout for a Spring Boot microservice — client JAR (controller interfaces + DTOs), service module (implementation), and infra module (Pulumi Java). Load when creating a new microservice, adding a module to one, or deciding which module/package a class belongs in. Maven only, never Gradle.
---

# Microservice Template — Maven Multi-Module Structure

Every microservice follows this three-module Maven layout. Replace `microservice-template`
with the actual service name (kebab-case) throughout. Maven ONLY — never Gradle.

## Language and Tone

- Australian English spelling throughout (colour, organise, licence, prioritise, -ise not -ize).
- No AI fluff: no filler openers ("Certainly!", "Great question!", "I'd be happy to"), no hedging, no restating the request, no unearned enthusiasm. State findings and actions directly.

## Module Overview

```
microservice-template-project/              # Parent (packaging: pom)
├── pom.xml                                  # modules + <parent> sandpipers-microservice-parent
├── microservice-template-client/            # Published client JAR — the API contract
├── microservice-template-service/           # Spring Boot application — the implementation
└── microservice-template-infra/             # Pulumi Java — the infrastructure
```

Dependency direction: `service` depends on `client`. `client` depends on nothing internal.
`infra` is independent of both (it describes infrastructure, not application code).

The project's parent POM extends `io.sandpipers:sandpipers-microservice-parent`, which itself
extends `io.sandpipers:sandpipers-parent` (JDK 25/GraalVM build conventions) and, transitively,
imports `io.sandpipers:sandpipers-dependencies` (the Sandpipers BOM). Don't redeclare compiler,
enforcer, Spotless, surefire/failsafe, or `spring-boot-maven-plugin` config locally — it's already
there, including the unit/IT split (`*Test` vs `*IT`) and the JDK 25 Mockito `argLine` fix.

## microservice-template-client

The contract other services (and this service's own controllers) compile against.
Keep dependencies minimal — API annotations and validation only, no Spring Boot starters,
no implementation logic. This JAR is published for consumers.

```
microservice-template-client/
└── src/main/java/<base.package>/client/
    ├── common/            # shared types only: ApiError, the OpenAPI error-response annotation
    └── earn/              # one package per feature (example)
        ├── EarnApi.java       # controller INTERFACE — request mappings, the API contract
        ├── EarnRequest.java   # DTOs exposed to consumers
        ├── EarnResponse.java
        └── EarnCreated.java   # event record the service publishes or consumes
```

- One `-client` JAR carries controller interfaces, DTOs and events. There is no
  separate `-contracts` module.
- Client packages are by feature, mirroring the service module. No `controller/`,
  `model/`, `event/` or `validation/` sub-packages.
- Classes are public, because the client JAR is the published surface.
- The controller interface is the only place endpoints are defined.
- DTOs are the types those interfaces use. No entities, no domain objects.
- Event records are immutable and named in past tense.

## microservice-template-service

The Spring Boot application. Implements the client contract.

```
microservice-template-service/
└── src/main/java/<base.package>/
    ├── (root)             # @SpringBootApplication + ALL @Configuration classes
    └── earn/              # one package per feature (example)
        ├── EarnController.java   # implements the interface from the client module
        ├── EarnService.java
        ├── EarnListener.java     # inbound events
        ├── EarnPublish.java      # outbound events
        ├── EarnConverter.java    # entity <-> DTO
        ├── EarnRepository.java
        └── Earn.java             # entity
```

Add `io.sandpipers:sandpipers-microservice-starter` as a dependency (web, actuator, validation, and
the Sandpipers shared libraries in one) and `io.sandpipers:sandpipers-test-starter` with
`<scope>test</scope>` (JUnit 5, MockMvc/MockMvcTester, Testcontainers Postgres — no version needed
on either, both come from the BOM). Don't add `spring-boot-starter-web`/`-actuator`/`-validation` or
`spring-boot-starter-test`/Testcontainers individually — that's what the two starters are for.

Placement rules:

- Controllers implement an interface from the client module — never define an endpoint
  that has no interface in the client JAR.
- Controllers are thin: translate the call, delegate to the feature's service. No business logic.
- Entities never leave the service module: the converter maps entity ↔ DTO,
  and only client-module DTOs cross the API boundary.
- Messaging is split by direction: inbound handlers in `<Feature>Listener`, outbound in `<Feature>Publish`.

## Package Rules

- All `@Configuration` classes live in the application's root package, next to the
  `@SpringBootApplication` class. No `config` package.
- Package by feature: `<root>.<feature>` holds everything for that feature: controller,
  service, listener, publisher, converter, repository and entity. Example for `earn`:
  `earn/EarnController`, `EarnService`, `EarnListener`, `EarnPublish`, `EarnConverter`,
  `EarnRepository`, `Earn` (entity).
- Classes are package-private unless another feature genuinely needs them.
- No `internal` packages and no layer sub-packages (`controller/`, `service/`,
  `repository/` and the like).
- Caching only through `@Cacheable`, `@CachePut` and `@CacheEvict` annotations; no
  hand-written cache calls.

## microservice-template-infra

Infrastructure for this service as code, using **Pulumi with Java**, using shared `sandpipers-iac` constructs.
The `-infra` module is a Pulumi Java program over the shared constructs:

```
microservice-template-infra/
├── Pulumi.yaml                  # runtime: java, options.binary: target/<app>.jar (shaded jar)
├── Pulumi.<stack>.yaml          # one per environment (dev, staging, prod)
└── src/
    ├── main/java/<base.package>/infra/
    │   ├── App.java                 # Pulumi entry point, render-only
    │   ├── <Service>StackConfig.java  # whitelist-validated stack configuration
    │   └── <Service>Stack.java      # composes NatsAccount, NatsStream, NatsConsumer,
    │                                #   NatsDeadLetterStream and NatsServicePermissions
    │                                #   with exact names (no wildcards)
    └── test/java/<base.package>/infra/
        ├── <Service>StackConfigTest.java  # config validation test
        └── InfraAppTest.java        # runs App with PulumiMockStack
```

- The stack convention is `Pulumi.yaml` with `runtime: {name: java, options: {binary: target/<app>.jar}}`; the application JAR is built with `./mvnw package`. Verify the executable configuration in the IaC spike before deployment.
- `<Service>StackConfig` validates every field against an allow-list (whitelist validation).
- The stack class composes `NatsAccount`, `NatsStream`, `NatsConsumer`, `NatsDeadLetterStream`
  and `NatsServicePermissions` with exact names; no wildcard subjects or permissions.
- Tests: a config validation test and an `InfraAppTest` using `PulumiMockStack`.
- No application code, no client/service dependencies.
- Render Kubernetes resources into repository GitOps manifests for ArgoCD, using a render-only provider without Kubernetes credentials or API access. Helm resources use `Chart` rendering rather than `Release`. Render-only engine execution may update state; it never applies resources to the cluster.
- Cloud resources use reviewed CI preview/apply. State belongs in owned object storage with an environment-specific KMS secrets provider; do not use Pulumi Cloud state.

## Parent POM

```xml
<parent>
  <groupId>io.sandpipers</groupId>
  <artifactId>sandpipers-microservice-parent</artifactId>
  <version>0.1.0-SNAPSHOT</version>
</parent>

<artifactId>microservice-template-project</artifactId>
<packaging>pom</packaging>

<modules>
  <module>microservice-template-client</module>
  <module>microservice-template-service</module>
  <module>microservice-template-infra</module>
</modules>
```

- No local `<dependencyManagement>` or plugin config — `sandpipers-microservice-parent` already
  supplies the managed versions (via `sandpipers-dependencies`) and the compiler/enforcer/Spotless/
  surefire/failsafe/`spring-boot-maven-plugin` setup. Child POMs declare dependencies without
  versions.
- A `-DskipTests -Pnative` build (or the `native` profile alone) produces a GraalVM native
  executable via the parent's `native-maven-plugin` wiring — no extra setup needed per service.

## Scaffolding a New Service

1. Copy this structure, replacing every occurrence of `microservice-template` with the
   service name and `<base.package>` with the organization's base package + service name.
2. Define the API first: controller interfaces and DTOs in the client module
   (use the /api-design skill for the contract).
3. Implement in the service module: entity → repository → service → controller,
   driving each piece with tests.
4. Add stacks/constructs to the infra module for the runtime the service needs.
5. Verify the build from the parent: `./mvnw clean verify` must pass at the root.

## Related Skills

- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — the stack reference for everything inside the service module
- [/junit5](../junit5/SKILL.md) — the `ApplicationIT` pattern and test slices that `sandpipers-test-starter` supports
- [/api-design](../api-design/SKILL.md) — designing the client module's contract
- [/db-migration-review](../db-migration-review/SKILL.md) — reviewing schema changes that accompany entity changes

All of this lives in the `sandpipers-foundation` monorepo (`~/Workspace/sandpipers-foundation`):
`sandpipers-dependencies` (BOM, no parent), `sandpipers-parent` (build conventions, extends the BOM),
`sandpipers-commons` (reactor for `sandpipers-lang`, `sandpipers-problems`, `sandpipers-logging`,
`sandpipers-microservice-starter`, and `sandpipers-test-starter`), and `sandpipers-microservice-parent`
(extends `sandpipers-parent`) as four top-level directories under that one root.
