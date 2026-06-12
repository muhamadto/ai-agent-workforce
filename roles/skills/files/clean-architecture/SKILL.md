---
name: clean-architecture
description: Reference knowledge for Clean Architecture enforcement — layer definitions, the Dependency Rule, boundary and isolation rules, SOLID principles, DDD tactical patterns, a catalog of architecture smells and anti-patterns, refactoring moves that restore boundaries, ArchUnit verification, and a full review checklist. Load this BEFORE reviewing code structure, judging layer or module boundaries, or arbitrating architectural decisions.
---

# Clean Architecture Reference

Reference knowledge for enforcing Clean Architecture as defined by Robert C. Martin (Uncle Bob).
Load this skill before any architecture review or boundary judgment.

## The Layers

- **Entities**: Enterprise business rules
- **Use Cases**: Application business rules
- **Interface Adapters**: Controllers, gateways, presenters
- **Frameworks & Drivers**: UI, database, external interfaces

## Rules Enforced Without Compromise

1. **Dependency Rule**: Dependencies only point inward
   - Outer layers depend on inner layers, NEVER the reverse
   - Domain layer has ZERO imports from frameworks, persistence, or transport

2. **Layer Isolation**:
   - Business rules do not know HTTP, gRPC, databases, JSON, or frameworks
   - No annotations from Spring, JPA, Jackson, etc. in domain entities
   - DTOs are NOT domain models
   - Persistence models are NOT domain models

3. **Boundary Enforcement**:
   - Use cases interact with interfaces, not implementations
   - Repository interfaces defined in domain, implemented in infrastructure
   - Controllers/presenters do NOT contain business logic
   - Entities contain behavior, not just data (no anemic domain models)

## SOLID Principles

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable
- **Interface Segregation**: Many specific interfaces > one general
- **Dependency Inversion**: Depend on abstractions, not concretions

## Domain-Driven Design Integration

- Identify and model: Entities, Value Objects, Aggregates
- Define bounded contexts and their interactions
- Ensure ubiquitous language throughout codebase
- Design anti-corruption layers for external systems
- Enforce aggregate boundaries (no direct access to internal entities)

## Violation Catalog

### Architectural Violations to Detect

- Framework leakage into core domain
- Business logic in controllers or repositories
- Direct database access from use cases
- Circular dependencies between layers
- God objects that violate Single Responsibility

### Architecture Smells

- Framework annotations in domain entities
- Database imports in domain layer
- HTTP/REST concepts in use cases
- JSON serialization in domain models
- Use cases returning persistence entities
- Controllers with business logic
- Missing abstractions at layer boundaries
- Tight coupling to specific frameworks
- Circular dependencies
- Feature envy (methods using more data from other classes)

### Anti-Patterns

- Anemic domain models (data bags with no behavior)
- Transaction script pattern in large systems
- Service layer that's just CRUD wrappers
- God services that do everything
- Transaction leakage across boundaries

### "Pragmatic Shortcuts" to Reject

- "It's just one annotation" → NO
- "We'll refactor it later" → NO
- "It's faster to put logic in the controller" → NO
- "The framework requires it" → Then abstract it away
- "It's just temporary" → NO

## Refactoring Moves That Restore Boundaries

- Extract domain logic from infrastructure
- Introduce interfaces at architectural boundaries
- Separate application logic from domain logic
- Apply ports and adapters (hexagonal) pattern

## Verification with ArchUnit

Boundaries must be enforced by automated tests, not convention alone. ArchUnit (JUnit 5) verifies layer rules in CI:

```java
@AnalyzeClasses(packages = "com.example.app")
class ArchitectureTest {

    @ArchTest
    static final ArchRule domainIsPure = noClasses()
        .that().resideInAPackage("..domain..")
        .should().dependOnClassesThat()
        .resideInAnyPackage("..infrastructure..", "..adapter..",
            "org.springframework..", "jakarta.persistence..", "com.fasterxml.jackson..");

    @ArchTest
    static final ArchRule layeredArchitecture = layeredArchitecture()
        .consideringAllDependencies()
        .layer("Domain").definedBy("..domain..")
        .layer("UseCase").definedBy("..usecase..")
        .layer("Adapter").definedBy("..adapter..")
        .layer("Infrastructure").definedBy("..infrastructure..")
        .whereLayer("Infrastructure").mayNotBeAccessedByAnyLayer()
        .whereLayer("Adapter").mayOnlyBeAccessedByLayers("Infrastructure")
        .whereLayer("UseCase").mayOnlyBeAccessedByLayers("Adapter", "Infrastructure");

    @ArchTest
    static final ArchRule noCycles = slices()
        .matching("com.example.app.(*)..").should().beFreeOfCycles();
}
```

## Review Checklist

- [ ] Are dependencies pointing inward exclusively?
- [ ] Are business rules isolated from frameworks and infrastructure?
- [ ] Can core domain be tested without databases, UI, or external services?
- [ ] Are interfaces defined in inner layers, implemented in outer layers?
- [ ] Is business domain clearly visible in code structure (screaming architecture)?
- [ ] Are use cases clearly defined and single-purpose?
- [ ] Are entities free of infrastructure concerns?
- [ ] Is there clear separation between application and domain logic?
- [ ] Can database be swapped without changing business rules?
- [ ] Can UI framework be changed without touching business logic?
- [ ] Are aggregates properly bounded?
- [ ] Is ubiquitous language used consistently?

## Related Skills

- [/microservice-template](../microservice-template/SKILL.md) — the mandatory Maven multi-module layout (client/service/infra) that physically encodes these boundaries
- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — the Java/Spring implementation stack these rules are applied to
- [/adr](../adr/SKILL.md) — document significant architectural decisions and accepted trade-offs
- [/api-design](../api-design/SKILL.md) — contract design at the interface-adapter boundary
