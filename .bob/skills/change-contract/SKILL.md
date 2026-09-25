---
name: change-contract
description: >
  Transform a plain developer request into a structured, machine-readable
  Change Contract. Use this skill when a developer describes a change they want
  to make. The skill produces a JSON file at
  .proofloop/session/change_contract.json that feeds every downstream agent.
  Triggers: "add feature", "change behavior", "implement", "modify",
  "I want to", "new requirement", "update", "refactor for".
---

# Change Contract Skill

## Purpose

Convert a free-form developer request into a structured Change Contract.
The Change Contract is the single source of truth for what the developer
asked for, what invariants must hold, and what evidence is required.

## When to use

Whenever a developer states a change they want to make to CheckoutLab —
or any other codebase — and no Change Contract yet exists for this session.

## Procedure

### Step 1 — Confirm the request

Repeat the request back in one sentence:
"You want to: [restatement]"
Ask: "Is this correct? Any missing details?"

### Step 2 — Identify invariants

Ask (or reason from context):
- What must NEVER happen after this change?
- What must ALWAYS remain true?
- What existing tests must keep passing?

### Step 3 — Identify affected components

List every module, service, or layer that may be touched.
Be explicit. Do not use "etc."

### Step 4 — Identify required evidence

List every check that must pass for the change to be considered complete.
Use the categories:
- functional_tests
- invariant_checks
- type_check
- lint
- api_compatibility
- security_check
- regression_tests

### Step 5 — Write the Change Contract

Write the JSON file to `.proofloop/session/change_contract.json`.
Use the schema at `proofloop/schemas/change_contract.py`.

Required fields:
- contract_id
- created_at (ISO 8601)
- scenario_id
- request_raw
- request_normalized
- intended_behavior (array of strings)
- functional_requirements (array with id + description + priority)
- invariants (array with id + description + severity)
- affected_components (array of strings)
- api_implications (array of strings, may be empty)
- data_schema_implications (array of strings, may be empty)
- security_concerns (array of strings, may be empty)
- required_evidence (object with arrays per category)
- estimated_regression_risk (low | medium | high)
- rollback_requirements (array of strings)

### Step 6 — Confirm with the developer

Print the Change Contract summary (not the full JSON).
Ask: "Does this capture what you need? Proceed?"

## Quality checks

- Every invariant must have a severity: critical, high, or medium.
- "Payment total must never be negative" must appear as a critical invariant
  whenever any pricing, discount, coupon, or total calculation is in scope.
- Functional requirements must be numbered req-01, req-02, etc.
- Invariants must be numbered inv-01, inv-02, etc.

## Output

File: `.proofloop/session/change_contract.json`
