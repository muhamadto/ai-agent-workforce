---
name: sandpipers-platform
description: The canonical service map for the sandpipers.io private cloud (K3S) — which platform service to use in place of each AWS managed service (PostgreSQL/Redis not RDS, NATS JetStream not SQS/SNS, Keycloak not Cognito, MinIO not S3, Kong, ArgoCD, Longhorn, OpenFaaS) and how to reach it. Load this whenever building, deploying, or wiring anything that runs on the private cloud, or choosing the platform equivalent of a managed cloud service.
---

# Sandpipers Platform Reference

Everything deployed here runs on the private K3S cloud (domain `sandpipers.io`, IaC at
`~/Workspace/private-cloud`). Designs are expressed in AWS-service terms but implemented
with these equivalents. Load this skill before wiring any service to platform infrastructure.

## AWS Service Equivalents

| AWS Service | Private Cloud Equivalent | Access |
|-------------|-------------------------|--------|
| **RDS** | PostgreSQL + Redis | Internal cluster only |
| **DynamoDB** | MongoDB | Internal cluster only |
| **S3** | MinIO (object storage) | API: https://api.minio.sandpipers.io (Tailscale) |
| **SQS/SNS/EventBridge** | NATS JetStream | Internal cluster only |
| **Lambda** | OpenFaaS | https://faas.sandpipers.io (Tailscale) |
| **Cognito** | Keycloak | https://auth.sandpipers.io (Tailscale) |
| **IAM** | Kubernetes RBAC | Built-in (ServiceAccounts, Roles, RoleBindings) |
| **API Gateway** | Kong | Public: api.sandpipers.io via Cloudflare tunnel |
| **CodePipeline** | ArgoCD | https://argocd.sandpipers.io (Tailscale) |
| **CloudWatch Logs** | Grafana Loki | https://grafana.sandpipers.io (Tailscale) |
| **CloudWatch Metrics** | Prometheus/Grafana | https://prometheus.sandpipers.io (Tailscale) |
| **ELB** | MetalLB (internal) + Cloudflare tunnel (public) | Kong: 192.168.4.202 (internal) |
| **EBS** | Longhorn (block storage) | https://longhorn.sandpipers.io (Tailscale) |

## How to Use Each Equivalent

- **Data**: PostgreSQL for relational, Redis for cache/sessions, MongoDB for documents — all internal-cluster only, no managed-database assumptions (you own pooling, backups, migrations). Details: [/data-stores](../data-stores/SKILL.md).
- **Object storage**: MinIO via standard S3 SDKs with an endpoint override (`api.minio.sandpipers.io`) and path-style access; presigned URLs and lifecycle policies work as on S3.
- **Messaging/eventing**: NATS JetStream for every queue, topic, and event-bus need — never introduce SQS/SNS/Kafka/RabbitMQ patterns that assume those brokers. Details: [/event-messaging](../event-messaging/SKILL.md).
- **Functions**: OpenFaaS for event-triggered or bursty function workloads instead of Lambda.
- **Identity**: Keycloak is the OIDC provider (`auth.sandpipers.io`) — authorization code + PKCE against its realms; service identity inside the cluster is Kubernetes ServiceAccounts + RBAC, not IAM roles. Auth rules: [/auth-engineering](../auth-engineering/SKILL.md).
- **Ingress & exposure**: Kong is the API gateway. Public exposure happens ONLY through the Cloudflare tunnel to `api.sandpipers.io`; everything else (dashboards, staging APIs) is Tailscale-only. Internal LoadBalancer IPs come from MetalLB (Kong at 192.168.4.202). Traefik handles cluster ingress with cert-manager TLS (wildcard `*.sandpipers.io`).
- **Deployment**: GitOps via ArgoCD — changes are committed to the repo and synced; no `kubectl apply` deployments, no clickops. Cluster changes go through the Ansible code in `~/Workspace/private-cloud`.
- **Storage**: PVCs use the Longhorn StorageClass; size deliberately and set backup/snapshot expectations per volume.
- **Observability**: Prometheus/Grafana for metrics, Loki for logs, AlertManager for alerts. Details: [/observability](../observability/SKILL.md).
- **Secrets**: Sealed Secrets committed to git — never plaintext secrets in manifests or values files.

## Platform Rules

1. **Tailscale-first**: every dashboard and non-public endpoint requires Tailscale; never expose a service publicly except through the Cloudflare tunnel + Kong path.
2. **NetworkPolicies are enforced** — new services must declare their ingress/egress; assume deny-by-default posture.
3. **Everything as code**: infrastructure via Ansible/`private-cloud` repo, app deployment via ArgoCD, service infra via CDKTF Java (the [/microservice-template](../microservice-template/SKILL.md) and [/modulith-template](../modulith-template/SKILL.md) infra modules).
4. **Resource limits required**: K3S runs on constrained hardware — set requests/limits on every workload; unbounded workloads are rejected.

## Related Skills

- [/data-stores](../data-stores/SKILL.md) · [/event-messaging](../event-messaging/SKILL.md) · [/observability](../observability/SKILL.md) — the deep references behind this map
- [/auth-engineering](../auth-engineering/SKILL.md) — Keycloak/OIDC integration rules
- [/infrastructure-engineering](../infrastructure-engineering/SKILL.md) — cloud + Kubernetes engineering reference
- [/microservice-template](../microservice-template/SKILL.md) — the service layout deployed onto this platform
