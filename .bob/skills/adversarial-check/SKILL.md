---
name: adversarial-check
description: >
  Challenge a completed implementation by assuming it is potentially wrong.
  Use this skill after implementation is complete and tests pass. The skill
  hunts for invariant violations, edge cases, security regressions, and
  missing tests. Produces .proofloop/session/adversarial_report.json.
  Triggers: "challenge", "adversarial check", "verify", "look for bugs",
  "what could go wrong", "find edge cases", "security review", "adversarial".
---

# Adversarial Check Skill

## Purpose

Assume the implementation is potentially wrong and find problems that
passed tests but may still be incorrect, dangerous, or incomplete.
The adversarial check is NOT a code review for style. It is an active
attempt to break the implementation.

## When to use

After implementation is complete, a Change Contract exists at
`.proofloop/session/change_contract.json`, and you are operating in
adversarial mode.

## Procedure

### Step 1 — Load the Change Contract

Read `.proofloop/session/change_contract.json`.
Extract: invariants, affected_components, security_concerns.

### Step 2 — Critical invariant checks

For EVERY invariant listed in the Change Contract, attempt to find a
scenario where it is violated.

**Mandatory checks (always run these):**
- Payment total must never be negative.
  Test mentally: what if coupon_value > subtotal? What is the result?
  If no `max(0, ...)` or equivalent guard exists, this is a critical finding.
- Coupon must not be applied twice to the same order.
- Coupon with is_active=False must be rejected.
- Coupon with expired_at in the past must be rejected.

### Step 3 — Edge case enumeration

Enumerate at minimum:
- Zero-value inputs
- Negative inputs
- Boundary values (coupon = exactly subtotal, coupon > subtotal)
- Invalid types
- Empty collections
- Expired resources
- Concurrent or double-use scenarios
- Missing optional fields

### Step 4 — Security scan

Check for:
- Unauthenticated access to privileged endpoints
- Missing input validation (negative discount amounts, zero-price items)
- SQL injection vectors
- Coupon enumeration (are coupon codes predictable?)
- Missing rate limiting on coupon validation endpoint

### Step 5 — API contract checks

Check for:
- New required fields that break existing clients
- Changed response shapes
- Changed error codes or HTTP status codes
- Missing backward compatibility

### Step 6 — Write the Adversarial Report

Write to `.proofloop/session/adversarial_report.json`.
Use the schema at `proofloop/schemas/adversarial_report.py`.

Every finding must include:
- finding_id (af-01, af-02, ...)
- severity (critical | high | medium | low)
- category (invariant_violation | edge_case | security | api_contract | missing_test)
- description
- evidence (what you observed in code or reasoning)
- evidence_category (deterministic | llm_reasoning)
- suggested_repair
- status (open)

### Step 7 — Summarize findings

Print: "Adversarial check complete. Found N findings: X critical, Y high, Z medium, W low."
If critical findings exist, print: "⚠ CRITICAL FINDINGS REQUIRE REPAIR BEFORE VERIFICATION"

## Quality standards

- Never report a finding that is not supported by code you actually read.
- Always check boundary: coupon_value > subtotal → negative total.
  If no floor guard exists in the code, this MUST be a critical finding.
- Severity critical = invariant violation or security vulnerability.
- Severity high = data corruption or significant behavioral regression.
- Severity medium = edge case that produces wrong output.
- Severity low = missing test coverage without code defect.

## Output

File: `.proofloop/session/adversarial_report.json`
