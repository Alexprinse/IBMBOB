# ProofLoop Mode — Change Contract Rules

## Required fields

A Change Contract is only valid if it contains ALL of the following:

- `id` — unique string identifier (e.g. "cc-s01")
- `version` — schema version string
- `status` — must be "draft" when first created
- `request.original_text` — developer's exact words, verbatim
- `request.requester` — "developer"
- `intent_summary` — one paragraph explaining the interpreted intent
- `functional_requirements` — minimum 1 item, each with `id` and `description`
- `affected_components` — minimum 1 item, each with `name`, `reason`, `risk_level`
- `invariants` — minimum 1 item; each invariant must have:
  - `id` (e.g. "inv-01")
  - `description` (what must remain true)
  - `verification_method` (test | type_check | lint | schema_validation | api_check)
  - `criticality` (must_pass | should_pass | informational)
- `security_concerns` — list of strings (can be empty list if none apply)
- `rollback_strategy` — string
- `evidence_required` — minimum 1 item; each item must have:
  - `type` — from the approved enum
  - `description` — what this evidence proves
  - `is_blocking` — true | false

## Invariants must be specific

Bad invariant: "The checkout should work correctly."
Good invariant: "The payment amount sent to the payment service must always be >= 0."

## Evidence required must be verifiable

For every invariant with `criticality: "must_pass"`, there must be at least one
`evidence_required` item with `is_blocking: true`.

## Save location

Always save to: `.proofloop/session/change-contract.json`

## Status transitions

Valid transitions:
draft → approved (developer approves)
approved → in_progress (implementation starts)
in_progress → challenged (adversarial mode runs)
challenged → repaired (repair applied)
repaired → verified (all checks pass)
repaired → failed (max repair cycles exceeded)
