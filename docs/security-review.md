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

The two findings in historical LiteLLM client settings are not excepted.
Localhost routing alone does not establish that a value was a dummy: proxy
authentication can require a genuine credential. Owner or issuer evidence is
required before classification; genuine credentials must be revoked or rotated.
Deleting current files does not remove historical exposure. No history rewrite
or broad scan suppression is authorised by this review.

The fingerprint format and matching behaviour are documented in the
[Gitleaks v8.30.1 documentation](https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#gitleaksignore).
