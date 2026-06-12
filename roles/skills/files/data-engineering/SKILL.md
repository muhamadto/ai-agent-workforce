---
name: data-engineering
description: Reference knowledge for data engineering — big data processing (Spark, Flink, Kafka Streams), orchestration (Airflow, Prefect, Dagster), data warehouses (Snowflake, BigQuery, Redshift), data lakes and table formats (Delta Lake, Iceberg, Hudi), advanced SQL and query engines, Python data tooling (Pandas, Polars, dbt, Great Expectations), ingestion and CDC, data modeling (Kimball, Data Vault, OBT), performance optimization, governance and lineage, and pipeline testing. Load this BEFORE designing, implementing, or reviewing any data engineering work.
---

# Data Engineering Reference

Reference knowledge for building scalable, reliable data pipelines and analytics infrastructure. Load this skill before designing, implementing, or reviewing data pipelines, warehouses, or transformations.

## Big Data Processing

### Apache Spark

- **PySpark**: Python API for Spark, DataFrame API, SQL, structured streaming
- **Spark SQL**: Distributed SQL query engine, Catalyst optimizer
- **Spark Streaming**: Micro-batch streaming, structured streaming, stateful processing
- **Spark MLlib**: Distributed machine learning, feature engineering
- **Optimization**: Partitioning, bucketing, caching, broadcast joins, adaptive query execution (AQE)
- **Delta Lake**: ACID transactions, time travel, schema enforcement, upserts (merge)

### Apache Flink

- **Stream Processing**: True streaming (not micro-batch), event time processing, watermarks
- **State Management**: Keyed state, operator state, queryable state
- **Exactly-Once Semantics**: Checkpointing, savepoints
- **Table API & SQL**: Unified batch and stream processing
- **Use Cases**: Real-time analytics, complex event processing (CEP), stateful stream processing

### Kafka Streams

- **Stream Processing**: Lightweight library for Kafka-native stream processing
- **KTables & KStreams**: Changelog streams and event streams
- **Stateful Operations**: Aggregations, joins, windowing
- **Exactly-Once Processing**: Idempotent producers, transactional writes

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

## Data Warehousing

### Snowflake

- **Architecture**: Separation of storage and compute, multi-cluster compute
- **Features**: Zero-copy cloning, time travel, data sharing, streams, tasks
- **Optimization**: Clustering keys, materialized views, search optimization
- **Security**: Column-level encryption, masking, row access policies
- **SnowSQL & Python Connector**: CLI and programmatic access

### Google BigQuery

- **Architecture**: Serverless, columnar storage, Dremel query engine
- **Features**: Nested and repeated fields, partitioning, clustering
- **BigQuery ML**: In-database machine learning
- **Streaming Inserts**: Real-time data ingestion
- **Cost Optimization**: Partitioning, clustering, query caching, slot reservations

### Amazon Redshift

- **Architecture**: Columnar storage, MPP (massively parallel processing)
- **Features**: Distribution styles (key, all, even), sort keys, materialized views
- **Redshift Spectrum**: Query S3 data directly
- **Concurrency Scaling**: Auto-scale for query concurrency
- **Optimization**: Compression, vacuum, analyze, workload management (WLM)

## Data Lakes & Storage

### Object Storage (S3, GCS, Azure Blob)

- **Data Lake Architecture**: Raw → processed → curated zones
- **File Formats**: Parquet (columnar, compressed), ORC, Avro (schema evolution)
- **Partitioning**: Hive-style partitioning (year=2024/month=01/day=15)
- **Lifecycle Policies**: Transition to cheaper storage tiers (Glacier, Nearline)

### Delta Lake / Apache Iceberg / Apache Hudi

- **ACID Transactions**: Atomic writes, schema enforcement, time travel
- **Delta Lake**: Databricks-led, tight Spark integration
- **Apache Iceberg**: Netflix-led, engine-agnostic (Spark, Flink, Trino)
- **Apache Hudi**: Uber-led, upserts and incremental processing
- **Use Cases**: Data lakehouse architecture, streaming + batch unification

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

### Change Data Capture (CDC)

- **Debezium**: Stream database changes to Kafka (MySQL, PostgreSQL, MongoDB)
- **Maxwell**: MySQL binlog to Kafka
- **Use Cases**: Replicate databases, event sourcing, real-time analytics

### ETL/ELT Tools

- **Apache NiFi**: Visual data flow, drag-and-drop pipelines
- **Airbyte**: Open-source data integration, 300+ connectors
- **Fivetran**: Managed ELT, automated schema drift handling
- **Stitch**: Singer-based data integration

### Streaming Ingestion

- **Kafka Connect**: Source and sink connectors for Kafka
- **Kinesis Data Firehose**: AWS streaming data delivery to S3, Redshift, Elasticsearch
- **Cloud Pub/Sub to BigQuery**: GCP streaming to data warehouse

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
- **Monitoring & Alerting**: pipeline metrics (rows processed, duration, failures, data lag); data quality metrics (null rate, duplicate rate, schema drift); SLAs defined and monitored (e.g., data fresh within 1 hour); alert on failures, SLA violations, and data quality issues; tools — Datadog, Prometheus, CloudWatch, custom dashboards
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

- [/test-plan](../test-plan/SKILL.md) — produce a structured test plan before writing pipeline tests
- [/db-migration-review](../db-migration-review/SKILL.md) — review schema migrations for safety, reversibility, and performance impact
- [/threat-model](../threat-model/SKILL.md) — threat modeling for pipelines handling PII or sensitive data
