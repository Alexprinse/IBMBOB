---
name: proof-pack
description: >
  Assemble the final Proof Pack for a completed ProofLoop session.
  Use this skill after all four session artifacts exist: change_contract.json,
  adversarial_report.json, repair_log.json, and verification_evidence.json.
  Produces .proofloop/session/proof_pack.json with a final VERIFIED / FAILED
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

### Step 1 — Check all artifacts exist

Required files:
- `.proofloop/session/change_contract.json`
- `.proofloop/session/adversarial_report.json`
- `.proofloop/session/repair_log.json`
- `.proofloop/session/verification_evidence.json`

If any are missing, report exactly which file is missing and stop.

### Step 2 — Run the assembler CLI

```
python -m proofloop proof-pack --session .proofloop/session/
```

This command:
1. Validates all input artifacts
2. Applies status determination rules (see rules-verifier/02-proof-pack-assembly.md)
3. Writes `.proofloop/session/proof_pack.json`
4. Prints the summary line

### Step 3 — Read and present the result

Read `.proofloop/session/proof_pack.json`.
Present the final status with the summary line.

Format:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROOF PACK — {scenario_id}
Status: {VERIFIED | VERIFIED_WITH_WARNINGS | FAILED | INCOMPLETE}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{summary line}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deterministic evidence:
  pytest:  {tests_passed}/{tests_total} passed  [exit {pytest_exit_code}]
  mypy:    {PASS|FAIL}  [exit {mypy_exit_code}]
  ruff:    {PASS|FAIL}  [exit {ruff_exit_code}]
LLM reasoning:
  Adversarial findings: {total}
    Critical resolved: {critical_resolved}/{critical_total}
    High resolved:     {high_resolved}/{high_total}
Repairs applied: {repair_count}
Residual risks: {residual_risk_count}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 4 — Handle non-VERIFIED status

If status is FAILED:
- List every unresolved critical finding with its description.
- State: "Proof Pack cannot be considered complete until these findings are resolved."

If status is VERIFIED_WITH_WARNINGS:
- List every unresolved high finding.
- State: "Change is functionally verified with residual risks. Review before merging."

If status is INCOMPLETE:
- List missing artifacts.
- State: "Run the full ProofLoop workflow before assembling a Proof Pack."

## What you do NOT do

- Do not override the status. Trust the assembler output.
- Do not remove findings from the Proof Pack to make the status look better.
- Do not rerun verification to fish for a passing result.
  If verification failed, report it as failed.

## Output

File: `.proofloop/session/proof_pack.json`
Displayed: Formatted summary in the terminal
