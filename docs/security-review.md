# Historical secret-scan adjudication

The full-history Gitleaks scan retains default detection rules and fails on
unreviewed findings. `.gitleaksignore` contains only exact finding fingerprints,
not file, rule, commit-wide or value-based exclusions.

The architecture guardian, principal engineer, SecOps engineer and QE engineer
independently reviewed the four guide findings at commit
`46db9883f7d3f896f641b0755bd316519ff30b6b`, in the Claude and Qwen
`GIT_HOOKS_GUIDE.md` files at lines 270 and 273. All four confirmed synthetic
documentation examples: an identical sequential demonstration payload appears
in shell fences, with no runtime reference. Only these four findings are
excepted. Their values are intentionally not reproduced here.

The owner explicitly confirmed on 7 October 2026 that the exposed LiteLLM
credential was revoked or rotated. All four specialists reviewed this attestation
and approved only the two historical client-settings fingerprints at line 37,
in commits `62a925c47b9f32827df634a3f7a1fda0e7b1b1aa` and
`dcd6b1aad272874b1587bdf7d7e2139305b273e8`.
These are owner-confirmed revoked/rotated historical credentials, not dummy
examples or false positives. Independent issuer verification is not claimed.
The earlier statement that the setup was obsolete was insufficient on its own.
Deleting current files does not remove historical exposure. No history rewrite
or broad scan suppression is authorised by this review. Default full-history
detection and failure on every unreviewed finding remain enabled.

The fingerprint format and matching behaviour are documented in the
[Gitleaks v8.30.1 documentation](https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#gitleaksignore).
