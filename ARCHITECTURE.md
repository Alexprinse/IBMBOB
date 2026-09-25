# ProofLoop — Architecture

## Overview

ProofLoop is a three-layer system built around IBM Bob 2.0.

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER A — IBM Bob IDE                                          │
│  Developer → proofloop mode → Change Contract                   │
│  → parallel subagents (Architect/Test/Security/API)             │
│  → Bob implements the change                                    │
│  → adversarial mode challenges the implementation               │
│  → repair agent fixes findings                                  │
│  → verifier mode runs deterministic tools                       │
│  → Proof Pack assembled                                         │
└────────────────────┬────────────────────────────────────────────┘
                     │ reads/writes .proofloop/session/*.json
┌────────────────────▼────────────────────────────────────────────┐
│  LAYER B — ProofLoop Orchestration Layer                        │
│  .proofloop/session/     runtime JSON artifacts                 │
│  proofloop/cli.py        verify | proof-pack | status | reset   │
│  proofloop/schemas/      Pydantic schemas for all artifacts     │
│  proofloop/verifiers/    pytest / mypy / ruff / api-compat      │
│  proofloop/assembler.py  builds proof-pack.json                 │
│  checkoutlab/            synthetic demo application             │
└────────────────────┬────────────────────────────────────────────┘
                     │ reads proof-pack.json (polling)
┌────────────────────▼────────────────────────────────────────────┐
│  LAYER C — Web Dashboard                                        │
│  dashboard/index.html    static HTML pipeline visualization     │
│  dashboard/app.js        reads JSON, renders stages             │
│  dashboard/serve.py      local HTTP server                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## IBM Bob Configuration

### Files created at project level

| Path | Purpose |
|---|---|
| `AGENTS.md` | Project context for all Bob agents |
| `.bob/custom_modes.yaml` | Three custom modes |
| `.bob/settings.json` | Allowed shell commands |
| `.bob/rules/` | Rules for all modes |
| `.bob/rules-proofloop/` | Proofloop mode rules |
| `.bob/rules-adversarial/` | Adversarial mode rules |
| `.bob/rules-verifier/` | Verifier mode rules |
| `.bob/skills/change-contract/SKILL.md` | Change Contract skill |
| `.bob/skills/adversarial-check/SKILL.md` | Adversarial challenge skill |
| `.bob/skills/proof-pack/SKILL.md` | Proof Pack skill |

### Custom modes

| Mode | Purpose | Key constraint |
|---|---|---|
| `proofloop` | Lead orchestrator | Demands evidence; never accepts "looks correct" |
| `adversarial` | Challenge the implementation | Read-only; finds invariant violations |
| `verifier` | Run deterministic checks | Runs real tools; never fabricates output |

---

## Agent Communication Protocol

All agent handoffs happen via JSON files in `.proofloop/session/`.

```
.proofloop/session/
  change-contract.json        ← proofloop mode
  architect-findings.json     ← Architect subagent
  test-findings.json          ← Test subagent
  security-findings.json      ← Security subagent
  api-findings.json           ← API subagent
  adversarial-report.json     ← adversarial mode
  repair-log.json             ← repair agent
  verification-evidence.json  ← proofloop CLI
  proof-pack.json             ← assembler
```

No agent writes to another agent's file.

---

## Evidence Categories

Every item in the Proof Pack carries an evidence category label.

| Category | Source | Examples |
|---|---|---|
| `deterministic` | Real tool output | pytest exit code, mypy error count, ruff violations |
| `llm_reasoning` | Bob agent analysis | Adversarial finding, architectural risk |

These must never be conflated. The final Proof Pack shows both categories separately.

---

## ProofLoop CLI

```bash
python proofloop/cli.py verify --tests    # runs pytest
python proofloop/cli.py verify --types    # runs mypy
python proofloop/cli.py verify --lint     # runs ruff
python proofloop/cli.py verify --all      # all → verification-evidence.json
python proofloop/cli.py proof-pack        # assembles proof-pack.json
python proofloop/cli.py status            # prints current status
python proofloop/cli.py reset             # clears session for a new scenario
```

---

## S01 Hero Scenario — Coupon Support

The primary demonstration scenario.

**Developer request:** "Add promotional coupon support to checkout."

**Seeded defect:** The coupon application lacks a floor guard.

```
subtotal = $50.00
coupon   = $75.00
result   = $50.00 - $75.00 = -$25.00   ← INVARIANT VIOLATION
```

**Key invariant:** Payment amount sent to payment service must always be >= 0.

**Adversarial finding:** The adversarial agent reads the Change Contract invariants
and notices that inv-01 ("payment >= 0") is not covered by any test. It inspects
the implementation and finds the missing floor guard.

**Repair:** Bob adds `max(Decimal("0.00"), subtotal - discount)` and a regression test.

**Final Proof Pack status:** VERIFIED (after 1 repair cycle)

---

## Workflow Diagram

```
Developer Request
       ↓
proofloop mode
  → generate Change Contract
  → Gate 1: developer approves
  → spawn parallel subagents:
      Architect  /  Test  /  Security  /  API Contract
  → read all findings
  → implement feature (with seeded defect)
       ↓
adversarial mode
  → read contract invariants
  → inspect implementation code
  → find: negative payment invariant violated
  → write adversarial-report.json
       ↓
Gate 2: developer reviews adversarial report
       ↓
proofloop mode (repair)
  → apply max(0) floor guard
  → add regression test
  → write repair-log.json
       ↓
verifier mode
  → python proofloop/cli.py verify --all
  → all checks pass
  → python proofloop/cli.py proof-pack
       ↓
Gate 3: developer reviews Proof Pack
       ↓
VERIFIED
```

---

## CheckoutLab

Minimal realistic FastAPI application.

| Component | Tech | Purpose |
|---|---|---|
| API | FastAPI | REST endpoints; auto-generates OpenAPI spec |
| Models | SQLAlchemy | ORM with SQLite |
| Schemas | Pydantic v2 | Request/response validation; mypy targets |
| Tests | pytest | Business invariant tests |
| Database | SQLite | Zero infrastructure dependency |

---

## Proof Pack Final Status

| Status | Meaning |
|---|---|
| `VERIFIED` | All blocking evidence requirements met |
| `VERIFIED_WITH_WARNINGS` | Blocking requirements met; non-blocking warnings exist |
| `FAILED` | One or more blocking requirements not met after max repair cycles |
| `INCOMPLETE` | Verification did not complete |
