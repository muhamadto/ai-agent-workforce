---
name: data-stores
description: Reference knowledge for the platform's data stores — PostgreSQL (RDS equivalent), Redis (caching/sessions), MongoDB (DynamoDB equivalent), and MinIO (S3-compatible object storage) — plus migrations, connection pooling, query optimization, and caching patterns. Load this BEFORE designing schemas, writing queries, choosing a store, or implementing caching or persistence in any service or pipeline.
---

# Data Stores Reference

The platform's persistence layer: PostgreSQL + Redis (RDS equivalent), MongoDB (DynamoDB
equivalent), and MinIO (S3 equivalent) — all internal-cluster services. Load this skill
before schema design, query work, store selection, or caching.

## PostgreSQL (Primary Relational Store)

- **Advanced features**: JSONB (with GIN indexes), CTEs and recursive queries, window functions, lateral joins, partitioning (range/list/hash), full-text search, arrays
- **Indexing**: B-tree by default; GIN for JSONB/arrays/full-text; partial and covering indexes; index only what queries need — every index taxes writes
- **Query optimization**: `EXPLAIN (ANALYZE, BUFFERS)`, avoid `SELECT *`, batch writes, prevent N+1 (fetch joins / entity graphs in JPA), use `pg_stat_statements` to find hot queries
- **Logical decoding**: the CDC source for Debezium → NATS JetStream (see [/event-messaging](../event-messaging/SKILL.md))
- **Scaling**: read replicas for read-heavy loads, connection pooling always, partitioning before sharding
- **MySQL/MariaDB** (when encountered): InnoDB tuning, optimizer hints, replication — same disciplines apply

## Redis (Cache, Sessions, Coordination)

- **Data structures**: strings, hashes, sets, sorted sets, streams, bitmaps — pick the structure that matches the access pattern
- **Caching patterns**: cache-aside (default), write-through, write-behind; explicit TTLs on everything; eviction policy chosen deliberately (LRU/LFU)
- **Distributed coordination**: Redisson locks (fair, read-write) — scope them tightly; pub/sub for ephemeral signals (durable events go to NATS JetStream)
- **Sessions**: Spring Session for distributed sessions; refresh-token and session state per the [/auth-engineering](../auth-engineering/SKILL.md) rules
- **HA**: Sentinel or Cluster when it matters; treat cache loss as a performance event, not a data-loss event — never make Redis the system of record

## MongoDB (Document Store)

- **Modeling**: embed what is read together, reference what grows unboundedly; design around query patterns, not normalization instincts
- **Aggregation pipeline**: match early, project narrow, index the match/sort stages
- **Indexes**: compound indexes follow the ESR rule (equality, sort, range); cap collection scans in production
- **Transactions**: multi-document transactions exist — but needing them often signals the data belongs in PostgreSQL
- **Change streams**: per-collection CDC feed (alternative to Debezium for Mongo sources)

## MinIO (S3-Compatible Object Storage)

- Endpoint: `https://api.minio.sandpipers.io` (Tailscale-only); use standard S3 SDKs with an endpoint override and path-style access
- **Buckets & layout**: raw → processed → curated zones for data work; Hive-style partitioning (`year=2026/month=06/`) for analytics datasets
- **Formats**: Parquet for columnar analytics data, Avro where schema evolution matters
- **Presigned URLs** for time-limited upload/download without credential sharing
- **Lifecycle policies**: expire transient objects, transition cold data
- **Versioning + object lock** for immutability where audit matters

## Migrations

- **Liquibase or Flyway**, versioned and committed with the code that needs them
- Forward-only mindset with documented rollback for every destructive change; review with [/db-migration-review](../db-migration-review/SKILL.md) before applying
- Expand-and-contract for zero-downtime schema changes (add column → dual-write → migrate → drop)

## Connection Pooling

- **HikariCP**: size pools from `connections = (cores × 2) + spindles` as a starting point, not hundreds; set `maxLifetime` below server timeout; enable leak detection in non-prod
- Pool exhaustion is a symptom — look for long transactions and missing indexes before raising the ceiling

## Multi-Level Caching

- **L1**: in-process Caffeine (small, short TTL) → **L2**: Redis (shared) → store
- **Invalidation**: time-based as the baseline; event-based via NATS for correctness-critical caches
- **Stampede prevention**: per-key locking or stale-while-revalidate on hot keys
- Cache only what is expensive to compute or read — caching everything hides real performance problems

## Choosing a Store

| Need | Use |
|---|---|
| Transactional/relational data, anything with joins or constraints | PostgreSQL |
| Cache, sessions, locks, counters, ephemeral state | Redis |
| Schemaless documents with document-shaped access patterns | MongoDB |
| Files, blobs, datasets, backups, Parquet | MinIO |
| Durable events and streams | NATS JetStream ([/event-messaging](../event-messaging/SKILL.md)) |

Default to PostgreSQL when in doubt.

## Related Skills

- [/sandpipers-platform](../sandpipers-platform/SKILL.md) — the platform service map these stores belong to
- [/event-messaging](../event-messaging/SKILL.md) — CDC out of these stores, event-driven invalidation
- [/db-migration-review](../db-migration-review/SKILL.md) — review every schema migration before applying
- [/java-spring-engineering](../java-spring-engineering/SKILL.md) — Spring Data JPA/Redis usage in services
