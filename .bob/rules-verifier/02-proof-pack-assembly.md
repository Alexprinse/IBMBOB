# Verifier Mode — Proof Pack Assembly Rules

## When to assemble the Proof Pack

Assemble the Proof Pack ONLY after all of the following exist:

1. `.proofloop/session/change_contract.json` — Change Contract
2. `.proofloop/session/adversarial_report.json` — Adversarial Report
3. `.proofloop/session/repair_log.json` — Repair Log (may be empty `[]` if no repairs)
4. `.proofloop/session/verification_evidence.json` — Verification Evidence

If any artifact is missing, report the gap and stop. Do not assemble a partial Proof Pack.

## Status determination rules

Apply these rules IN ORDER:

1. If `verification_evidence.pytest_exit_code != 0` → status = `FAILED`
2. If `verification_evidence.mypy_exit_code != 0` → status = `FAILED`
3. If any adversarial finding with `severity = "critical"` is NOT resolved → status = `FAILED`
4. If any adversarial finding with `severity = "high"` is NOT resolved → status = `VERIFIED_WITH_WARNINGS`
5. If `repair_log` is non-empty and all repairs passed re-verification → status = `VERIFIED`
6. If all deterministic checks pass and no open critical/high findings → status = `VERIFIED`

Default status when in doubt: `INCOMPLETE`. Never default to `VERIFIED`.

## Summary line format

The `summary` field must follow this template exactly:

```
Requirements: {req_met}/{req_total} | Tests: {tests_passed}/{tests_total} | Type check: {PASS|FAIL} | Lint: {PASS|FAIL} | Security: {sec_status} | Residual risks: {count} warning(s)
```

Example:
```
Requirements: 3/3 | Tests: 24/24 | Type check: PASS | Lint: PASS | Security: PASS | Residual risks: 1 warning(s)
```

## Assembly command

Run: `python -m proofloop proof-pack --session .proofloop/session/`

This will:
1. Load all four input artifacts
2. Validate they are present and schema-valid
3. Apply status determination rules
4. Write `.proofloop/session/proof_pack.json`
5. Print the summary line to stdout

## What you do NOT do

- Do not write the Proof Pack JSON manually. Use the CLI.
- Do not override the status determination rules.
- Do not omit any adversarial findings from the Proof Pack.
- Do not mark a finding as resolved unless a repair was recorded in `repair_log.json`.
