---
name: observability
description: Reference knowledge for observability on the platform stack — structured logging to Grafana Loki, metrics via Micrometer/Prometheus, tracing via OpenTelemetry/Tempo, health checks, dashboards, and alerting with AlertManager. Load this BEFORE instrumenting a service or pipeline, defining alerts or SLOs, building dashboards, or debugging production behavior.
---

# Observability Reference

The platform observability stack: Prometheus + Grafana (metrics, `prometheus.sandpipers.io` /
`grafana.sandpipers.io`), Loki (logs), Tempo (traces), AlertManager (alerting) — all
Tailscale-only. Load this skill before instrumenting, alerting, or debugging anything in production.

## Structured Logging → Loki

- **SLF4J + Logback** with JSON encoder (Logstash encoder) — structured fields, never string-interpolated prose
- **Correlation IDs**: propagate a request/trace id via MDC across every service hop; logs without correlation ids are write-only
- **Levels**: ERROR (requires action), WARN (potential issue), INFO (significant business events), DEBUG (troubleshooting only — never enabled by default in prod)
- **Shipping**: Promtail (or Fluent Bit) ships container stdout to Loki; log to stdout, never to files in containers
- **Loki querying**: LogQL — label selectors first (`{app="orders"}`), then filters; design labels sparingly (high-cardinality labels kill Loki)
- Never log secrets, tokens, or PII; structured fields make accidental leakage greppable

## Metrics → Prometheus

- **Micrometer** as the instrumentation facade in Java services; Prometheus registry exposition on `/actuator/prometheus`
- **Custom business metrics**: counters (orders placed), timers (payment latency), gauges (queue depth) — business metrics catch what infra metrics miss
- **Built-ins**: JVM (heap, GC, threads), HikariCP pool, HTTP server timings; NATS consumer lag via the NATS exporter; node/cluster via node-exporter and kube-state-metrics
- **Naming**: `snake_case` with unit suffixes (`_seconds`, `_bytes`, `_total`); label cardinality is the budget — no user ids or unbounded values in labels
- **Recording rules** pre-compute expensive PromQL for dashboards and alerts
- **Python pipelines**: `prometheus_client` with pushgateway or scrape target for batch jobs (job duration, rows processed, failure counts, data lag)

## Tracing → Tempo

- **OpenTelemetry** instrumentation (auto-instrumentation agent for Spring, manual spans for business operations); W3C trace context propagation across HTTP and NATS hops (inject/extract headers on publish/consume)
- Export OTLP → Tempo; link traces ↔ logs via trace id in MDC, traces ↔ metrics via exemplars
- Sample deliberately: head sampling for volume, keep error traces

## Health Checks

- **Spring Boot Actuator**: `/actuator/health` with custom `HealthIndicator`s for the dependencies that matter (database, Redis, NATS)
- **Kubernetes**: liveness (restart me) vs readiness (stop routing to me) — never wire external dependencies into liveness or a dependency blip restarts the fleet; startup probes for slow boots

## Dashboards & Alerting

- **Grafana**: one overview dashboard per service (RED: rate, errors, duration) plus one per concern (NATS lag, DB pool, JVM); dashboards as code (provisioned JSON in git, deployed via GitOps)
- **AlertManager**: route by severity, group related alerts, silence during maintenance
- **Alert discipline**: alert on symptoms (error rate, latency, lag, freshness) not causes (CPU); every alert needs an owner and a runbook link; pages must be actionable — anything else is a ticket, not a page
- **SLOs**: define availability/latency targets per service, alert on error-budget burn rate rather than instant thresholds (fast-burn + slow-burn alert pairs)

## Pipeline & Data Observability

- Pipeline metrics: rows processed, duration, failure count, data lag/freshness — exported per run
- Data quality metrics: null rate, duplicate rate, schema drift alerts (see data-engineering quality tooling)
- SLAs on freshness ("data fresh within 1 hour") monitored like any SLO

## Related Skills

- [/sandpipers-platform](../sandpipers-platform/SKILL.md) — endpoints and access for the observability stack
- [/event-messaging](../event-messaging/SKILL.md) — NATS consumer lag and redelivery monitoring
- [/incident](../incident/SKILL.md) — incident response when alerts fire; postmortems
- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — Actuator and Micrometer usage in services
