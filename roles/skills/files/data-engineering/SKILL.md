---
name: data-engineering
description: Reference knowledge for data engineering on the platform stack — Python data tooling (Polars, Pandas, dbt, Great Expectations), orchestration (Airflow, Prefect, Dagster, Temporal), the PostgreSQL + MinIO analytics substrate, advanced SQL, data modeling (Kimball, Data Vault, OBT), pipeline quality standards, governance and lineage, and pipeline testing. Load this BEFORE designing, implementing, or reviewing any data pipeline, transformation, or analytics work. Streaming/CDC lives in event-messaging; storage engines in data-stores.
---

# Data Engineering Reference

Reference knowledge for building scalable, reliable data pipelines and analytics infrastructure. Load this skill before designing, implementing, or reviewing data pipelines, warehouses, or transformations.

## Processing on the Platform

The analytics substrate is **PostgreSQL + MinIO (Parquet)** with **NATS JetStream** as the
streaming backbone — there is no Spark/Kafka cluster here.

- **Batch**: Python jobs (Polars/Pandas/PyArrow) run as Kubernetes Jobs/CronJobs; transform in-warehouse with dbt against PostgreSQL wherever possible — move compute to the data
- **Streaming**: JetStream pull consumers (`nats-py`) batch-fetch → transform → land in PostgreSQL or MinIO Parquet; checkpoint by stream sequence, watermark on event time (details: [/event-messaging](../event-messaging/SKILL.md))
- **Stateful processing**: keep state in PostgreSQL or JetStream KV, not in process memory; design every stage replay-safe (idempotent upserts)
- **Ad-hoc analytics on the lake**: DuckDB reads Parquet on MinIO directly (S3 endpoint override) — fast local analytics without a warehouse cluster

**Other ecosystems** (when working outside this platform): Spark (DataFrame API, AQE, broadcast joins), Flink (true streaming, watermarks, exactly-once checkpoints), and Kafka Streams (KTables, windowing) map onto the same batch/stream/state concepts; warehouses like Snowflake/BigQuery/Redshift replace the PostgreSQL+MinIO substrate. Translate the patterns, don't import the infrastructure.

## Data Orchestration & Workflow

### Apache Airflow

- **DAGs**: Directed Acyclic Graphs for workflow orchestration
- **Operators**: PythonOperator, BashOperator, KubernetesPodOperator, custom operators
- **Sensors**: File sensors, time sensors, external task sensors
- **XComs**: Cross-communication between tasks
- **Dynamic DAGs**: Programmatically generated workflows
- **Executors**: Local, Celery, Kubernetes, Dask for distributed execution
- **Best Practices**: Idempotent tasks, retry logic, alerting, task dependencies

### Modern Alternatives

- **Prefect**: Hybrid execution, cloud orchestration, dynamic workflows
- **Dagster**: Software-defined assets, data lineage, type system
- **Temporal**: Durable execution, workflow-as-code, long-running workflows

## Warehouse & Lake on the Platform

- **Warehouse**: PostgreSQL is the analytical store — schemas per layer (staging → marts), materialized views for expensive aggregates, partitioning for large fact tables; dbt manages the transformation DAG
- **Lake**: MinIO with raw → processed → curated zones, Parquet (columnar) as the standard format, Avro where schema evolution matters, Hive-style partitioning (`year=2026/month=06/day=12`), lifecycle policies on transient zones — store details in [/data-stores](../data-stores/SKILL.md)
- **Table formats** (when a lakehouse is warranted): Apache Iceberg is the engine-agnostic choice (ACID, schema evolution, time travel); Delta Lake and Hudi are Spark-ecosystem equivalents

## SQL & Query Engines

### SQL Mastery (Mandatory)

- **Advanced SQL**: CTEs, window functions, recursive queries, lateral joins
- **Query Optimization**: Explain plans, indexing, partitioning, query rewriting
- **Database-Specific**: PostgreSQL (JSONB, arrays, CTEs), MySQL (optimizer hints), BigQuery (arrays, structs)
- **Performance Tuning**: Avoid N+1 queries, batch operations, materialized views

### Distributed Query Engines

- **Trino (formerly Presto)**: Federated queries across multiple data sources
- **Apache Drill**: Schema-free SQL, query files directly (Parquet, JSON, CSV)
- **Dremio**: Data lakehouse platform, reflections (materialized views), data virtualization

## Python for Data Engineering

### Core Libraries

- **Pandas**: DataFrame manipulation, data cleaning, aggregation (slower for large data)
- **Polars**: Fast DataFrame library (Rust-based), lazy evaluation, parallel execution
- **Dask**: Parallel computing, distributed DataFrames (scales Pandas)
- **PySpark**: Distributed data processing with Spark
- **PyArrow**: Columnar data format, zero-copy reads, Parquet I/O

### Data Transformation

- **dbt (data build tool)**: SQL-based transformations in the warehouse; Jinja templating, macros, tests, documentation; incremental models, snapshots (slowly changing dimensions); lineage and dependency graphs; version control for analytics code
- **SQLMesh**: dbt alternative with Python support, efficient incremental processing

### Data Quality & Validation

- **Great Expectations**: Data validation framework, expectations, data docs
- **Pandera**: DataFrame schema validation (Pandas, Polars)
- **Deequ**: Data quality validation on Spark (AWS)
- **Soda**: Data quality monitoring, anomaly detection

## Data Ingestion & Integration

- **Streaming ingestion and CDC** run over NATS JetStream (Debezium → JetStream, pull-consumer pipelines, replay, checkpointing) — the full reference lives in [/event-messaging](../event-messaging/SKILL.md) and is shared with backend services
- **Batch ETL/ELT connectors**: Airbyte (open-source, 300+ connectors) for third-party sources; Apache NiFi for visual flow when warranted; managed equivalents (Fivetran, Stitch) only outside the platform
- **Ingestion rules**: land raw data immutably (MinIO raw zone) before transforming; schema-validate at the boundary; track source watermarks for incremental loads

## Data Modeling

### Dimensional Modeling (Kimball)

- **Fact Tables**: Measures, metrics, additive/semi-additive/non-additive
- **Dimension Tables**: Descriptive attributes, slowly changing dimensions (SCD Type 1, 2, 3)
- **Star Schema**: Fact table + dimension tables (denormalized)
- **Snowflake Schema**: Normalized dimensions (less common)
- **Conformed Dimensions**: Shared dimensions across fact tables

### Data Vault 2.0

- **Hubs**: Business keys (customers, products)
- **Links**: Relationships between hubs (orders linking customers and products)
- **Satellites**: Descriptive attributes, historical changes
- **Use Cases**: Agile data warehousing, audit trail, flexible schema

### One Big Table (OBT)

- **Denormalization**: Wide tables for analytics, avoid joins
- **Use Cases**: BI tools, ad-hoc queries, simplicity over normalization
- **Trade-offs**: Storage cost vs query performance

## Performance Optimization

### Query Optimization

- **Partitioning**: Reduce data scanned (date partitions, hash partitions)
- **Clustering/Bucketing**: Co-locate related data, optimize joins
- **Compression**: Snappy, gzip, zstd for storage and I/O reduction
- **Predicate Pushdown**: Filter early, reduce data movement
- **Broadcast Joins**: Small table replicated to all nodes (Spark)
- **Columnar Storage**: Read only needed columns (Parquet, ORC)

### Data Pipeline Optimization

- **Incremental Processing**: Process only new/changed data (watermarks, checkpoints)
- **Parallel Execution**: Partition data, parallelize tasks
- **Caching**: Cache intermediate results, avoid recomputation
- **Batch Size**: Tune batch sizes for throughput vs latency
- **Resource Allocation**: CPU, memory, executors tuning

## Data Governance & Lineage

### Data Cataloging

- **Apache Atlas**: Metadata management, lineage, classification
- **Amundsen**: Data discovery, metadata search (Lyft)
- **DataHub**: Metadata platform, lineage, data quality (LinkedIn)
- **AWS Glue Data Catalog / GCP Data Catalog**: Managed catalogs

### Data Lineage

- **Column-Level Lineage**: Track data flow from source to destination
- **Impact Analysis**: Understand downstream effects of schema changes
- **dbt Lineage**: Automatic lineage from dbt models

### Data Privacy & Compliance

- **GDPR**: Right to erasure, data minimization, consent
- **CCPA**: California Consumer Privacy Act
- **PII Detection**: Identify and mask personally identifiable information
- **Data Anonymization**: k-anonymity, differential privacy

## Data Quality & Pipeline Standards

- **Data quality dimensions**: completeness (no missing critical data), accuracy (matches source of truth), consistency (conforms to business rules), timeliness (fresh and up-to-date), validity (conforms to schema and constraints), uniqueness (no duplicates unless intentional)
- **Idempotency**: rerunnable pipelines produce the same result; upsert/merge logic (insert if not exists, update if exists); checkpointing to resume from failure; no side effects that can't be repeated safely
- **Monitoring & Alerting**: pipeline metrics (rows processed, duration, failures, data lag); data quality metrics (null rate, duplicate rate, schema drift); SLAs defined and monitored (e.g., data fresh within 1 hour); alert on failures, SLA violations, and data quality issues via Prometheus/Grafana/AlertManager (see [/observability](../observability/SKILL.md))
- **Documentation**: data dictionary (column definitions, data types, business meaning); pipeline docs (what it does, dependencies, schedule, owner); dbt auto-generated docs with lineage; runbooks for troubleshooting and incident response

## Testing Data Pipelines

- **Unit**: pytest — test transformation logic as pure functions (input → expected output)
- **Integration**: Testcontainers (real DB), schema validation, row count assertions
- **Data Quality (dbt)**: `not_null`, `unique`, `relationships`, `accepted_values`, custom business rule tests
- **Freshness**: data not older than X hours

## Pipeline Review Checklist

- [ ] Idempotent pipeline (safe to rerun)?
- [ ] Incremental processing for large datasets (not full refresh)?
- [ ] Partitioning and clustering for query performance?
- [ ] Data quality tests (schema, null checks, uniqueness)?
- [ ] Error handling and retry logic?
- [ ] Monitoring and alerting configured?
- [ ] Documentation (data dictionary, pipeline docs)?
- [ ] SQL optimized (avoid SELECT *, use CTEs, proper joins)?
- [ ] Secrets not hardcoded (use secret managers)?
- [ ] Schema evolution handled (backward compatibility)?
- [ ] Data lineage tracked (manual or automatic)?
- [ ] Test coverage for transformations?
- [ ] Cost optimization (partitioning, compression, spot instances)?
- [ ] SLA defined and monitored?
- [ ] Data privacy compliance (PII handling, GDPR)?

## Related Skills

- [/event-messaging](../event-messaging/SKILL.md) — NATS JetStream streaming, CDC, ingestion pipelines (shared with backend)
- [/data-stores](../data-stores/SKILL.md) — PostgreSQL, MinIO, Redis, MongoDB specifics
- [/observability](../observability/SKILL.md) — pipeline metrics, freshness SLOs, alerting
- [/sandpipers-platform](../sandpipers-platform/SKILL.md) — the platform service map
- [/test-plan](../test-plan/SKILL.md) — produce a structured test plan before writing pipeline tests
- [/db-migration-review](../db-migration-review/SKILL.md) — review schema migrations for safety, reversibility, and performance impact
- [/threat-model](../threat-model/SKILL.md) — threat modeling for pipelines handling PII or sensitive data
