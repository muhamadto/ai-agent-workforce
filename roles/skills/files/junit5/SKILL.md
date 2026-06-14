---
name: junit5
description: Testing patterns for JUnit 5 on Spring Boot 4.x — the full-context controller IT pattern (ApplicationIT abstract base, @SpringBootTest, @AutoConfigureMockMvc, Testcontainers, MockMvc + MockMvcTester), Spring test slice patterns (@WebMvcTest, @DataJpaTest), @ParameterizedTest, @MockitoBean, and JDK 25 Mockito setup. Load this BEFORE writing or reviewing integration tests, test base classes, or controller IT tests on the platform stack.
---

# JUnit 5 Testing Reference — Spring Boot 4.x

Testing patterns and prescriptions for the platform stack. Load this before writing or reviewing integration tests, controller ITs, or test base classes.

## The Dual-Layer Strategy

Every controller gets two test classes:

| Layer | Annotation | Spring Context | When to use |
|-------|-----------|----------------|-------------|
| Slice | `@WebMvcTest` | Controller + MVC only | Fast feedback — serialization, validation, status codes, mocked service |
| IT | `@SpringBootTest` + `@AutoConfigureMockMvc` | Full context | Confidence — real DB, real service, mocked external side-effects only |

Run both with `mvn verify`. Slices go in `src/test/java` (surefire); ITs follow the `*IT` naming convention (failsafe).

## Controller IT: Abstract Base Class

Define one `ApplicationIT` base per service. All controller ITs extend it.

```java
@Testcontainers
@SpringBootTest(webEnvironment = RANDOM_PORT)
@AutoConfigureMockMvc
@DirtiesContext
@ActiveProfiles("test")
public abstract class ApplicationIT {

  @Container
  static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

  @Container
  @SuppressWarnings("resource")
  static GenericContainer<?> nats =
      new GenericContainer<>("nats:2.10-alpine").withCommand("--jetstream").withExposedPorts(4222);

  @Autowired protected MockMvc mockMvc;
  @Autowired protected MockMvcTester mockMvcTester;   // AssertJ-based alternative
  @Autowired protected ObjectMapper objectMapper;

  @DynamicPropertySource
  static void overrideProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", postgres::getJdbcUrl);
    registry.add("spring.datasource.username", postgres::getUsername);
    registry.add("spring.datasource.password", postgres::getPassword);
    // Must override driver-class-name explicitly: application-test.yml sets org.h2.Driver for slices;
    // without this override @SpringBootTest picks up H2 driver and rejects the postgres JDBC URL.
    registry.add("spring.datasource.driver-class-name", () -> "org.postgresql.Driver");
    registry.add("nats.spring.server",
        () -> "nats://localhost:" + nats.getMappedPort(4222));
  }
}
```

Add containers to match what the service actually needs (postgres, nats, redis, etc.).
`@DirtiesContext` ensures each concrete IT class gets a fresh context — important when subclasses
register different `@MockitoBean` configurations.

> **Spring Boot 4 + Flyway**: `FlywayAutoConfiguration` ships in a separate Boot 4 module (not in
> `spring-boot-autoconfigure`). If Flyway is not on the classpath, any `spring.flyway.*` properties
> are silently ignored. For IT tests, rely on `ddl-auto: create-drop` (set in `application-test.yml`)
> to let Hibernate create the schema from entities — no Flyway needed.

## Controller IT: Concrete Test Class

```java
class BookControllerIT extends ApplicationIT {

  @MockitoBean private NatsBookPublisher natsBookPublisher;  // mock external side-effects only

  @Autowired private BookRepository bookRepository;

  @BeforeEach
  void cleanDatabase() {
    bookRepository.deleteAll();
  }

  @Test
  void createBook_returns201WithLocationAndBody() throws Exception {
    mockMvc
        .perform(
            post("/api/v1/books")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(sampleRequest())))
        .andDo(print())
        .andExpect(status().isCreated())
        .andExpect(header().string("Location", matchesPattern("/api/v1/books/\\d+")))
        .andExpect(jsonPath("$.title", is("The Pragmatic Programmer")));

    verify(natsBookPublisher).publish(eq("books.created"), any(BookCreatedEvent.class));
  }

  @Test
  void getBook_returns404ForUnknownId() throws Exception {
    mockMvc
        .perform(get("/api/v1/books/9999999"))
        .andDo(print())
        .andExpect(status().isNotFound())
        .andExpect(jsonPath("$.status", is(404)));
  }

  @ParameterizedTest
  @MethodSource("genreFilterCases")
  void listBooks_filtersByGenre(String genre, int expectedCount) throws Exception {
    createBookWithGenre("TECHNOLOGY");
    createBookWithGenre("TECHNOLOGY");
    createBookWithGenre("FICTION");

    mockMvc
        .perform(get("/api/v1/books").param("genre", genre))
        .andDo(print())
        .andExpect(status().isOk())
        .andExpect(jsonPath("$", hasSize(expectedCount)));
  }

  static Stream<Arguments> genreFilterCases() {
    return Stream.of(Arguments.of("TECHNOLOGY", 2), Arguments.of("FICTION", 1));
  }
}
```

Rules for controller ITs:
- Real service → real repository → real database. Mock only external I/O (message publishers, HTTP clients).
- `@BeforeEach` truncates affected tables via the repository — keeps tests independent.
- `.andDo(print())` on every request — visible in CI logs when a test fails.
- `verify()` after `mockMvc.perform()` for any mocked collaborator that should have been called.
- Use `@ParameterizedTest` + `@MethodSource` for data-driven cases.

## Spring Test Slices (Spring Boot 4.x package changes)

### @WebMvcTest — controller slice

```xml
<!-- Spring Boot 4: @WebMvcTest lives in its own artifact -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-webmvc-test</artifactId>
  <scope>test</scope>
</dependency>
```

```java
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;  // Boot 4 package

@WebMvcTest(BookController.class)
@Import(GlobalExceptionHandler.class)
class BookControllerTest {

  @Autowired private MockMvc mockMvc;
  @Autowired private ObjectMapper objectMapper;
  @MockitoBean private BookService bookService;

  @Test
  void createBook_returns201() throws Exception {
    when(bookService.createBook(any())).thenReturn(sampleResponse(1L));

    mockMvc
        .perform(post("/api/v1/books")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(sampleRequest())))
        .andDo(print())
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.id", is(1)));

    verify(bookService).createBook(any(BookRequest.class));
  }
}
```

### @DataJpaTest — repository slice

```xml
<!-- Spring Boot 4: @DataJpaTest lives in its own starter -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-data-jpa-test</artifactId>
  <scope>test</scope>
</dependency>
```

```java
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;  // Boot 4 package

@DataJpaTest
@ActiveProfiles("test")
class BookRepositoryTest {
  @Autowired private BookRepository bookRepository;
}
```

`@DataJpaTest` does NOT load `FlywayAutoConfiguration` — `ddl-auto: create-drop` in `application-test.yml`
is sufficient. No `flyway.enabled: false` needed (Flyway autoconfiguration is not loaded by the slice).

### application-test.yml (baseline for slices and ITs)

```yaml
spring:
  test:
    database:
      replace: none
  datasource:
    url: jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1
    driver-class-name: org.h2.Driver   # required: prevents Boot from auto-selecting postgres driver
  jpa:
    hibernate:
      ddl-auto: create-drop
nats:
  spring:
    server: nats://localhost:4222
```

This profile applies to both slices and `@SpringBootTest` ITs (via `@ActiveProfiles("test")`).
`create-drop` works for all contexts: slices use H2, ITs use postgres (overridden by `@DynamicPropertySource`).
`driver-class-name: org.h2.Driver` is essential — without it, Spring Boot detects the postgres driver on the
classpath and rejects the H2 JDBC URL. `ApplicationIT.overrideProperties()` then explicitly overrides it back
to `org.postgresql.Driver` for the `@SpringBootTest` context.

## @MockitoBean vs @Mock

| Annotation | Lives in | Use when |
|-----------|----------|----------|
| `@MockitoBean` | Spring context (replaces bean) | Spring Boot tests — the mock is wired as a real Spring bean |
| `@Mock` + `@ExtendWith(MockitoExtension.class)` | Mockito only (no Spring) | Pure unit tests with no Spring context |

Use `@MockitoBean` in `@WebMvcTest` and `@SpringBootTest` to replace a collaborator. The replaced bean
is reset between tests automatically.

## @ParameterizedTest Patterns

```java
// @MethodSource — Java Stream of Arguments
@ParameterizedTest
@MethodSource("genreFilterCases")
void listBooks_filtersByGenre(String genre, int expectedCount) { ... }

static Stream<Arguments> genreFilterCases() {
  return Stream.of(
      Arguments.of("TECHNOLOGY", 2),
      Arguments.of("FICTION", 1));
}

// @ValueSource — single argument
@ParameterizedTest
@ValueSource(strings = {"", " ", "\t"})
void listBooks_withBlankGenre_returnsAll(String genre) { ... }

// @CsvSource — inline CSV
@ParameterizedTest
@CsvSource({"TECHNOLOGY,2", "FICTION,1"})
void listBooks_filtersByGenre(String genre, int expectedCount) { ... }
```

## MockMvcTester (AssertJ-based, Spring 6.2+)

An alternative to `MockMvc` that returns AssertJ assertions instead of Hamcrest matchers.
Autowire both in `ApplicationIT` and use whichever reads better for the assertion at hand.

```java
mockMvcTester
    .get().uri("/api/v1/books/{id}", id)
    .exchange()
    .assertThat()
    .hasStatus(200)
    .bodyJson().extractingPath("$.title").isEqualTo("The Pragmatic Programmer");
```

## JDK 25: Mockito Setup

ByteBuddy self-attach is blocked on JDK 25. Two changes required:

**1. `src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker`**

```
mock-maker-subclass
```

**2. surefire and failsafe argLine in the module POM**

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-surefire-plugin</artifactId>
  <configuration>
    <argLine>@{argLine} -Djdk.attach.allowAttachSelf=true</argLine>
  </configuration>
</plugin>
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-failsafe-plugin</artifactId>
  <configuration>
    <argLine>@{argLine} -Djdk.attach.allowAttachSelf=true</argLine>
  </configuration>
  <executions>
    <execution>
      <goals>
        <goal>integration-test</goal>
        <goal>verify</goal>
      </goals>
    </execution>
  </executions>
</plugin>
```

`@{argLine}` is set by the JaCoCo `prepare-agent` goal — include it verbatim to avoid breaking coverage.

## Jackson 3.x in Tests (Spring Boot 4)

Spring Boot 4 uses Jackson 3 (`tools.jackson.*`), not Jackson 2 (`com.fasterxml.jackson.*`).

```java
import tools.jackson.databind.ObjectMapper;    // not com.fasterxml.jackson.databind.ObjectMapper
import tools.jackson.core.JacksonException;    // not com.fasterxml.jackson.core.JsonProcessingException
```

`JacksonException` is unchecked in Jackson 3 — no need to declare it in `throws` clauses.
`objectMapper.writeValueAsString()` and `readValue()` work identically for serialization in tests.

## Related Skills

- [/microservice-template](../microservice-template/SKILL.md) — module layout, where test base classes live
- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — the full backend stack reference including testing stack overview
- [/quality-engineering](../quality-engineering/SKILL.md) — test strategy, test pyramid, coverage targets, BDD
