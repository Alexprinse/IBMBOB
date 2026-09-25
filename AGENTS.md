# ProofLoop — AGENTS.md

This is the primary project context for all IBM Bob 2.0 agents working in this repository.

---

## What is ProofLoop?

ProofLoop is an evidence-backed developer workflow built on IBM Bob 2.0.

The central thesis: AI-assisted development accelerates implementation, but verification
is fragmented. ProofLoop closes this gap with a structured loop that produces a Proof Pack —
a traceable evidence artifact that proves a change is correct.

Every ProofLoop session results in:

1. A **Change Contract** — machine-readable statement of what must be true
2. An **Adversarial Report** — structured findings assuming the implementation is wrong
3. A **Repair Log** — record of what was fixed and why
4. **Verification Evidence** — real tool output (pytest, mypy, ruff)
5. A **Proof Pack** — the final evidence artifact

The final status is one of: VERIFIED / VERIFIED_WITH_WARNINGS / FAILED / INCOMPLETE.

---

## Repository Structure

```
IBMBOB/
├── AGENTS.md                         ← this file
├── .bob/                             ← Bob configuration
│   ├── custom_modes.yaml             ← proofloop, adversarial, verifier modes
│   ├── settings.json                 ← tool permissions
│   ├── rules/                        ← global rules for all modes
│   ├── rules-proofloop/              ← proofloop mode rules
│   ├── rules-adversarial/            ← adversarial mode rules
│   ├── rules-verifier/               ← verifier mode rules
│   └── skills/                       ← project-local skills
├── proofloop/                        ← Python orchestration package
│   ├── cli.py                        ← CLI entry point
│   ├── schemas/                      ← Pydantic schemas for all JSON artifacts
│   ├── verifiers/                    ← real tool wrappers (pytest/mypy/ruff)
│   └── assembler.py                  ← proof-pack.json assembly
├── .proofloop/session/               ← runtime artifacts (gitignored)
├── checkoutlab/                      ← synthetic demo application
│   ├── app/                          ← FastAPI + SQLAlchemy + SQLite
│   └── tests/                        ← pytest test suite (20+ tests)
├── benchmark/scenarios/              ← S01-S05 scenario definitions
├── dashboard/                        ← static HTML/CSS/JS visualization
├── demo/session-snapshot/            ← pre-recorded real artifacts
└── docs/bob-evidence/                ← team Bob session screenshots
```

---

## Session Artifacts Directory

All agent outputs are written to `.proofloop/session/`.

| File | Written by | Contents |
|---|---|---|
| `change-contract.json` | proofloop mode | Machine-readable contract |
| `architect-findings.json` | Architect subagent | Affected components, risks |
| `test-findings.json` | Test subagent | Test gaps, regression risks |
| `security-findings.json` | Security subagent | Security implications |
| `api-findings.json` | API subagent | API contract impacts |
| `adversarial-report.json` | adversarial mode | Findings with remediation tasks |
| `repair-log.json` | repair agent | What was fixed and why |
| `verification-evidence.json` | proofloop CLI | Real tool output |
| `proof-pack.json` | proofloop CLI | Final assembled evidence |

**Rule:** No agent writes to another agent's file.

---

## Change Contract

The Change Contract is a JSON document generated from the developer's natural-language request.

Required fields:
- `id` — unique identifier for this contract
- `version` — schema version
- `status` — draft / approved / in_progress / challenged / repaired / verified / failed
- `request.original_text` — developer's exact words
- `intent_summary` — one-paragraph interpretation of the request
- `functional_requirements` — list of {id, description} items
- `affected_components` — list of {name, reason, risk_level}
- `invariants` — list of {id, description, verification_method, criticality}
- `security_concerns` — list of concern strings
- `rollback_strategy` — string
- `evidence_required` — list of {type, description, is_blocking}

Schema location: `proofloop/schemas/change_contract.py`
Example S01: `benchmark/scenarios/s01_coupon_support.json`

---

## ProofLoop CLI Commands

```bash
# From project root, with venv activated:
python proofloop/cli.py verify --tests      # runs pytest, captures results
python proofloop/cli.py verify --types      # runs mypy, captures results
python proofloop/cli.py verify --lint       # runs ruff, captures results
python proofloop/cli.py verify --all        # all checks → verification-evidence.json
python proofloop/cli.py proof-pack          # assembles proof-pack.json
python proofloop/cli.py status              # prints current contract status
python proofloop/cli.py reset               # clears session for a new scenario
```

---

## Evidence Standards — CRITICAL

Every piece of evidence in the Proof Pack must be labeled:

### `deterministic`
Evidence produced by a real tool with a real exit code.
Examples: pytest results, mypy error count, ruff violations.
**Never paraphrase, never summarize.** Capture exact tool output.

### `llm_reasoning`
Evidence produced by Bob agent analysis.
Examples: architectural risk identification, adversarial findings.
**Always include specific code locations and reasoning.**

These two categories must never be conflated.
A Proof Pack that lists an LLM observation as deterministic evidence is invalid.

---

## Key Business Invariant for S01

For the coupon support scenario:

**inv-01: Payment amount must always be >= 0.**

The seeded defect in CheckoutLab produces:
```
subtotal = $50.00
coupon   = $75.00
result   = -$25.00   ← VIOLATION
```

The correct implementation:
```python
final_total = max(Decimal("0.00"), order_subtotal - discount_amount)
```

---

## CheckoutLab Application

Technology: FastAPI, SQLAlchemy, SQLite, Pydantic v2, pytest

Key files:
- `checkoutlab/app/main.py` — FastAPI application entry point
- `checkoutlab/app/models.py` — SQLAlchemy ORM models
- `checkoutlab/app/schemas.py` — Pydantic request/response schemas
- `checkoutlab/app/database.py` — SQLite database setup
- `checkoutlab/app/services/checkout.py` — checkout business logic
- `checkoutlab/app/services/payment.py` — payment service stub
- `checkoutlab/app/services/inventory.py` — inventory stub
- `checkoutlab/tests/test_checkout.py` — core business logic tests
- `checkoutlab/tests/test_invariants.py` — business invariant tests (critical)
- `checkoutlab/tests/test_api.py` — API integration tests

Run tests: `pytest checkoutlab/tests/ -v`

---

## Team Ownership

**Team Member 1 — Bob Workflow Engineer**
Owns: `.bob/` configuration, AGENTS.md, ProofLoop schemas, assembler, Proof Pack

**Team Member 2 — Verification/Application Engineer**
Owns: CheckoutLab application, verification CLI verifiers, dashboard, benchmark scenarios

Both members must perform meaningful Bob sessions and capture screenshots in `docs/bob-evidence/`.

---

## Three Custom Modes

Use the appropriate mode for each stage:

| Mode | When | What it does |
|---|---|---|
| `proofloop` | Starting a new workflow | Generates contract, coordinates agents, drives full loop |
| `adversarial` | After implementation | Challenges implementation; hunts for invariant violations |
| `verifier` | After repair | Runs deterministic tools; assembles Proof Pack |

To switch modes: use the mode selector in Bob or reference the mode slug.
