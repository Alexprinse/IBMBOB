---
name: proof-pack
description: >
  Assemble the final Proof Pack for a completed ProofLoop session.
  Use this skill after all four session artifacts exist: change-contract.json,
  adversarial-report.json, repair-log.json, and verification-evidence.json.
  Produces .proofloop/session/proof-pack.json with a final VERIFIED / FAILED
  status backed by deterministic evidence.
  Triggers: "proof pack", "assemble evidence", "final status", "is it done",
  "generate proof", "verification complete", "what is the result".
---

# Proof Pack Skill

## Purpose

Assemble all session artifacts into a final, auditable Proof Pack that
answers: "Is this change verified, and what is the evidence?"

## When to use

After the full ProofLoop workflow has run:
1. Change Contract created
2. Implementation complete
3. Adversarial check complete
4. Repairs applied (if any)
5. Verification evidence collected

## Procedure

### Step 1 — Check session state

Run:
```bash
python proofloop/cli.py status
```

This shows which artifacts are present and the current `final_status` if a
proof pack already exists.

Required files (three are mandatory, one is expected):
- `.proofloop/session/change-contract.json`   — REQUIRED
- `.proofloop/session/adversarial-report.json` — REQUIRED
- `.proofloop/session/repair-log.json`         — REQUIRED
- `.proofloop/session/verification-evidence.json` — EXPECTED (absent → INCOMPLETE)

If any of the first three are missing, stop and report which file is absent.

### Step 2 — Run the assembler CLI

```bash
python proofloop/cli.py proof-pack
```

This command:
1. Loads and validates all session artifacts
2. Applies status determination rules
3. Writes `.proofloop/session/proof-pack.json`
4. Prints the final status
5. Exits non-zero for FAILED or INCOMPLETE

### Step 3 — Read and present the result

Read `.proofloop/session/proof-pack.json`.
Present the final status with the conclusion.

Format:
```
============================================================
PROOF PACK — {scenario_id}
Status: {VERIFIED | VERIFIED_WITH_WARNINGS | FAILED | INCOMPLETE}
============================================================
{conclusion}
============================================================
Deterministic evidence:
  pytest:  {tests_passed}/{tests_total} passed  [exit {pytest_exit_code}]
  mypy:    {PASS|FAIL}  [exit {mypy_exit_code}]
  ruff:    {PASS|FAIL}  [exit {ruff_exit_code}]
LLM reasoning:
  Adversarial findings: {total}
    Open blocking: {open_blocking}
Repairs applied: {repair_count}
============================================================
```

### Step 4 — Handle non-VERIFIED status

If status is FAILED:
- List every unresolved critical/high finding with its description.
- State: "Proof Pack is FAILED. These findings must be resolved before VERIFIED."

If status is VERIFIED_WITH_WARNINGS:
- List every unresolved medium/low finding.
- State: "Change is functionally verified with residual risks. Review before merging."

If status is INCOMPLETE:
- List missing artifacts from `missing_artifacts` field.
- State: "Run `python proofloop/cli.py verify --all` then re-run `proof-pack`."

## What you do NOT do

- Do not override the status. Trust the assembler output.
- Do not remove findings from the Proof Pack to make the status look better.
- Do not rerun verification to fish for a passing result.
  If verification failed, report it as failed.
- Do not report VERIFIED when `verification-evidence.json` is absent.

## Output

File: `.proofloop/session/proof-pack.json`
Displayed: Formatted summary in the terminal
