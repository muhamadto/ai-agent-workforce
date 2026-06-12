---
name: microservice-template
description: Standard Maven multi-module layout for a Spring Boot microservice — client JAR (controller interfaces + DTOs), service module (implementation), and infra module (CDK for Terraform). Load when creating a new microservice, adding a module to one, or deciding which module/package a class belongs in. Maven only, never Gradle.
---

# Microservice Template — Maven Multi-Module Structure

Every microservice follows this three-module Maven layout. Replace `microservice-template`
with the actual service name (kebab-case) throughout. Maven ONLY — never Gradle.

## Module Overview

```
microservice-template-project/              # Parent (packaging: pom)
├── pom.xml                                  # modules, dependencyManagement, pluginManagement
├── microservice-template-client/            # Published client JAR — the API contract
├── microservice-template-service/           # Spring Boot application — the implementation
└── microservice-template-infra/             # CDK for Terraform (CDKTF, Java) — the infrastructure
```

Dependency direction: `service` depends on `client`. `client` depends on nothing internal.
`infra` is independent of both (it describes infrastructure, not application code).

## microservice-template-client

The contract other services (and this service's own controllers) compile against.
Keep dependencies minimal — API annotations and validation only, no Spring Boot starters,
no implementation logic. This JAR is published for consumers.

```
microservice-template-client/
└── src/main/java/<base.package>/client/
    ├── controller/        # Controller INTERFACES — request mappings, the API contract
    └── model/             # DTOs — request/response models exposed to consumers
```

- `controller/` holds interfaces only. Endpoints are defined here and nowhere else.
- `model/` holds the DTOs those interfaces use. No entities, no domain objects.

## microservice-template-service

The Spring Boot application. Implements the client contract.

```
microservice-template-service/
└── src/main/java/<base.package>/
    ├── (root)             # @SpringBootApplication + ALL @Configuration classes — config stays in the root package
    ├── controller/        # Classes IMPLEMENTING the controller interfaces from the client module
    ├── service/           # Business services called by the controllers
    ├── repository/        # Data access (Spring Data repositories)
    ├── entity/            # Persistence entities
    ├── converter/         # Converters between entity and domain model classes
    ├── helper/            # Focused helper classes
    ├── listener/          # Event listeners (consuming events)
    └── publisher/         # Event publishers (producing events)
```

Placement rules:

- Controllers implement an interface from the client module — never define an endpoint
  that has no interface in the client JAR.
- Controllers are thin: translate the call, delegate to `service/`. No business logic.
- Entities never leave the service module: `converter/` maps entity ↔ domain model,
  and only client-module DTOs cross the API boundary.
- Configuration classes do not get their own package — they live in the root package
  next to the application class.
- Messaging is split by direction: inbound handlers in `listener/`, outbound in `publisher/`.

## microservice-template-infra

Infrastructure for this service as code, using **CDK for Terraform (CDKTF) with Java**.
Mirrors the service module's structure idea — root package for entry point and
configuration, one package per concern:

```
microservice-template-infra/
└── src/main/java/<base.package>/infra/
    ├── (root)             # CDKTF App entry point + configuration classes
    ├── stack/             # Terraform stacks (one per deployable unit/environment)
    └── construct/         # Reusable constructs composed into stacks
```

- `cdktf.json` lives in the module root; synthesis runs through Maven (`mvn compile exec:java`).
- No application code, no client/service dependencies.

## Parent POM

```xml
<groupId>com.example</groupId>
<artifactId>microservice-template-project</artifactId>
<packaging>pom</packaging>

<modules>
  <module>microservice-template-client</module>
  <module>microservice-template-service</module>
  <module>microservice-template-infra</module>
</modules>
```

- All dependency versions are managed in the parent's `<dependencyManagement>`;
  child POMs declare dependencies without versions.
- Plugin configuration (compiler, surefire, failsafe, spotless) is centralized in
  `<pluginManagement>`.

## Scaffolding a New Service

1. Copy this structure, replacing every occurrence of `microservice-template` with the
   service name and `<base.package>` with the organization's base package + service name.
2. Define the API first: controller interfaces and DTOs in the client module
   (use the /api-design skill for the contract).
3. Implement in the service module: entity → repository → service → controller,
   driving each piece with tests.
4. Add stacks/constructs to the infra module for the runtime the service needs.
5. Verify the build from the parent: `mvn clean verify` must pass at the root.

## Related Skills

- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — the stack reference for everything inside the service module
- [/api-design](../api-design/SKILL.md) — designing the client module's contract
- [/db-migration-review](../db-migration-review/SKILL.md) — reviewing schema changes that accompany entity changes
