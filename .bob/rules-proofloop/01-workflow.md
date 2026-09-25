# ProofLoop Mode — Workflow Rules

## The workflow must follow this exact order

1. Generate Change Contract → save to `.proofloop/session/change-contract.json`
2. Present contract to developer → **WAIT** for approval (Gate 1)
3. Spawn parallel investigation agents
4. Read ALL agent findings before implementing
5. Implement the change
6. Hand off to adversarial mode
7. Present adversarial findings → **WAIT** for approval (Gate 2)
8. Apply repairs (max 3 cycles per finding)
9. Switch to verifier mode
10. Present Proof Pack → **WAIT** for acknowledgment (Gate 3)

## Approval gates are mandatory

You must not proceed past a gate without explicit developer approval.
"I'll assume that's fine" is not approval.

## Change Contract must come before implementation

Never begin implementing a feature before the Change Contract is:
- written
- shown to the developer
- explicitly approved

## Subagents run in parallel

The Architect, Test, Security, and API subagents all investigate the Change Contract simultaneously.
Do not run them sequentially when parallel execution is available.

## What the proofloop mode may and may not do

MAY:
- Generate and edit Change Contract JSON
- Spawn subagents
- Read agent findings files
- Implement the requested change in CheckoutLab
- Apply repairs based on adversarial findings
- Write to repair-log.json

MAY NOT:
- Mark findings as resolved without running the relevant check
- Report VERIFIED based on its own judgment
- Skip the adversarial mode step
- Write to adversarial-report.json (that is the adversarial mode's file)
