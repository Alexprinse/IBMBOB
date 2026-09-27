# ProofLoop

**Evidence-backed developer workflow built on IBM Bob 2.0.**

> *"Every AI-assisted code change should prove itself before it is considered complete."*

---

## 1. The Problem

AI-assisted coding has drastically accelerated code generation, but **verification remains dangerously fragmented**. 

Large language models frequently generate implementations that look syntactically elegant and pass basic happy-path unit tests, yet subtly violate fundamental business invariants, leak security permissions, or introduce silent data incompatibilities. Developers are left with a false sense of security—reviewing code for plausibility rather than correctness.

---

## 2. The Solution: ProofLoop

ProofLoop closes the verification gap by replacing *"the AI generated the code"* with a closed, evidence-backed loop:

```
Developer Intent
      ↓
Change Contract        (Machine-readable specification of what must be true)
      ↓
Implementation         (Application code written to satisfy requirements)
      ↓
Adversarial Challenge  (Assumes implementation is broken; hunts for invariant violations)
      ↓
Defect Discovery       (Identifies counterexamples and edge conditions)
      ↓
Repair                 (Applies mathematical guards and invariant regression tests)
      ↓
Deterministic Verify   (Real tool execution: pytest, mypy, ruff exit codes)
      ↓
Proof Pack             (Traceable, cryptographically structured evidence artifact)
      ↓
VERIFIED
```

Every ProofLoop run produces a **Proof Pack** (`proof-pack.json`) containing deterministic tool outputs and audit items. The final status is strictly computed from tool exit codes and resolved findings: **VERIFIED**, **VERIFIED_WITH_WARNINGS**, **FAILED**, or **INCOMPLETE**.

---

## 3. The Hero Scenario: S01 Coupon Support

In our primary demonstration scenario (`s01_coupon_support.json`), a developer requests promotional coupon support for the CheckoutLab e-commerce service:

```
Developer Prompt: "Add promotional coupon support to checkout."
```

### The Invariant
- **`inv-01`**: *"The payment amount charged to the customer must never be negative (&ge; $0.00)."*

### The Seeded Defect
The initial implementation subtracts the discount from the order subtotal without a boundary guard:
```python
# Unchecked subtraction
final_total = order_subtotal - discount_amount
```

### The Adversarial Breakthrough
ProofLoop's **Adversarial Agent** challenges the implementation with boundary conditions and uncovers the critical breach:
```text
Subtotal: $50.00
Coupon:   $75.00
Result:  -$25.00   ← CRITICAL INVARIANT VIOLATION (Store pays customer!)
```

### The Repair & Deterministic Verification
1. The **Repair Agent** patches the checkout logic with a strict floor guard:
   ```python
   final_total = max(Decimal("0.00"), order_subtotal - discount_amount)
   ```
2. Adds regression test `test_payment_never_negative_when_coupon_exceeds_subtotal` to `checkoutlab/tests/test_invariants.py`.
3. The **Verifier** executes real tools:
   - `pytest`: **27/27 passed** (exit code 0)
   - `mypy`: **0 errors** (exit code 0)
   - `ruff`: **0 violations** (exit code 0)
4. The assembler seals the **Proof Pack** with status: **`VERIFIED`**.

---

## 4. How IBM Bob 2.0 Powers ProofLoop

IBM Bob 2.0 serves as the agentic workflow engine for ProofLoop:

- **Custom Modes (`.bob/custom_modes.yaml`)**:
  - `proofloop`: Lead orchestrator; generates Change Contracts and coordinates subagent analysis.
  - `adversarial`: Invariant hunter; assumes the implementation is broken and deliberately crafts counterexamples.
  - `verifier`: Evidence auditor; runs deterministic verification tools and builds the Proof Pack.
- **Project Skills (`.bob/skills/`)**:
  - `change-contract`: Formulates machine-readable contracts from natural language.
  - `adversarial-check`: Audits code diffs against declared business invariants.
  - `proof-pack`: Validates session evidence and triggers deterministic assembly.
- **Rule Enforcement (`.bob/rules-*/`)**:
  - Prohibits agents from marking tasks complete without deterministic tool proof.
  - Strict evidence separation: LLM reasoning is never conflated with deterministic tool exit codes.

*Note on Tooling Attribution*: IBM Bob 2.0 is the interactive AI workflow driver and pair programmer. Local execution environments (Antigravity/terminal) execute real compilers, linters, test runners, and the local dashboard server.

---

## 5. Repository Structure

```
IBMBOB/
├── AGENTS.md                   ← Bob project context & mode definitions
├── ARCHITECTURE.md             ← Three-layer architectural specification
├── BENCHMARK.md                ← Benchmark matrix (S01–S05) & evidence rules
├── DEMO.md                     ← 3-minute video presentation script
├── .bob/                       ← IBM Bob 2.0 configuration
│   ├── custom_modes.yaml       ← proofloop, adversarial, verifier modes
│   ├── settings.json           ← Tool permissions
│   ├── rules-proofloop/        ← ProofLoop mode rules
│   ├── rules-adversarial/      ← Adversarial mode rules
│   ├── rules-verifier/         ← Verifier mode rules
│   └── skills/                 ← Project-local skills
├── proofloop/                  ← Orchestration package
│   ├── cli.py                  ← CLI entry point (verify, proof-pack, benchmark)
│   ├── schemas/                ← Pydantic schemas for all artifacts
│   ├── verifiers/              ← Real tool wrappers (pytest, mypy, ruff)
│   └── assembler.py            ← Proof Pack assembly logic
├── checkoutlab/                ← Synthetic demo application (FastAPI + SQLite)
│   ├── app/                    ← Models, schemas, checkout services
│   └── tests/                  ← Pytest test suite (27 unit & invariant tests)
├── benchmark/scenarios/        ← S01–S05 scenario definitions
├── dashboard/                  ← Static HTML/CSS/JS visual presentation layer
│   ├── index.html              ← Pipeline stages, hero card, audit table
│   ├── styles.css              ← High-contrast dark engineering theme
│   ├── app.js                  ← 2s polling & artifact renderer
│   └── serve.py                ← Local HTTP server with CORS
├── demo/session-snapshot/      ← Pre-recorded verified S01 session artifacts
└── docs/bob-evidence/          ← Team member Bob session documentation
```

---

## 6. Quick Start

### Prerequisites
- Python 3.11+
- IBM Bob 2.0

### Setup
```bash
git clone https://github.com/Alexprinse/IBMBOB.git
cd IBMBOB
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### Run Tests Directly
```bash
pytest checkoutlab/tests/ -v
```

### Execute ProofLoop CLI
```bash
# Inspect session status
python proofloop/cli.py status

# Run deterministic verification tools (pytest, mypy, ruff)
python proofloop/cli.py verify --all

# Assemble the final Proof Pack
python proofloop/cli.py proof-pack

# Inspect the benchmark matrix (S01-S05)
python proofloop/cli.py benchmark
```

### Launch the Visual Dashboard
```bash
python dashboard/serve.py
# Open http://localhost:8080 in your browser
# (or: cd dashboard && python serve.py)
```

---

## 7. Team & Attribution

- **Team Member 1 (Bob Workflow Engineer)**: Mode configuration, skills, Change Contract, adversarial workflow, Proof Pack assembler.
- **Team Member 2 (Verification / Application Engineer)**: CheckoutLab service, deterministic verifiers CLI, visual dashboard, benchmark scenarios.

---

## 8. License

MIT
