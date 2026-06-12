---
name: infrastructure-engineering
description: Reference knowledge for infrastructure engineering — AWS and GCP service catalogs, the private cloud stack at ~/Workspace/private-cloud (K3S, Traefik, Sealed Secrets, GitOps, observability), Infrastructure as Code (Terraform, Ansible, Helm, Kustomize), Kubernetes operations and security, monitoring/logging/tracing/alerting, networking and service mesh, backup and disaster recovery, security hardening, and cost optimization. Load this BEFORE designing, implementing, or reviewing any infrastructure work.
---

# Infrastructure Engineering Reference

Reference knowledge for infrastructure design, deployment, and operations across public cloud and on-premise systems. Load this skill before designing, implementing, or reviewing infrastructure.

## Amazon Web Services (AWS)

- **Compute**: EC2, ECS, EKS (Kubernetes), Lambda (serverless), Fargate
- **Storage**: S3, EBS, EFS, Glacier (archival)
- **Database**: RDS (PostgreSQL, MySQL, Aurora), DynamoDB, ElastiCache (Redis), DocumentDB
- **Networking**: VPC, subnets, route tables, NAT Gateway, Transit Gateway, Direct Connect
- **Load Balancing**: ALB (Application), NLB (Network), CLB (Classic)
- **Security**: IAM (roles, policies), Security Groups, NACLs, KMS (encryption), Secrets Manager, WAF
- **Monitoring**: CloudWatch (logs, metrics, alarms), X-Ray (tracing)
- **Infrastructure as Code**: CloudFormation, CDK (Cloud Development Kit)
- **Cost Management**: Cost Explorer, Savings Plans, Reserved Instances

## Google Cloud Platform (GCP)

- **Compute**: Compute Engine, GKE (Kubernetes), Cloud Run (serverless), Cloud Functions
- **Storage**: Cloud Storage, Persistent Disk, Filestore
- **Database**: Cloud SQL (PostgreSQL, MySQL), Firestore, Bigtable, Memorystore (Redis)
- **Networking**: VPC, subnets, Cloud NAT, Cloud Interconnect, VPN
- **Load Balancing**: HTTP(S) Load Balancer, Network Load Balancer, Internal Load Balancer
- **Security**: IAM, VPC Service Controls, Cloud KMS, Secret Manager, Cloud Armor (WAF)
- **Monitoring**: Cloud Monitoring, Cloud Logging, Cloud Trace
- **Infrastructure as Code**: Deployment Manager, Terraform

## Private Cloud Infrastructure (~/Workspace/private-cloud)

The private cloud lives at `~/Workspace/private-cloud` and includes:

- **Container Orchestration**: K3S (lightweight Kubernetes for edge/on-premise); high availability via multi-master setup with embedded etcd or external datastore; cluster management with kubectl, Helm charts, kustomize
- **Networking & Load Balancing**: Traefik (ingress controller, reverse proxy, load balancer); VPC-style network isolation, subnet management, routing; dynamic DNS for dynamic IPs; CNI plugins, network policies, service mesh
- **API Gateway & Service Mesh**: centralized API management, rate limiting, authentication; service load balancing, health checks, failover
- **Certificate Management**: automated provisioning and renewal (Let's Encrypt); TLS termination at ingress
- **Messaging & Event Streaming**: NATS, Kafka, RabbitMQ for async communication; pub/sub patterns, event sourcing
- **Databases & Persistence**: PostgreSQL, MySQL, MongoDB deployments; persistent volumes and storage classes (block storage); S3-compatible object storage (MinIO)
- **Secrets Management**: Sealed Secrets (Bitnami), external secrets operator; secrets encrypted at rest, RBAC for access control
- **Identity & Access Management**: centralized authentication, federated access, SSO
- **Observability**: Prometheus (metrics), Grafana (dashboards), Loki (logs), Jaeger (tracing); cluster health, resource usage, application metrics; AlertManager for notifications
- **GitOps & CI/CD**: ArgoCD, Flux for declarative deployments; Git-based configuration management; push-based or pull-based automated deployments
- **Serverless Functions**: OpenFaaS, Knative for serverless workloads
- **Platform Operations**: backup, restore, disaster recovery, capacity planning; custom kernel modules for specialized workloads; Portainer container management UI (optional); secure tunnels for remote access (Cloudflare Tunnel, Tailscale)

## Infrastructure as Code (IaC)

### Terraform

- **Multi-Cloud**: Provision AWS, GCP, Azure, Kubernetes resources
- **State Management**: Remote state (S3, GCS, Terraform Cloud), state locking
- **Modules**: Reusable infrastructure components
- **Workspaces**: Environment isolation (dev, staging, prod)
- **Best Practices**: Immutable infrastructure, versioned modules, automated testing
- **CDK for Terraform (CDKTF)**: programmatic infrastructure in Java — used by the microservice-template infra module

### Ansible

- **Configuration Management**: Server provisioning, application deployment
- **Idempotency**: Run multiple times without side effects
- **Inventory**: Dynamic inventories (AWS, GCP, Kubernetes)
- **Roles**: Modular, reusable playbooks
- **Secrets**: Ansible Vault for encrypted variables

### Helm

- **Kubernetes Package Manager**: Chart-based application deployment
- **Templating**: Parameterized Kubernetes manifests
- **Versioning**: Rollback to previous releases
- **Repositories**: Public (Artifact Hub) and private chart repositories

### Kustomize

- **Kubernetes Native**: Declarative customization of Kubernetes resources
- **Overlays**: Environment-specific configurations (base + overlays)
- **No Templating**: Patch-based modifications

## Kubernetes

### Core Concepts

- **Pods**: Smallest deployable units, one or more containers
- **Deployments**: Declarative updates, rolling updates, rollbacks
- **StatefulSets**: Stable network identities, persistent storage for stateful apps
- **DaemonSets**: Run on every node (logging, monitoring agents)
- **Services**: ClusterIP, NodePort, LoadBalancer for networking
- **Ingress**: HTTP/HTTPS routing, TLS termination
- **ConfigMaps & Secrets**: Configuration and sensitive data management
- **Namespaces**: Logical resource isolation

### Advanced Features

- **Horizontal Pod Autoscaler (HPA)**: Scale based on CPU, memory, custom metrics
- **Vertical Pod Autoscaler (VPA)**: Adjust resource requests/limits
- **Cluster Autoscaler**: Add/remove nodes based on demand
- **Pod Disruption Budgets**: Maintain availability during disruptions
- **Network Policies**: Firewall rules for pod-to-pod communication
- **Resource Quotas**: Limit resource consumption per namespace
- **LimitRanges**: Default and max resource limits
- **Admission Controllers**: Enforce policies (OPA, Kyverno)

### Kubernetes Security

- **RBAC**: Role-Based Access Control (Roles, ClusterRoles, RoleBindings)
- **Service Accounts**: Identity for pods, token-based authentication
- **Pod Security Standards**: Baseline, restricted, privileged policies
- **Network Policies**: Restrict network traffic between pods
- **Secrets Encryption**: Encrypt secrets at rest (etcd encryption, Sealed Secrets)
- **Image Security**: Vulnerability scanning (Trivy, Clair), signed images

## Observability & Monitoring

### Metrics (Prometheus Stack)

- **Prometheus**: Time-series metrics collection, PromQL queries
- **Grafana**: Visualization, dashboards, alerting
- **Exporters**: Node Exporter, Kube-state-metrics, application exporters
- **Service Monitors**: Prometheus Operator for service discovery
- **Recording Rules**: Pre-compute expensive queries
- **Alerting Rules**: Define alert conditions, severity levels

### Logging (ELK / Loki)

- **Elasticsearch / Logstash / Kibana**: search and analytics engine, log processing pipeline, log visualization (ELK stack)
- **Loki**: Log aggregation (lightweight, Prometheus-like); **Promtail** as log shipper
- **Fluentd/Fluent Bit**: Log collection and forwarding
- **Structured Logging**: JSON logs with consistent fields

### Tracing

- **Jaeger**: Distributed tracing, trace visualization
- **OpenTelemetry**: Vendor-neutral instrumentation (metrics, traces, logs)
- **Zipkin**: Distributed tracing (alternative to Jaeger)
- **Service Mesh Integration**: Istio, Linkerd for automatic tracing

### Alerting

- **AlertManager**: Route alerts, group, silence, inhibit
- **Notification Channels**: Email, Slack, PagerDuty, webhooks
- **Escalation Policies**: On-call rotations, escalation rules
- **Runbooks**: Documented response procedures

## Networking

### Service Mesh

- **Istio**: Traffic management, security, observability
- **Linkerd**: Lightweight service mesh, mTLS, retries, timeouts
- **Consul Connect**: Service mesh with service discovery

### Ingress Controllers

- **NGINX Ingress**: Kubernetes ingress controller, path-based routing
- **Traefik**: Dynamic ingress, Let's Encrypt integration
- **Istio Gateway**: Ingress with service mesh integration
- **Ambassador/Emissary**: API Gateway on Kubernetes

### DNS & Service Discovery

- **CoreDNS**: Kubernetes DNS, service discovery
- **ExternalDNS**: Sync Kubernetes services with DNS providers
- **Consul**: Service discovery, health checking, KV store

### Load Balancing

- **Layer 7 (Application)**: HTTP/HTTPS routing, content-based routing
- **Layer 4 (Network)**: TCP/UDP load balancing
- **Global Load Balancing**: Multi-region traffic distribution
- **Session Affinity**: Sticky sessions for stateful apps

## Backup & Disaster Recovery

- **Backup Strategies**: Full, incremental, differential backups
- **Retention Policies**: Define how long to keep backups (7 days, 30 days, 1 year)
- **Backup Tools**: Velero (Kubernetes), Restic, Borg, cloud-native backups
- **Offsite Backups**: Geographic redundancy, cloud storage (S3, GCS)
- **Restore Testing**: Regularly test restore procedures
- **RPO (Recovery Point Objective)**: Maximum acceptable data loss
- **RTO (Recovery Time Objective)**: Maximum acceptable downtime
- **Disaster Recovery Plan**: Documented procedures, runbooks, contact info

## Security Best Practices

- **Principle of Least Privilege**: Minimal IAM permissions, RBAC roles
- **Network Segmentation**: VPCs, security groups, network policies
- **Encryption**: At rest (disk encryption, KMS) and in transit (TLS 1.2+)
- **Secrets Management**: Vault, Sealed Secrets, cloud secret managers (AWS Secrets Manager, GCP Secret Manager)
- **Vulnerability Scanning**: Container images (Trivy), infrastructure (Checkov, Terrascan)
- **Patch Management**: Regular updates, automated patching (when safe)
- **Access Control**: MFA, SSO, IP whitelisting, VPN
- **Audit Logging**: CloudTrail (AWS), Cloud Audit Logs (GCP), Kubernetes audit logs
- **Compliance**: CIS benchmarks, SOC 2, ISO 27001, PCI DSS
- **Zero Trust / Defense in Depth**: never trust, always verify; multiple layers of security; secrets never in code

## Cost Optimization

- **Right-Sizing**: Match resources to actual usage (not over-provisioned)
- **Auto-Scaling**: Scale up/down based on demand
- **Spot/Preemptible Instances**: Use for fault-tolerant workloads (70-90% cost savings)
- **Reserved Instances/Savings Plans**: Commit to long-term usage for discounts
- **Storage Lifecycle Policies**: Move old data to cheaper tiers (S3 Glacier, Nearline)
- **Idle Resource Detection**: Shut down unused instances, delete orphaned volumes
- **Cost Monitoring**: Set budgets, alerts for cost anomalies
- **Tagging**: Resource tagging for cost allocation by team, project, environment

## Reliability & Scalability Design Principles

- **High Availability**: Multi-AZ (AWS), multi-zone (GCP), multi-master (Kubernetes)
- **Fault Tolerance**: Survive failures at the node, AZ, and region level
- **Health Checks**: Liveness and readiness probes (Kubernetes), ELB health checks
- **Graceful Degradation**: Partial functionality over complete failure
- **Circuit Breakers**: Prevent cascading failures (Resilience4j, Istio)
- **Horizontal Scaling**: Add more instances, not bigger instances
- **Stateless Applications**: Store state externally (database, cache, object storage)
- **Caching**: Reduce load on databases (Redis, CDN)
- **Asynchronous Processing**: Decouple with message queues (Kafka, NATS, RabbitMQ)
- **Database Scaling**: Read replicas, sharding, caching
- **Immutable Infrastructure**: Replace, don't modify — destroy and recreate

## Infrastructure Review Checklist

- [ ] Infrastructure declared as code (Terraform, Ansible, Helm)?
- [ ] No manual changes (clickops prohibited)?
- [ ] High availability configured (multi-AZ, multi-zone, multi-master)?
- [ ] Backup and restore procedures defined and tested?
- [ ] Monitoring, logging, alerting configured?
- [ ] Security groups / network policies restrict access (least privilege)?
- [ ] Secrets managed securely (Vault, Sealed Secrets, cloud secret managers)?
- [ ] Encryption at rest and in transit (TLS 1.2+, KMS)?
- [ ] Auto-scaling configured for variable load?
- [ ] Cost optimization applied (right-sizing, spot instances, lifecycle policies)?
- [ ] Resource tagging for cost allocation and compliance?
- [ ] Disaster recovery plan documented (RTO, RPO)?
- [ ] Health checks configured (liveness, readiness)?
- [ ] Rollback plan documented and tested?
- [ ] Compliance requirements met (CIS benchmarks, SOC 2, PCI DSS)?

## Related Skills

- [/microservice-template](../microservice-template/SKILL.md) — the mandatory microservice layout; its infra module uses CDK for Terraform (CDKTF, Java)
- [/threat-model](../threat-model/SKILL.md) — STRIDE threat modeling for new infrastructure or changed trust boundaries
- [/incident](../incident/SKILL.md) — incident response and blameless postmortems
- [/adr](../adr/SKILL.md) — record significant infrastructure architecture decisions
