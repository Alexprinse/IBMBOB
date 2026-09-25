# Adversarial Mode — Finding Format

## adversarial-report.json schema

```json
{
  "report_id": "adv-{scenario_id}-001",
  "timestamp": "ISO 8601 datetime",
  "change_contract_id": "same id as change-contract.json",
  "findings": [
    {
      "finding_id": "af-01",
      "severity": "critical",
      "category": "invariant_violation",
      "invariant_id": "inv-01",
      "title": "One-line description of the finding",
      "description": "Specific description with example values showing the violation",
      "code_location": "checkoutlab/app/services/checkout.py: apply_coupon()",
      "evidence_category": "llm_reasoning",
      "remediation_task": "Specific action for repair agent. Example: Add max(Decimal('0.00'), ...) guard.",
      "is_blocking": true
    }
  ],
  "summary": {
    "total_findings": 1,
    "critical": 1,
    "high": 0,
    "medium": 0,
    "low": 0,
    "blocking_findings": 1
  }
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

## What makes a good finding

A good finding:
- Has a specific code location (file and function name at minimum)
- Has a specific example showing the failure (with actual values)
- Has a remediation task specific enough to act on without asking questions
- Correctly identifies the evidence_category as "llm_reasoning"

A bad finding:
- "The code might have issues with edge cases"
- "Consider adding more validation"
- Does not reference a specific invariant or contract requirement
