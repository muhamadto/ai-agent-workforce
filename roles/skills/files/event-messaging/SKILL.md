---
name: event-messaging
description: Reference knowledge for messaging and event streaming on NATS JetStream — the platform's standard event backbone (SQS/SNS/EventBridge equivalent). Core NATS, JetStream streams and consumers, key-value and object stores, event-driven microservice patterns (publishers, listeners, outbox, idempotent consumers), streaming ingestion, and CDC. Load this BEFORE designing, implementing, or reviewing anything that publishes, consumes, or streams events or messages.
---

# Event Messaging & Streaming Reference

NATS JetStream is the standard messaging and event-streaming backbone on this platform
(the SQS/SNS/EventBridge equivalent — internal cluster only). Kafka and RabbitMQ are
NOT used here. Load this skill before any work that publishes, consumes, or streams events.

## Core NATS

- **Subjects**: hierarchical, dot-separated (`orders.created`, `orders.*`, `orders.>`); design subject taxonomies up front — they are the API
- **Request-Reply**: synchronous RPC over NATS with timeouts; good for internal service queries without HTTP overhead
- **Queue Groups**: competing consumers — members of the same group share the load, each message delivered to one member; the unit of horizontal scaling for workers
- **Fan-out Pub/Sub**: subscribers without a queue group each receive every message

## JetStream (Persistence Layer)

- **Streams**: persisted, replayable message logs bound to subject filters; retention by limits (age, size, msgs), interest, or work-queue policy
- **Consumers**:
  - *Pull consumers* (preferred for workers): explicit fetch, natural backpressure, horizontal scaling
  - *Push consumers*: server-initiated delivery to a subject
  - Durable vs ephemeral; `DeliverPolicy` (all, last, new, by start time/sequence)
- **Acknowledgement**: `AckExplicit` for work queues; `ack`, `nak` (with delay for backoff), `term` (poison messages), `inProgress` (extend ack window)
- **Redelivery & DLQ pattern**: `MaxDeliver` caps attempts; on exhaustion JetStream emits a `$JS.EVENT.ADVISORY.CONSUMER.MAX_DELIVERIES` advisory — subscribe to it and route the failed message to a dead-letter stream
- **Exactly-once-style dedup**: publish with a `Nats-Msg-Id` header; the stream's duplicate window (default 2 min) drops re-publishes — combine with idempotent consumers for end-to-end safety
- **Key-Value Store**: stream-backed KV buckets — config, feature flags, coordination, watch for changes
- **Object Store**: chunked large-payload storage over JetStream (small artifacts; use MinIO for real object storage)
- **Replication**: R3 streams for HA on multi-node clusters; placement by tags

## Event-Driven Microservice Patterns

Per the [/microservice-template](../microservice-template/SKILL.md) layout, inbound handlers
live in the service module's `listener/` package and outbound emitters in `publisher/`.

- **Outbox pattern** (standalone microservices): write the event to an outbox table in the same DB transaction as the state change; a relay publishes from the outbox to JetStream — never publish to the broker inside a transaction directly. **In Spring Modulith projects the event publication registry IS the outbox** — publish application events and externalize with `@Externalized` per [/modulith-template](../modulith-template/SKILL.md); do NOT build a second outbox table
- **Idempotent consumers**: treat every delivery as possibly-duplicate; dedupe on business key or `Nats-Msg-Id`, make handlers safe to replay
- **Event payloads**: versioned, additive schema evolution (never repurpose fields); include event id, type, version, occurred-at, and aggregate id; JSON by default, CloudEvents envelope where interop matters
- **Choreography vs orchestration**: prefer choreography (services react to events) for loose coupling; use an orchestrator (Temporal, or a saga in the service layer) when a flow needs central error handling and compensation
- **Ordering**: per-subject ordering is preserved within a stream; partition by aggregate id in the subject (`orders.created.<region>`) when strict per-entity ordering matters
- **Slim notifications at the boundary**: every feature that changes a stateful, externally visible resource publishes a slim event notification (event_id, event_type, resource_type, resource_id, resource_version, occurred_at, link — never state) on successful processing, after commit. External consumers fetch current state from the linked endpoint (notify-then-fetch); out-of-order delivery is harmless because the fetch is always current and resource_version lets consumers skip stale work
- **Rich events inside**: within a modulith (and between platform-internal services), events are rich domain events carrying the data consumers need. Thin-event-plus-refetch is for crossing the platform boundary, not for internal choreography

## Client Usage

- **Java**: `jnats` client; Spring integration via NATS Spring Boot starter or a thin `@Configuration` wrapper; consumers as beans in `listener/`, publishers in `publisher/`; virtual threads pair well with pull-consumer fetch loops
- **Python** (data work): `nats-py` with asyncio; pull subscriptions for batch ingestion workers
- **Testing**: Testcontainers `nats:latest` with JetStream enabled (`-js`) for integration tests; assert on stream state, redeliveries, and dedup behavior

## Streaming Ingestion & CDC

- **Change Data Capture**: Debezium (PostgreSQL logical decoding, MongoDB change streams) — run Debezium Server with the NATS JetStream sink to stream row-level changes into streams; use for replication, event sourcing from legacy tables, cache invalidation, and feeding analytics
- **Ingestion pipelines**: JetStream pull consumers batch-fetch → transform → land in PostgreSQL or MinIO (Parquet); checkpoint by stream sequence for resumability; watermark on event time for late data
- **Replay**: re-create a consumer with `DeliverPolicy: all` (or by start time) to rebuild projections or backfill analytics — design downstream sinks to be replay-safe (idempotent upserts)

## Operational Notes

- NATS runs inside the cluster only — no public exposure; service-to-service auth via accounts/credentials managed as sealed secrets
- Monitor with the NATS Prometheus exporter: consumer lag (pending count), redelivery rate, stream bytes/msgs vs limits — alert on lag growth and max-deliveries advisories (see [/observability](../observability/SKILL.md))
- Capacity: set stream limits explicitly; unbounded streams are an outage waiting to happen

Other ecosystems: Kafka topics/consumer-groups and RabbitMQ queues/exchanges map onto the same
patterns (streams/queue-groups here) — translate the concepts, but NATS JetStream is the standard
on this platform.

## Related Skills

- [/sandpipers-platform](../sandpipers-platform/SKILL.md) — the platform service map (NATS is the SQS/SNS/EventBridge equivalent)
- [/microservice-template](../microservice-template/SKILL.md) — where listeners and publishers live in a service
- [/data-stores](../data-stores/SKILL.md) — the stores ingestion pipelines land in
- [/observability](../observability/SKILL.md) — monitoring consumers, lag, and redeliveries
