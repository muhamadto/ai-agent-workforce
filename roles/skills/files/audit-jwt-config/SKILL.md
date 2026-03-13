---
name: audit-jwt-config
description: Audit a JWT implementation for algorithm confusion, claims validation gaps, insecure storage, and token lifecycle weaknesses.
---

# Audit JWT Config Skill

Audit an existing JWT implementation against known attack vectors and RFC best practices. Use this before merging any auth change that touches token issuance, validation, or storage.

## When to use

- Reviewing a JWT decoder/encoder configuration before merge
- Auditing an existing auth implementation for security regressions
- After upgrading a security library that handles JWT (Spring Security, nimbus-jose-jwt, jsonwebtoken, etc.)
- When a security finding or CVE touches the token validation path

---

## Step 1 — Locate JWT configuration

```bash
# Spring Security
grep -rn "JwtDecoder\|JwtEncoder\|NimbusJwtDecoder\|NimbusJwtEncoder" src/
grep -rn "oauth2ResourceServer\|jwt(" src/
grep -rn "jwk-set-uri\|issuer-uri\|public-key-location" src/main/resources/

# Node / TypeScript
grep -rn "jsonwebtoken\|jose\|jwt\.verify\|jwt\.sign" src/
grep -rn "algorithms\|issuer\|audience" src/

# Python
grep -rn "jwt\.decode\|jwt\.encode\|PyJWT\|python-jose" .
```

---

## Step 2 — Algorithm confusion check

**Critical.** Algorithm confusion is the most exploited JWT vulnerability.

| Finding | Risk |
|---------|------|
| `alg: none` accepted | Critical — no signature verification |
| HS256 used in distributed system | High — shared secret leakage |
| Algorithm not explicitly configured (accept-all) | High — confusion attack |
| RS256/ES256 public key also used as HMAC secret | Critical |

**Check:**

```bash
# Java — check for algorithm pinning
grep -rn "JwsAlgorithms\|RS256\|ES256\|HS256" src/
grep -rn "withAlgorithm\|setAllowedAlgorithms\|setSupportedAlgorithms" src/

# Node — check algorithms array is restricted
grep -rn "algorithms:" src/
```

**Pass criteria:** Algorithm is explicitly pinned to RS256 or ES256. `none` is never accepted. HS256 is only used for single-service internal tokens with a secret ≥ 32 bytes.

---

## Step 3 — Claims validation

Every JWT decoder must validate all of the following claims. Missing any is a vulnerability.

| Claim | Attack if skipped | Required |
|-------|------------------|----------|
| `exp` (expiration) | Expired tokens accepted forever | Yes |
| `nbf` (not before) | Future tokens accepted early | Yes |
| `iss` (issuer) | Tokens from rogue issuers accepted | Yes |
| `aud` (audience) | Tokens intended for other services accepted | Yes |
| `sub` (subject) | No user identity — authorization bypass | Yes |
| `jti` (JWT ID) | Token replay if revocation is needed | Situational |

**Check:**

```bash
# Spring — check for claim validators
grep -rn "JwtClaimValidator\|withClaimName\|MappedJwtClaimSetConverter" src/
grep -rn "issuerUri\|audiences\|audience" src/main/resources/

# Node
grep -rn "issuer:\|audience:\|subject:" src/
```

**Flag** any decoder that omits `iss` or `aud` validation.

---

## Step 4 — Token storage

| Context | Secure storage | Insecure — flag immediately |
|---------|---------------|----------------------------|
| Web browser | HttpOnly + Secure + SameSite=Strict cookie | `localStorage`, `sessionStorage` |
| Mobile iOS | Keychain | UserDefaults, plain file |
| Mobile Android | EncryptedSharedPreferences / Keystore | SharedPreferences, plain file |
| Backend service | In-memory / environment variable | Hardcoded, config file committed to git |

```bash
# Check for localStorage usage
grep -rn "localStorage\.setItem\|sessionStorage\.setItem" src/

# Check for hardcoded tokens or secrets
grep -rn "Bearer \|eyJ" src/ --include="*.java" --include="*.ts" --include="*.py"
```

---

## Step 5 — Token lifetime

| Token type | Maximum TTL | Flag if exceeded |
|------------|-------------|-----------------|
| Access token | 15 minutes | > 1 hour |
| ID token | 15 minutes | > 1 hour |
| Refresh token | 30 days | > 90 days without rotation |

```bash
grep -rn "expir\|ttl\|maxAge\|access-token-time-to-live" src/main/resources/
```

Check that refresh tokens rotate on use (one-time use) and are stored hashed, not plaintext.

---

## Step 6 — Refresh token security

- [ ] Refresh token is opaque (not JWT) — prevents claims inspection
- [ ] Stored hashed in database (bcrypt / argon2) — not plaintext
- [ ] Rotation enforced on every use — old token invalidated immediately
- [ ] Revocation endpoint exists — for logout and breach response
- [ ] Reuse detection in place — reuse of a rotated token triggers revocation of the entire family

```bash
grep -rn "refreshToken\|refresh_token" src/ | grep -v "test\|spec"
```

---

## Step 7 — Output the audit report

```text
## JWT Config Audit: <service / component>

### Summary
<what was audited and overall risk posture>

### Risk Level
🟢 Low | 🟡 Medium | 🔴 High | 🚨 Critical

### Findings

| # | Category | Finding | Severity | Recommendation |
|---|----------|---------|----------|----------------|
| 1 | Algorithm | HS256 used across multiple services | High | Switch to RS256 with JWKS endpoint |
| 2 | Claims | `aud` claim not validated | High | Add audience validator to JwtDecoder |
| 3 | Storage | Access token in localStorage | Critical | Move to HttpOnly cookie |

### Checklist

- [ ] Algorithm explicitly pinned (RS256 or ES256); `none` rejected
- [ ] All required claims validated: exp, nbf, iss, aud, sub
- [ ] Access token TTL ≤ 15 minutes
- [ ] Refresh token is opaque, stored hashed, rotated on use
- [ ] Token storage is secure for the target platform
- [ ] No tokens hardcoded in source or config files
- [ ] Revocation capability exists
```

---

## Safety rules

- A 🚨 Critical finding blocks merge — do not approve until resolved
- A 🔴 High finding requires a remediation plan with an owner and due date before merge
- Never accept `alg: none` under any circumstance
- If the JWK Set URI is externally controlled, verify the URL is pinned to a trusted issuer
