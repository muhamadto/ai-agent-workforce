---
name: modulith-template
description: Standard Maven multi-module layout for a Spring Modulith application — client JAR (controller interfaces + DTOs), app module (Spring Boot modulith with enforced module boundaries), and infra module (Pulumi Java). Load when working on a Spring Modulith product — starting one, adding an application module, deciding which module/package a class belongs in, or extracting a module into a standalone microservice. Maven only, never Gradle.
---

# Modulith Template — Maven Multi-Module Structure

The layout for a product built as a **modular monolith on Spring Modulith** —
microservice-shaped boundaries, monolith-shaped deployment. Whether a project is a
modulith or standalone microservices is a per-project decision; when it is a
modulith, this layout is mandatory. Modules extracted later follow
[/microservice-template](../microservice-template/SKILL.md). Replace
`modulith-template` with the actual product name (kebab-case) throughout.
Maven ONLY — never Gradle.

## Language and Tone

- Australian English spelling throughout (colour, organise, licence, prioritise, -ise not -ize).
- No AI fluff: no filler openers ("Certainly!", "Great question!", "I'd be happy to"), no hedging, no restating the request, no unearned enthusiasm. State findings and actions directly.

## Module Overview

```
modulith-template-project/               # Parent (packaging: pom)
├── pom.xml                               # modules, dependencyManagement, pluginManagement
├── modulith-template-client/          # Published client JAR — the API surface
├── modulith-template-app/                # Spring Boot modulith — the implementation
└── modulith-template-infra/              # Pulumi Java — the infrastructure
```

Dependency direction: `app` depends on `client`. `client` depends on nothing
internal. `infra` is independent of both (it describes infrastructure, not application
code).

## modulith-template-client

The externally published API surface, organized by application module. Same rules as
a microservice client JAR: API annotations and validation only, no Spring Boot
starters, no implementation logic.

```
modulith-template-client/
└── src/main/java/<base.package>/client/
    ├── <module-a>/
    │   ├── controller/    # Controller INTERFACES — request mappings, the API contract
    │   └── model/         # DTOs — request/response models exposed to consumers
    └── <module-b>/
        ├── controller/
        └── model/
```

- Every public endpoint is defined here as an interface and nowhere else.
- Packages mirror the application modules one-to-one. When a module is later
  extracted, its slice of this JAR becomes the new service's client module verbatim.
- OpenAPI specs are generated from these interfaces; SDKs are generated from the
  OpenAPI specs in CI. Never hand-write an SDK.

## modulith-template-app

One Spring Boot application. Every **direct subpackage of the base package is a
Spring Modulith application module** — a bounded context with a verified boundary.

```
modulith-template-app/
└── src/main/java/<base.package>/
    ├── (root)                 # @SpringBootApplication + ALL @Configuration classes
    ├── <module-a>/            # one application module = one bounded context (a feature package)
    │   ├── package-info.java  # @ApplicationModule(allowedDependencies = ...)
    │   ├── <A>Controller      # implements the interface from the client module
    │   ├── <A>Service         # business logic
    │   ├── <A>Listener        # @ApplicationModuleListener handler (consuming events)
    │   ├── <A>Publish         # event publisher (producing events)
    │   ├── <A>Converter       # entity ↔ domain/DTO converter
    │   ├── <A>Repository      # data access (Spring Data)
    │   └── <A>                # persistence entity
    └── <module-b>/
        └── ...
```

All module classes sit directly in the feature package and are package-private.
There are no `internal/` packages and no layer sub-packages.

Placement rules:

- **Module API is the public types only**: classes are package-private unless another
  module genuinely needs them. Spring Modulith does not expose non-public types to
  other modules, so encapsulation holds without an `internal/` package. The only
  public types are a module API interface (facade) and published event records (in the
  client JAR where consumers outside the application need them). Expose additional
  packages only via `@NamedInterface`, and treat every use of it as a design smell to
  justify.
- **Every module declares `@ApplicationModule(allowedDependencies = ...)`** in
  `package-info.java`. An empty list is the default posture; add dependencies
  deliberately, never retroactively to silence a verification failure.
- **Modules communicate by events first**: publish a domain event record, consume
  with `@ApplicationModuleListener` (async, transactional, persisted). Direct calls
  to another module's facade are allowed but are the exception — each one couples
  the modules' availability and transaction context.
- The feature package follows the same package rules as the microservice-template
  service module, so an extracted module needs no reshuffling.
- Controllers implement an interface from the client module — never define an
  endpoint without a client interface. Controllers are thin; no business logic.
- Entities never leave their module. Only client-module DTOs cross the API
  boundary; only event records cross module boundaries internally.
- Every `@Configuration` class, cross-cutting or module-specific, lives in the
  application root package; modules hold no `@Configuration` of their own.

## Events, Outbox, and Externalization

- Use the **Spring Modulith event publication registry** (JDBC) — events publish in
  the same transaction as the state change; this IS the transactional outbox, do not
  build another one.
- Events that must leave the application (to a broker, to other systems) are marked
  `@Externalized("<topic>")`. Internal module-to-module events stay internal.
- Spring Modulith ships externalizers for Kafka/AMQP/JMS/SQS only — there is no
  NATS externalizer, so `@Externalized` alone delivers nothing. Every modulith
  project uses the platform `NatsEventExternalizer` (built on the
  `spring-modulith-events-core` SPI over the jnats/nats-spring `Connection` bean).
  Semantics are non-negotiable: the publication is marked complete on `PublishAck`
  ONLY; a failed publish leaves it incomplete for registry resubmission;
  `Nats-Msg-Id` = the event publication ID so JetStream's duplicate window makes
  resubmission safe. Never log-and-swallow a publish failure.
- JetStream streams and consumers are provisioned in the infra module (Pulumi Java),
  never by shell scripts or in-app code, and never with no-ack — publish acks are
  load-bearing.
- Event records are immutable Java records, named in past tense
  (`OrderCancelled`, not `CancelOrder`), and are public API of the publishing module
  (in the client JAR when consumers outside the application need them).

## Persistence

- One database, **one schema per module**, owned exclusively by that module.
- No cross-module foreign keys, no cross-module JPA relations, no cross-schema
  joins. If module B needs module A's data, it listens to A's events and keeps its
  own projection, or calls A's facade.
- Migrations are per-module (one Flyway/Liquibase location per schema) so an
  extracted module takes its migration history with it.

## Verification — Non-Negotiable

Two tests exist from day one and run in every build:

```java
class ModularityTests {

    ApplicationModules modules = ApplicationModules.of(Application.class);

    @Test
    void verifiesModuleStructure() {
        modules.verify();   // boundary violations fail the build
    }

    @Test
    void writesDocumentation() {
        new Documenter(modules).writeDocumentation();  // C4/PlantUML per module
    }
}
```

- `modules.verify()` failing is a build failure, never a warning to suppress.
- Module slice tests use `@ApplicationModuleTest` with Testcontainers — a module
  must be testable without bootstrapping its neighbours.

## modulith-template-infra

Identical conventions to the microservice template: **Pulumi with Java**, using shared `sandpipers-iac` constructs.

```
modulith-template-infra/
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
- No application code, no client/app dependencies.
- Render Kubernetes resources into repository GitOps manifests for ArgoCD, using a render-only provider without Kubernetes credentials or API access. Helm resources use `Chart` rendering rather than `Release`. Render-only engine execution may update state; it never applies resources to the cluster.
- Cloud resources use reviewed CI preview/apply. State belongs in owned object storage with an environment-specific KMS secrets provider; do not use Pulumi Cloud state.

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

## Extracting a Module into a Microservice

Extraction is a deliberate decision with evidence, not a milestone. Extract when a
module has **proven** divergent needs: independent scaling profile, independent
deploy cadence, a different runtime requirement, or a separate team. Never extract
to "be more microservice."

Mechanics (cheap by construction):

1. Scaffold a new [/microservice-template](../microservice-template/SKILL.md) project.
2. Move the module's client packages into the new client module — consumers
   recompile against the same interfaces.
3. Move the module's feature package into the new service module's root package — the
   layout already matches; move its `@Configuration` classes from the modulith root too.
4. Replace internal event delivery with the broker: the events are already
   `@Externalized` records; point listeners at the broker topic.
5. Move the module's schema and migration history to the new service's database.
6. Add stacks/constructs to the new infra module; delete the module from the
   modulith and let `modules.verify()` confirm nothing still reaches into it.

## Scaffolding a New Modulith

1. Copy this structure, replacing every occurrence of `modulith-template` with the
   product name and `<base.package>` with the organization's base package + product
   name.
2. Define the first module's API in the client module (use the /api-design skill).
3. Create the application module: `package-info.java` with `@ApplicationModule`,
   a package-private implementation directly in the feature package (only the module
   API interface and published events public), driving each piece with tests.
4. Add the two modularity tests before writing the second module.
5. Add stacks/constructs to the infra module for the runtime the app needs.
6. Verify the build from the parent: `./mvnw clean verify` must pass at the root.

## Related Skills

- [/microservice-template](../microservice-template/SKILL.md) — the extraction target for a module that has earned independence
- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — the stack reference for everything inside the app module
- [/api-design](../api-design/SKILL.md) — designing the client module
- [/db-migration-review](../db-migration-review/SKILL.md) — reviewing per-module schema changes
