# ProofLoop

**Evidence-backed developer workflow built on IBM Bob 2.0.**

> Every AI-assisted code change should prove itself before it is considered complete.

---

## What is ProofLoop?

ProofLoop transforms the AI-assisted development workflow from:

> "The AI generated the code."

to:

> "Here is the evidence the change is correct."

The workflow:

```
Developer Intent
→ Change Contract    (what must be true)
→ Impact Analysis    (four parallel agents)
→ Implementation     (Bob writes the code)
→ Adversarial Check  (Bob assumes it's wrong)
→ Repair             (Bob fixes what it found)
→ Verification       (real deterministic tools)
→ Proof Pack         (traceable evidence artifact)
```

The hero scenario: A developer asks for coupon support. The implementation
produces a negative payment amount. The adversarial agent catches it.
Bob repairs it. The Proof Pack proves it is fixed.

---

## Architecture

Three layers:

| Layer | Purpose |
|---|---|
| **A — IBM Bob IDE** | Primary engineering interaction; custom modes, skills, subagents |
| **B — ProofLoop Orchestration** | Change Contract, CLI verification, Proof Pack assembly |
| **C — Web Dashboard** | Visual pipeline; reads JSON artifacts from Layer B |

See [ARCHITECTURE.md](ARCHITECTURE.md) for full design.

---

## Quick Start

### Prerequisites

- Python 3.11+
- IBM Bob 2.0

### Setup

```bash
git clone https://github.com/<your-org>/IBMBOB.git
cd IBMBOB
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### Run CheckoutLab tests (verify baseline)

```bash
source .venv/bin/activate
pytest checkoutlab/tests/ -v
```

### Run a full ProofLoop verification cycle

```bash
# From within IBM Bob in proofloop mode, or directly from CLI:
python proofloop/cli.py verify --all
python proofloop/cli.py proof-pack
python proofloop/cli.py status
```

### Run the S01 demo scenario

See [DEMO.md](DEMO.md) for the step-by-step 3-minute demo script.

### Start the dashboard

```bash
cd dashboard && python serve.py
# open http://localhost:8080
```

---

## Repository Structure

```
IBMBOB/
├── AGENTS.md                   ← Bob project context
├── .bob/                       ← Bob configuration
│   ├── custom_modes.yaml       ← proofloop, adversarial, verifier modes
│   ├── settings.json           ← tool permissions
│   ├── rules-proofloop/        ← proofloop mode rules
│   ├── rules-adversarial/      ← adversarial mode rules
│   ├── rules-verifier/         ← verifier mode rules
│   └── skills/                 ← project-local skills
├── proofloop/                  ← orchestration layer
│   ├── cli.py                  ← verify, proof-pack, status, reset
│   ├── schemas/                ← Pydantic schemas for all artifacts
│   ├── verifiers/              ← pytest, mypy, ruff, api-compat wrappers
│   └── assembler.py            ← Proof Pack assembly
├── .proofloop/session/         ← runtime artifacts (gitignored)
├── checkoutlab/                ← synthetic demo application
│   ├── app/                    ← FastAPI + SQLAlchemy + SQLite
│   └── tests/                  ← pytest test suite
├── benchmark/                  ← scenarios and results
├── dashboard/                  ← static HTML/CSS/JS visualization
├── demo/                       ← session snapshots and screenshots
└── docs/                       ← architecture, bob-evidence
```

---

## Team

**Team Member 1** — Bob Workflow Engineer  
Owns: orchestration, custom modes, skills, Change Contract, adversarial workflow, Proof Pack

**Team Member 2** — Verification/Application Engineer  
Owns: CheckoutLab, verification CLI, tests, dashboard, benchmark scenarios

---

## License

MIT
