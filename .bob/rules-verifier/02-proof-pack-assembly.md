# Verifier Mode — Proof Pack Assembly Rules

## Session artifact filenames

All session artifacts use **hyphen** naming under `.proofloop/session/`:

| Artifact | Filename |
|---|---|
| Change Contract | `change-contract.json` |
| Adversarial Report | `adversarial-report.json` |
| Repair Log | `repair-log.json` |
| Verification Evidence | `verification-evidence.json` |
| Proof Pack | `proof-pack.json` |

## When to assemble the Proof Pack

Assemble the Proof Pack ONLY after all of the following exist:

1. `.proofloop/session/change-contract.json` — Change Contract
2. `.proofloop/session/adversarial-report.json` — Adversarial Report
3. `.proofloop/session/repair-log.json` — Repair Log (may have empty `repairs` list if no repairs)
4. `.proofloop/session/verification-evidence.json` — Verification Evidence

If `verification-evidence.json` is missing, the assembler still writes `proof-pack.json` with
`final_status = "INCOMPLETE"` and lists the missing artifact in `missing_artifacts`.
If any of the other three are missing, assembly raises an error.

## Status determination rules

Apply these rules IN ORDER:

1. If `verification-evidence.json` is absent → status = `INCOMPLETE`
2. If `pytest exit_code != 0` → status = `FAILED`
3. If `mypy exit_code != 0` → status = `FAILED`
4. If any adversarial finding with `severity = "critical"` has `status = "open"` → status = `FAILED`
5. If any adversarial finding with `severity = "high"` has `status = "open"` → status = `FAILED`
6. If any adversarial finding with `severity = "medium"` or `"low"` has `status = "open"` → status = `VERIFIED_WITH_WARNINGS`
7. Otherwise → status = `VERIFIED`

Default when in doubt: `INCOMPLETE`. Never default to `VERIFIED`.

## Assembly command

```bash
python proofloop/cli.py proof-pack
```

This will:
1. Load all session artifacts from `.proofloop/session/`
2. Validate them against the Pydantic schemas
3. Apply status determination rules
4. Write `.proofloop/session/proof-pack.json`
5. Print the final status to stdout
6. Exit non-zero for FAILED or INCOMPLETE

## Check session state at any time

```bash
python proofloop/cli.py status
```

## What you do NOT do

- Do not write the Proof Pack JSON manually. Use the CLI.
- Do not override the status determination rules.
- Do not omit any adversarial findings from the Proof Pack.
- Do not mark a finding as resolved unless a repair was recorded in `repair-log.json`.
- Do not report VERIFIED when `verification-evidence.json` is absent.
