# ADR-0002: Align infrastructure guidance with Pulumi Java

- Status: Accepted for shared guidance alignment only
- Date: 2026-10-07
- Decider: Muhammad Hamadto
- Tracking: [Shortcut 688](https://app.shortcut.com/sandpipers/story/688)

## Context

Shared rules prescribed CDKTF. The owner selected Pulumi Java for
[epic 439](https://app.shortcut.com/sandpipers/epic/439) and directed correction of contradicting docs.
Sonar integration for sandpipers-iac is deferred.

## Decision

Java infrastructure uses Pulumi and shared sandpipers-iac constructs; CDKTF is excluded.
Ansible remains responsible for private/homelab host automation. Cloud resources use reviewed CI
preview/apply, owned object-storage state and environment-specific KMS secrets providers.
Kubernetes programs use render-only providers without cluster credentials or API access and commit
manifests for ArgoCD reconciliation. Renderer engine execution may update owned state; it does not
authorise Kubernetes API writes. Helm uses Chart rendering rather than Release.

Template guidance records story 492's Maven-built Java binary convention. The feasibility spike must
verify executable configuration before deployment. This ADR does not declare the spike GO, accept
story 491's technical ADR or bypass prerequisites.

## Consequences and deployment

Update canonical instructions, infrastructure personas and four affected reference skills.
Preserve application module boundaries, security rules, model choices, authentication, MCP and client
configuration. Keep historical changelog entries and generic scanner capabilities.

Use the scoped playbook with check mode first:

```sh
ansible-playbook deploy-pulumi-guidance.yml --limit local --check
ansible-playbook deploy-pulumi-guidance.yml --limit local
```

The playbook uses the existing guarded instructions role and copies only reviewed guidance files.
It refuses unfamiliar content, redirected ancestors and multiply linked guidance before writes.
It does not invoke full client roles, download skills, change settings or install packages.
Restart existing CLI sessions to reload instructions and specialist definitions.
