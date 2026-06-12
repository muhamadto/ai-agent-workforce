---
name: auth-engineering
description: Reference knowledge for authentication and identity engineering — OAuth 2.1, OIDC, SAML, WebAuthn/passkeys, MFA, JWT security, session management, federated identity, and secure token handling on web, iOS, and Android. Load this BEFORE designing, implementing, or reviewing any authentication, authorization, or token-handling code.
---

# Authentication & Identity Engineering Reference

Reference knowledge for identity, authentication, and authorization work.
Load this skill before designing, implementing, or reviewing auth code on any platform.

## Identity & Access Management Standards

### OAuth 2.1

- **Authorization Code Flow with PKCE**: Mandatory for ALL clients (public and confidential)
- **Client Credentials Flow**: Service-to-service (machine-to-machine) authentication
- **Refresh Token Flow**: Token renewal with rotation on every use
- **Device Authorization Flow**: IoT, TV, CLI applications
- **Deprecated — never implement**: Implicit Flow (insecure), Resource Owner Password Credentials (anti-pattern)

### OpenID Connect (OIDC)

- **ID Token**: JWT with identity claims (iss, sub, aud, exp, iat, nonce)
- **UserInfo Endpoint**: User profile retrieval; verify `sub` matches the ID token
- **Discovery**: `/.well-known/openid-configuration`
- **Dynamic Client Registration**: Runtime client registration
- **Standard Claims**: profile, email, address, phone scopes
- **Logout**: RP-initiated, back-channel, and front-channel logout

### SAML 2.0

- Enterprise SSO federation with legacy IdPs; SP and IdP configuration; signed XML assertions

### WebAuthn / FIDO2 (Passkeys)

- **Platform authenticators**: Touch ID, Face ID, Windows Hello; **roaming**: YubiKey, Titan Key
- **Registration**: server challenge → `navigator.credentials.create()` → user verification → key pair created (private key never leaves device) → server stores public key + credential ID (validate attestation if required)
- **Authentication**: server challenge → `navigator.credentials.get()` → user verification → authenticator signs challenge → server verifies signature with stored public key
- **Libraries**: Yubico java-webauthn-server, @simplewebauthn/browser, @simplewebauthn/server

### Multi-Factor Authentication

- **TOTP** (Google Authenticator, Authy); **push notifications**; **biometrics** via WebAuthn; **backup codes** for recovery
- **SMS codes are discouraged** (SIM-swap attacks)

## JWT

### Structure & Claims

- Header (algorithm, type), payload (claims), signature
- Standard claims: iss, sub, aud, exp, iat, nbf; custom claims: roles, scopes, permissions, tenant ID
- Algorithms: RS256/ES256 (asymmetric, preferred); HS256 (symmetric — avoid for distributed systems)

### JWT Security (Mandatory)

- **Algorithm verification**: never accept `none`; verify the algorithm matches the expected one; prevent HS256→RS256 confusion attacks
- **Full claims validation**: signature, exp, nbf, iss, aud, iat — reject if missing or invalid
- **Short-lived access tokens**: 5-15 minutes
- **Refresh tokens**: opaque and cryptographically random (not JWT), stored hashed (bcrypt/argon2), rotated on every use (one-time use), revocable
- **Revocation**: token blacklist or short TTLs; mass revocation capability for breach response

### Token Storage Rules

- **Web**: HttpOnly + Secure + SameSite=Strict cookies — NEVER localStorage or sessionStorage
- **iOS**: Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` — never UserDefaults or files
- **Android**: `EncryptedSharedPreferences` (Jetpack Security) backed by Android Keystore — never plain SharedPreferences

## OAuth2/OIDC Security (RFC 6749, RFC 7636, BCP 212)

- **PKCE (RFC 7636)**: mandatory on every authorization code flow
- **State parameter**: random and unpredictable — CSRF protection on authorization requests
- **Nonce parameter** (OIDC): replay prevention, binds ID token to client session
- **Redirect URI validation**: exact match, no wildcards, no open redirects
- **Token binding (DPoP)**: bind tokens to the client instance to blunt token theft
- **Scope validation**: least privilege; validate requested scopes server-side
- **Client authentication**: confidential clients use client_secret_basic/post or private_key_jwt; public clients have no secret and rely on PKCE
- **Token introspection (RFC 7662)** for opaque tokens; **token revocation (RFC 7009)** for logout and breach response
- **Token exchange (RFC 8693)** for crossing audience/scope boundaries between services

## Access Control Models

- **RBAC**: users → roles → permissions
- **ABAC**: policy decisions from user/resource attributes
- **Policy engines**: Open Policy Agent (OPA), Casbin for complex policies
- **OAuth2 scopes**: fine-grained permissions (read:users, write:orders, admin:system)

## Session Management

- **Stateless** (JWT, horizontally scalable) vs **stateful** (Redis/database, for sensitive apps)
- Regenerate session ID after login (fixation prevention)
- Absolute timeout + idle timeout; concurrent session limits per user
- Remember-me via persistent hashed tokens, separate from the session
- Logout: clear cookies server-side AND revoke the refresh token at the authorization server

## Federated Identity & Social Login

- **Platform IdP**: Keycloak is the standard identity provider here (auth.sandpipers.io, the Cognito equivalent) — realms, clients, roles, identity brokering; integrate via OIDC discovery
- **Social providers**: Google, GitHub, Microsoft, Apple Sign-In (brokered through Keycloak)
- **Other enterprise IdPs** (when encountered): Okta, Auth0, Azure AD (Entra ID), Ping Identity
- **Account linking**: merge multiple identities into one user account
- **JIT provisioning**: auto-create users on first federated login

## Password Security (if passwords are used at all)

- **Hashing**: Argon2id (recommended), BCrypt cost 12+, or PBKDF2 100k+ iterations; unique salt per password
- **Policy**: minimum 12 characters, no complexity theatre — length + breach-database check (HaveIBeenPwned)
- **Reset**: cryptographically random one-time tokens, 15-30 minute expiry, email confirmation

## Platform Integration

### Web (SPA / SSR)

- Authorization Code + PKCE is mandatory for browser clients; no Implicit Flow
- Tokens in HttpOnly/Secure/SameSite=Strict cookies; CSP with `script-src 'self'` against XSS exfiltration
- Silent refresh via back-channel with <15 min access tokens and rotating refresh tokens

### iOS

- `ASWebAuthenticationSession` with Authorization Code + PKCE (not SFSafariViewController for token exchanges)
- Keychain storage gated by `LAContext.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics)` for sensitive operations
- App Attest (DeviceCheck) to verify request integrity before issuing tokens
- Certificate pinning on the auth server; fail closed on pin mismatch

### Android

- Custom Tabs with AppAuth-Android (Authorization Code + PKCE); never WebView for OAuth
- Token retrieval gated by `BiometricPrompt` + `CryptoObject`, `BIOMETRIC_STRONG` only
- Play Integrity API verdict validated server-side before token issuance; reject/restrict rooted devices

## Microservices & Zero Trust Architecture

- **API Gateway**: centralized token validation and rate limiting at the edge
- **Service-to-service**: client credentials flow, mutual TLS (mTLS)
- **Token relay** to preserve user context across services; validate `aud` at every hop (no confused deputies)
- **Zero trust**: never trust, always verify — authenticate and authorize every request including internal ones; least privilege; micro-segmentation; continuous re-verification; assume breach and limit blast radius

## Threat Detection & SecOps

- **Brute force**: rate limiting, account lockout (e.g. 5 failures → 15 min lockout)
- **Credential stuffing**: monitor login patterns, block known-breached credentials
- **Account takeover**: anomaly detection — new location/device/time, impossible travel
- **Audit logging**: every authentication event, authorization decision, token issuance, and security event
- **Alerting**: failed-login spikes, token reuse or expired-token attempts, privilege-escalation attempts
- **Incident response**: lockout procedures, mass token revocation, user notification of suspicious logins

## Security Testing Checklist

- Authentication bypass (missing checks, logic flaws) and authorization bypass (horizontal/vertical privilege escalation)
- Token leakage, tampering, replay, algorithm confusion
- Session fixation, hijacking, concurrent session handling
- CSRF (state parameter, synchronizer tokens) and XSS in auth flows (error messages, redirects)
- Rate limiting / lockout / CAPTCHA on auth endpoints
- PKCE enforcement, redirect URI validation, scope enforcement, refresh token rotation
- OIDC nonce and ID token validation, logout flows
- Passkey attestation, credential validation, challenge-response correctness

## Compliance Map

- **OWASP Top 10**: A01 Broken Access Control, A02 Cryptographic Failures, A07 Identification & Authentication Failures
- **NIST SP 800-63B**: authenticator types and lifecycle
- **PCI DSS** (strong auth, encryption, access control), **GDPR** (consent, minimization, erasure), **SOC 2**, **ISO 27001**

## Related Skills

- [/oauth-threat-model](../oauth-threat-model/SKILL.md) — threat model an OAuth2/OIDC flow before building it
- [/audit-jwt-config](../audit-jwt-config/SKILL.md) — audit any token-path change before merge
- [/threat-model](../threat-model/SKILL.md) — broader STRIDE analysis across the auth surface
