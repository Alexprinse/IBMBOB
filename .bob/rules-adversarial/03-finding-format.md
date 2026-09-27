# Adversarial Mode — Finding Format

## adversarial-report.json schema

The adversarial report is written to `.proofloop/session/adversarial-report.json`.
It is validated against `proofloop/schemas/adversarial_report.py`.

```json
{
  "report_id": "ar-s01-001",
  "contract_id": "cc-s01-001",
  "created_at": "2025-01-01T12:00:00Z",
  "scenario_id": "s01",
  "findings": [
    {
      "finding_id": "af-01",
      "severity": "critical",
      "category": "invariant_violation",
      "description": "Specific description with example values showing the violation",
      "evidence": "What was observed in code or reasoning (with file:line reference)",
      "evidence_category": "llm_reasoning",
      "suggested_repair": "Specific action for repair agent. Example: Add max(Decimal('0.00'), ...) guard.",
      "status": "open",
      "resolved_by_repair_id": null
    }
  ],
  "summary": "N findings: X critical, Y high, Z medium, W low."
}
```

## Severity levels

| Level | When to use |
|---|---|
| `critical` | Violates a must_pass invariant; incorrect behavior guaranteed |
| `high` | Violates a should_pass invariant; incorrect behavior likely |
| `medium` | Edge case that may cause incorrect behavior |
| `low` | Code quality or missing test for an informational invariant |

## Category values

| Category | When to use |
|---|---|
| `invariant_violation` | Code violates a stated invariant |
| `missing_test` | Invariant has no covering test |
| `security` | Security regression or missing validation |
| `scope_creep` | Implementation exceeds what the contract specified |
| `edge_case` | Unhandled edge condition not covered by an invariant |

## Finding status values

| Status | Meaning |
|---|---|
| `open` | Finding has not been addressed |
| `resolved` | Finding was addressed by a recorded repair |
| `accepted_risk` | Finding acknowledged but intentionally not repaired |

## Output file

Always write to: `.proofloop/session/adversarial-report.json`

## What makes a good finding

A good finding:
- Has a specific code location in the `evidence` field (file and line number or function name)
- Has a specific example showing the failure (with actual values)
- Has a `suggested_repair` specific enough to act on without asking questions
- Always uses `"evidence_category": "llm_reasoning"` (adversarial analysis is never deterministic)

A bad finding:
- "The code might have issues with edge cases"
- "Consider adding more validation"
- Does not reference a specific invariant or contract requirement
