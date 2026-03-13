---
name: oauth-threat-model
description: Produce a focused threat model for OAuth2/OIDC authorization flows covering PKCE, token endpoints, redirect URIs, scope creep, and token theft vectors.
---

# OAuth Threat Model Skill

Produce a structured threat model specifically for OAuth2 and OIDC authorization flows. Use this skill before implementing or changing any authorization flow, client registration, or token endpoint.

## When to use

- Adding or modifying an OAuth2 authorization flow (authorization code, client credentials, device flow)
- Integrating a new identity provider (social login, enterprise SSO)
- Adding a new OAuth2 client (mobile app, SPA, service account)
- Changing token endpoint configuration, scopes, or redirect URIs
- After a security incident involving token theft or authorization bypass

---

## Step 1 — Define the OAuth2 context

State clearly:

- **Flow type**: Authorization Code + PKCE / Client Credentials / Device Flow / Refresh Token
- **Client type**: Public (SPA, mobile) / Confidential (server-side)
- **Identity provider**: Spring Authorization Server / Keycloak / Auth0 / Okta / Google / custom
- **Resources being protected**: API endpoints, data, admin operations
- **Actors**: End user, OAuth2 client application, authorization server, resource server, external IdP
- **Token types in use**: Access token (JWT / opaque), ID token (OIDC), refresh token

---

## Step 2 — Draw the OAuth2 data flow

```
[User-Agent / Browser]
    │
    ▼  GET /authorize?response_type=code&client_id=...&redirect_uri=...&state=...&code_challenge=...
[Authorization Server]
    │
    ▼  302 Location: redirect_uri?code=AUTH_CODE&state=...
[Client Application]
    │
    ▼  POST /token { code, code_verifier, client_id, redirect_uri }
[Authorization Server]
    │
    ▼  { access_token, refresh_token, id_token }
[Client Application]
    │
    ▼  GET /api/resource  Authorization: Bearer <access_token>
[Resource Server]
```

Adapt the diagram to the actual flow being modelled. Include all redirect hops, token storage locations, and inter-service token relay.

---

## Step 3 — STRIDE analysis for OAuth2 attack surface

Apply STRIDE to each component and data flow arrow in your diagram.

### Authorization endpoint (`/authorize`)

| Threat | STRIDE | Attack vector | Mitigation |
|--------|--------|--------------|------------|
| Open redirect | S, I | `redirect_uri` not exactly matched; wildcard or partial match allows attacker to steal auth code | Exact URI match, no wildcards, no path traversal |
| CSRF on authorization request | S | Missing or predictable `state` parameter | Cryptographically random `state` tied to session |
| Authorization code interception | S | Code intercepted in redirect (e.g., referrer header, log, browser history) | PKCE mandatory; short code lifetime (< 5 min) |
| Mix-up attack | S, EoP | Attacker substitutes a different issuer's authorization endpoint | Validate `iss` in authorization response (RFC 9207) |

### Token endpoint (`/token`)

| Threat | STRIDE | Attack vector | Mitigation |
|--------|--------|--------------|------------|
| Authorization code replay | S | Stolen code reused before expiry | Single-use codes; detect replay → revoke all tokens |
| PKCE bypass | S, EoP | Server does not enforce `code_verifier` validation | Always validate `code_verifier` against `code_challenge` |
| Client impersonation | S | Weak client authentication (none, plain secret in URL) | `private_key_jwt` for confidential clients; PKCE for public |
| Token farming | DoS | Automated requests to exhaust token quota | Rate limit per client_id and IP; anomaly detection |
| Credential stuffing on ROPC | S | Resource Owner Password Credentials flow leaks credentials | Never implement ROPC; use authorization code flow |

### Access token (in transit and at rest)

| Threat | STRIDE | Attack vector | Mitigation |
|--------|--------|--------------|------------|
| Token theft from storage | I | Access token in localStorage / sessionStorage exposed via XSS | HttpOnly cookie or secure storage; short TTL |
| Token theft in transit | I | HTTPS not enforced; token leaked in logs or headers | HSTS; never log tokens; use `Authorization` header not query param |
| Token replay | S | Stolen access token reused within TTL window | Short TTL (≤ 15 min); DPoP binding for high-value resources |
| Audience confusion | EoP | Token intended for service A accepted by service B | Validate `aud` claim at every resource server |
| Scope escalation | EoP | Client requests broader scopes than needed | Enforce least-privilege scopes; resource server validates scopes |

### Refresh token

| Threat | STRIDE | Attack vector | Mitigation |
|--------|--------|--------------|------------|
| Refresh token theft | S, I | Plaintext refresh token stored in database or log | Store hashed; never log; revoke on breach |
| Refresh token replay | S | Stolen refresh token used to obtain new access tokens | Rotation on every use; detect reuse → revoke entire family |
| Infinite session via refresh | EoP | No maximum lifetime on refresh token chain | Absolute expiry (e.g., 30 days) regardless of activity |

### Redirect URI

| Threat | STRIDE | Attack vector | Mitigation |
|--------|--------|--------------|------------|
| Open redirect code theft | S | `redirect_uri` allows off-domain redirect | Allowlist exact URIs; reject any URI not pre-registered |
| Subdomain takeover | S | Pre-registered URI points to expired subdomain taken over by attacker | Audit registered redirect URIs; remove stale URIs |
| Localhost URI on production | I | Redirect to localhost accepted in production environments | Disable localhost URIs outside development environments |

### OIDC-specific

| Threat | STRIDE | Attack vector | Mitigation |
|--------|--------|--------------|------------|
| ID token replay | S | ID token from one session accepted in another | Validate `nonce` claim; bind nonce to session |
| Issuer substitution | S | Attacker serves a crafted ID token from a rogue issuer | Validate `iss` against pinned issuer URL; use discovery |
| UserInfo endpoint spoofing | S, I | Attacker returns false claims from a spoofed UserInfo endpoint | Verify `sub` in UserInfo response matches `sub` in ID token |
| Logout bypass | EoP | RP-initiated logout not implemented; session persists after token revocation | Implement RP-initiated logout; validate `id_token_hint` |

---

## Step 4 — Risk assessment

Rate each threat identified in Step 3 that applies to your specific flow:

| Threat | STRIDE | Likelihood (L/M/H) | Impact (L/M/H) | Risk | Owner |
|--------|--------|-------------------|----------------|------|-------|
| Open redirect code theft | S | Low | Critical | High | identity-security-developer |
| PKCE not enforced | S, EoP | Medium | Critical | Critical | identity-security-developer |
| Refresh token not rotated | S | Medium | High | High | backend-developer |

**Risk matrix**: High likelihood × High impact = Critical; drop one dimension = High; Low × Low = Low.

---

## Step 5 — Mitigations summary

For each Medium / High / Critical risk, specify:

| Risk | Control | Implementation | Validation |
|------|---------|---------------|------------|
| PKCE bypass | Enforce `code_verifier` server-side | Reject token requests without verifier if challenge was sent | Integration test: token request without verifier → 400 |
| Token in localStorage | Move to HttpOnly cookie | Set-Cookie with HttpOnly, Secure, SameSite=Strict | OWASP ZAP scan; manual browser inspection |
| Redirect URI wildcard | Exact URI match | Allowlist in client registration; reject partial matches | Unit test with altered redirect_uri → 400 |

---

## Step 6 — Output the threat model document

```
# OAuth2 Threat Model: <Feature / Client / Flow>

## Context
<Flow type, client type, IdP, resources protected>

## Data Flow
<Adapted diagram from Step 2>

## STRIDE Analysis
<Applicable rows from Step 3 tables>

## Risk Assessment
<Table from Step 4>

## Mitigations
<Table from Step 5>

## Residual Risks
<Accepted risks, justification, review date, owner>
```

---

## Safety rules

- A Critical risk blocks implementation until mitigated
- PKCE is mandatory for all authorization code flows — no exceptions
- Redirect URI exact match is mandatory — wildcards are never acceptable
- Refresh token rotation is mandatory — any non-rotating refresh token is a Critical finding
- Run this threat model before implementing any new OAuth2 client, not after
- Share output with secops-engineer for review before sign-off
