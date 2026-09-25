# ProofLoop — Evidence Standards (applies to ALL modes)

## The cardinal rule

Every claim of correctness must be backed by evidence.
"It looks correct" is not evidence.
"The AI said it is correct" is not evidence.

## Two categories of evidence

### 1. Deterministic evidence

Source: a real tool with a real exit code.

Examples:
- pytest: 24 passed, 0 failed (exit code 0)
- mypy: Success: no issues found (exit code 0)
- ruff: All checks passed (exit code 0)

Deterministic evidence is labeled `"evidence_category": "deterministic"` in all JSON artifacts.

### 2. LLM reasoning

Source: Bob agent analysis, architectural review, adversarial finding.

Examples:
- Architect Agent: "This change affects the payment service because..."
- Adversarial Agent: "Invariant inv-01 is violated because..."

LLM reasoning is labeled `"evidence_category": "llm_reasoning"` in all JSON artifacts.

## The mixing prohibition

NEVER label LLM reasoning as deterministic evidence.
NEVER report a tool result without running the actual tool.
NEVER fabricate exit codes, test counts, or error counts.

A Proof Pack with fabricated evidence is worse than no Proof Pack.

## Session artifact location

All session artifacts are written to: `.proofloop/session/`

Do not write session artifacts anywhere else.
Do not read session artifacts from anywhere else.
