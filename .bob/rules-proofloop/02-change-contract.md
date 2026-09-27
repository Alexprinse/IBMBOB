# ProofLoop Mode — Change Contract Rules

## Schema

The Change Contract is defined in `proofloop/schemas/change_contract.py` and saved to
`.proofloop/session/change-contract.json`.

## Required fields

A Change Contract is only valid if it contains ALL of the following:

- `contract_id` — unique string identifier (e.g. "cc-s01-001")
- `created_at` — ISO 8601 datetime
- `scenario_id` — benchmark scenario ID (e.g. "s01")
- `request_raw` — developer's exact words, verbatim
- `request_normalized` — normalized single-sentence summary
- `intended_behavior` — list of strings describing what should be true after the change
- `functional_requirements` — minimum 1 item, each with:
  - `id` (pattern `req-NN`, e.g. "req-01")
  - `description`
  - `priority` — one of: `must_have`, `should_have`, `nice_to_have`
- `invariants` — minimum 1 item; each invariant must have:
  - `id` (pattern `inv-NN`, e.g. "inv-01")
  - `description` (what must remain true)
  - `severity` — one of: `critical`, `high`, `medium`, `low`
- `affected_components` — list of file paths or component names
- `required_evidence` — object with lists of test names / commands to verify the change
- `estimated_regression_risk` — one of: `low`, `medium`, `high`

## Invariants must be specific

Bad invariant: "The checkout should work correctly."
Good invariant: "The payment amount sent to the payment service must always be >= 0."

## Save location

Always save to: `.proofloop/session/change-contract.json`

## Status lifecycle

The contract's lifecycle is tracked via the ProofLoop workflow:

```
draft
  ↓ (developer approves)
in_progress
  ↓ (adversarial mode runs)
challenged
  ↓ (repair applied)
repaired
  ↓ (all checks pass)
verified
      OR
  ↓ (max repair cycles exceeded)
failed
```

Note: `status` is not a field in the Pydantic schema — it is tracked as part of the
ProofLoop workflow state, not embedded in the contract JSON itself.
