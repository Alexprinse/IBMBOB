# ProofLoop — Revised Implementation Plan v2

**Status:** planning — awaiting approval before any implementation  
**Repository state:** empty (only `.git/` directory + this plan file)  
**Last updated:** post design-review, incorporating all locked decisions

---

## 1. Executive Summary

ProofLoop is a closed-loop, evidence-backed developer workflow built visibly on IBM Bob 2.0.

The core thesis: AI-assisted development dramatically accelerates implementation, but leaves verification fragmented. ProofLoop replaces fragmented manual verification with a structured, contract-driven loop that produces a **Proof Pack** — a traceable evidence artefact proving a change is correct.

The loop:

```
Developer Intent
→ Change Contract
→ Parallel Impact Analysis
→ Bob Implementation
→ Adversarial Challenge
→ Deterministic Verification
→ Repair
→ Re-Verification
→ Proof Pack
```

**Primary demo scenario:**

A developer asks Bob to "Add promotional coupon support to checkout." The implementation contains a seeded invariant violation: a coupon discount exceeds the order subtotal, producing a negative payment amount ($50 − $75 = −$25). The Adversarial Agent catches this. Bob repairs it. Deterministic tests confirm the fix. The Proof Pack shows VERIFIED.

**Three layers:**

- **Layer A — IBM Bob IDE:** Primary engineering interaction. Developers use Bob to drive the entire loop. Custom modes, skills, subagents, AGENTS.md — all used visibly.
- **Layer B — ProofLoop Orchestration:** Change Contract schema, verification CLI, evidence collection, adversarial analysis, repair log, Proof Pack assembly.
- **Layer C — Web Dashboard:** Static HTML visualization of the live loop. Reads JSON artifacts. Shows pipeline stages, adversarial findings, and final Proof Pack.

**Two-person team:**
- **Team Member 1** — Bob Workflow Engineer: orchestration, custom modes, skills, Change Contract, adversarial agent, Proof Pack.
- **Team Member 2** — Verification/Application Engineer: CheckoutLab, deterministic verification CLI, tests, benchmark scenarios, dashboard.

---

## 2. Current Repository Assessment

**Path:** `/Users/shalem/IBMBOB`  
**Branch:** `main`  
**Remote:** none  
**Content:** empty — only `.git/` and `proofloop-plan.md`

**Bob configuration found in workspace:** none — must be created from scratch.

**Global Bob skills environment:** the user has a large globally-installed skills library at `~/.agents/skills/`. Several of these are directly relevant and can be referenced or adapted rather than reinvented:
- `adversarial-check` (already exists globally)
- `atlas-contract` (goal-integrity skill — related concept)
- `differential-review` (security-focused code review)
- `phase-gated-debugging` (enforces root cause before fix)
- `find-bugs` (finds bugs in branch changes)
- `requesting-code-review` and `receiving-code-review`

**Decision:** ProofLoop's custom skills are purpose-built for the workflow and reference but do not duplicate global skills.

---

## 3. IBM Bob 2.0 — Actual Configuration Architecture

### Confirmed configuration files (IBM Bob 2.0)

Based on actual Bob 2.0 documentation:

| File/Directory | Location | Purpose |
|---|---|---|
| `AGENTS.md` | Project root | Primary project context for all agents |
| `.bob/custom_modes.yaml` | Project root | Custom mode definitions (YAML) |
| `.bob/settings.json` | Project root | Tool permissions, allowed shell commands |
| `.bob/mcp.json` | Project root | Project-level MCP server configuration |
| `.bob/rules/` | Project root | General rules applied to all modes |
| `.bob/rules-{mode-slug}/` | Project root | Mode-specific rules and instructions |
| `.bob/skills/` | Project root | Project-local skill definitions |
| `.bobignore` | Project root | File access filter (gitignore syntax) |

### Custom mode YAML schema

```yaml
customModes:
  - slug: mode-slug
    name: 🔷 Mode Display Name
    description: One-line description
    roleDefinition: >-
      You are a ...
    whenToUse: Use for X tasks.
    customInstructions: |-
      Additional behavioral instructions.
    groups:
      - read
      - edit
      - command
      - skill
```

**Tool groups for ProofLoop modes:**

| Group | Meaning |
|---|---|
| `read` | Read files |
| `edit` | Write/modify files |
| `command` | Execute shell commands |
| `skill` | Activate skills |
| `browser` | Browser access (not needed for MVP) |

**Mode-specific rules:** Placed in `.bob/rules-{mode-slug}/`. Files loaded alphabetically. All `.md` and `.txt` files processed.

---

## 4. Problem and Market Gap

AI coding assistants generate code faster than teams can verify it. The gap is not speed — it is **evidence**.

When an AI implements a feature, there is no standard mechanism that:
1. Formalizes intent as a machine-readable contract before coding starts
2. Runs specialized analysis of risk across architecture, tests, security, and APIs
3. Adversarially challenges the generated output assuming it is wrong
4. Collects real, deterministic evidence from actual tools
5. Produces a traceable, auditable record that is human-readable

This gap causes rework, missed invariant violations, silent regressions, and AI-generated changes that cannot be justified to reviewers, security teams, or auditors.

**ProofLoop's answer:** Replace "the AI generated it" with "here is the evidence it is correct."

---

## 5. Why This Is Different

| Existing approach | ProofLoop |
|---|---|
| AI generates code | AI generates code under a verified contract |
| Developer manually reviews | Adversarial agent challenges before human review |
| Tests run in CI | Tests run as explicit, labeled contract evidence |
| Security is a separate process | Security agent is part of the pre-implementation analysis |
| API compatibility is a surprise in review | API agent analyzed it before the first line of code |
| The change has no formal record | Every change produces a Proof Pack |
| Bob is used to write code | Bob IS the entire workflow |

**The differentiator is not any single capability — it is the trinity:**

> **Change Contract + Adversarial Verification + Evidence-Backed Proof Pack**

---

## 6. MVP Scope

### In scope

- Repository scaffolding and Bob project configuration (AGENTS.md, `.bob/`, `.bobignore`)
- Three custom Bob modes: `proofloop`, `adversarial`, `verifier`
- Three custom Bob skills: `change-contract`, `adversarial-check`, `proof-pack`
- Mode-specific rules for each custom mode
- CheckoutLab synthetic application (FastAPI, SQLite, Pydantic, 20+ tests)
- Seeded invariant violation in S01 (negative payment amount)
- `proofloop` CLI tool (Python): `verify --tests`, `verify --types`, `verify --lint`, `proof-pack`, `status`
- Change Contract JSON schema (Pydantic-validated)
- Adversarial report JSON schema
- Repair log JSON schema
- Proof Pack JSON schema + assembler
- Web dashboard (static HTML/CSS/JS): pipeline visualization, adversarial finding card, Proof Pack summary
- Scenario S01 end-to-end run with real artifacts
- Scenarios S02–S05 as secondary benchmark
- Bob session screenshots from both team members
- README, ARCHITECTURE.md, BENCHMARK.md
- `.proofloop/session/` runtime directory for agent artifacts

### Required to win

- Visible multi-agent Bob activity in screenshots and video
- Real deterministic tool output in the Proof Pack (actual pytest results, actual mypy output)
- Adversarial finding that was caught, repaired, and re-verified — all documented
- Dashboard that visually communicates the BEFORE (broken) → REPAIR → AFTER (verified) arc
- Proof Pack summary card as the hero visual

---

## 7. Non-Goals

- SaaS platform, accounts, billing, multi-user support
- PostgreSQL or any database beyond SQLite
- CI/CD pipeline integration
- IDE plugin
- Mobile/responsive dashboard
- Real-time WebSocket dashboard updates (polling is sufficient)
- Performance benchmarking at scale
- External project management tool integration
- Scenarios S06–S10 for MVP (good for post-hackathon)
- Invented numerical benchmark results
- Any feature that cannot be explained in 10 seconds to a judge

---

## 8. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER A — IBM Bob IDE                                          │
│                                                                 │
│  Developer uses Bob in proofloop mode                           │
│  Bob generates Change Contract                                  │
│  Bob spawns parallel subagents (Architect/Test/Security/API)    │
│  Bob implements the change                                      │
│  Bob switches to adversarial mode                               │
│  Bob adversarially challenges the implementation                │
│  Bob applies repair                                             │
│  Bob switches to verifier mode                                  │
│  Bob invokes proofloop CLI for deterministic evidence           │
│  Bob assembles Proof Pack                                       │
│                                                                 │
│  Configuration:                                                 │
│  AGENTS.md / .bob/custom_modes.yaml / .bob/settings.json        │
│  .bob/rules-proofloop/ .bob/rules-adversarial/ .bob/rules-ver/  │
│  .bob/skills/change-contract/ adversarial-check/ proof-pack/    │
└────────────────────┬────────────────────────────────────────────┘
                     │ reads/writes artifacts
┌────────────────────▼────────────────────────────────────────────┐
│  LAYER B — ProofLoop Orchestration Layer                        │
│                                                                 │
│  .proofloop/session/                                            │
│    change-contract.json     ← generated by proofloop mode       │
│    architect-findings.json  ← generated by Architect subagent   │
│    test-findings.json       ← generated by Test subagent        │
│    security-findings.json   ← generated by Security subagent    │
│    api-findings.json        ← generated by API subagent         │
│    adversarial-report.json  ← generated by adversarial mode     │
│    repair-log.json          ← generated by repair agent         │
│    verification-evidence.json ← generated by proofloop CLI      │
│    proof-pack.json          ← assembled by proofloop CLI        │
│                                                                 │
│  proofloop/cli.py           ← CLI entry point                   │
│  proofloop/verifiers/       ← pytest / mypy / ruff / api-compat │
│  proofloop/schemas/         ← Pydantic schemas for all artifacts │
│  proofloop/assembler.py     ← assembles proof-pack.json         │
│                                                                 │
│  checkoutlab/               ← synthetic demo application        │
│    app/ tests/ migrations/  ← FastAPI, SQLite, Alembic           │
└────────────────────┬────────────────────────────────────────────┘
                     │ reads proof-pack.json
┌────────────────────▼────────────────────────────────────────────┐
│  LAYER C — Web Dashboard                                        │
│                                                                 │
│  dashboard/index.html       ← pipeline visualization            │
│  dashboard/app.js           ← reads JSON artifacts, renders UI  │
│  dashboard/styles.css       ← visual identity                   │
│  dashboard/serve.py         ← simple local HTTP server          │
│                                                                 │
│  Polls proof-pack.json every 2 seconds                          │
│  No backend required                                            │
└─────────────────────────────────────────────────────────────────┘
```

### Key architectural principles

1. **All agent communication is via JSON files** in `.proofloop/session/`. This makes agent handoffs inspectable, auditable, and judge-readable.

2. **The ProofLoop CLI is a real Python tool** that calls real tools (pytest, mypy, ruff). Never simulate output.

3. **The dashboard reads real artifacts.** Never hardcode demo data in the dashboard — it reads the JSON files produced by the actual run.

4. **Demo Mode uses a controlled seeded scenario.** The same real code path runs; the input scenario is fixed. No fabrication.

5. **Bob is the workflow engine, not just a code generator.** Every stage is initiated from within Bob.

---

## 9. IBM Bob Architecture — Detailed Design

### Bob directory structure for this project

```
IBMBOB/
├── AGENTS.md                              ← Project context for all agents
├── .bob/
│   ├── custom_modes.yaml                  ← Three custom modes
│   ├── settings.json                      ← Tool permissions
│   ├── rules/                             ← Rules for all modes
│   │   ├── 01-proofloop-principles.md
│   │   └── 02-evidence-standards.md
│   ├── rules-proofloop/                   ← Rules for proofloop mode
│   │   ├── 01-workflow.md
│   │   ├── 02-change-contract.md
│   │   └── 03-agent-coordination.md
│   ├── rules-adversarial/                 ← Rules for adversarial mode
│   │   ├── 01-adversarial-mindset.md
│   │   ├── 02-invariant-checking.md
│   │   └── 03-finding-format.md
│   ├── rules-verifier/                    ← Rules for verifier mode
│   │   ├── 01-evidence-collection.md
│   │   └── 02-proof-pack-assembly.md
│   └── skills/
│       ├── change-contract/
│       │   └── SKILL.md
│       ├── adversarial-check/
│       │   └── SKILL.md
│       └── proof-pack/
│           └── SKILL.md
└── .bobignore
```

### Custom modes (`.bob/custom_modes.yaml`)

#### Mode 1: `proofloop` — Lead Orchestrator

```yaml
- slug: proofloop
  name: 🔷 ProofLoop Orchestrator
  description: Drives the full ProofLoop workflow from intent to Proof Pack.
  roleDefinition: >-
    You are the ProofLoop Lead Orchestrator. Your role is to transform a
    developer's natural-language request into a structured Change Contract,
    coordinate specialized investigation agents, oversee implementation,
    and synthesize all findings into a Proof Pack. You demand evidence
    before declaring anything complete. You never accept "looks correct"
    as verification. Every claim must be backed by either a deterministic
    tool result or an explicit agent finding with a source.
  whenToUse: >-
    Use when starting a new ProofLoop workflow. The developer provides a
    change request, and this mode drives the entire loop from contract
    generation through to Proof Pack.
  customInstructions: |-
    1. Always start by generating a Change Contract JSON file.
    2. Show the contract to the developer and wait for approval before proceeding.
    3. Spawn parallel subagents for Architect, Test, Security, and API analysis.
    4. Read all agent findings before beginning implementation.
    5. After implementation, switch to adversarial mode.
    6. After adversarial findings are addressed, invoke the proofloop CLI.
    7. Assemble the Proof Pack only when all blocking checks pass.
    8. Write all session artifacts to .proofloop/session/.
  groups:
    - read
    - edit
    - command
    - skill
```

#### Mode 2: `adversarial` — Adversarial Challenger

```yaml
- slug: adversarial
  name: 🔴 Adversarial Agent
  description: Assumes the implementation is wrong. Hunts for invariant violations, edge cases, and security regressions.
  roleDefinition: >-
    You are the ProofLoop Adversarial Agent. Your job is to assume the
    implementation is potentially incorrect. You do not accept that
    passing tests are sufficient evidence of correctness. You hunt for
    invariant violations, edge cases, off-by-one errors, missing
    validations, security regressions, and scope creep. You read the
    Change Contract and ask: for each invariant listed, is it actually
    tested? You read the test code and ask: are these tests testing
    the right thing? For each finding you produce a specific remediation
    task that the Repair Agent can act on.
  whenToUse: >-
    Use after implementation is complete. Provide the Change Contract,
    implementation diff, and test results. Report every finding in the
    adversarial report format.
  customInstructions: |-
    1. Read the Change Contract invariants. For each one, verify it has a test.
    2. Read the implementation code. Look for: missing validation, boundary
       conditions, None/null handling, negative values, negative totals.
    3. Specifically test the negative-payment invariant for any checkout change.
    4. Read the test code. Assess whether tests test behavior or just structure.
    5. Write all findings to .proofloop/session/adversarial-report.json.
    6. Each finding must include: severity, category, description, code location,
       and a specific remediation task.
    7. Do NOT modify code. Do NOT write tests. Findings only.
  groups:
    - read
    - skill
```

#### Mode 3: `verifier` — Evidence Collector

```yaml
- slug: verifier
  name: ✅ ProofLoop Verifier
  description: Runs deterministic verification tools and assembles the Proof Pack.
  roleDefinition: >-
    You are the ProofLoop Verifier. Your job is to run deterministic
    verification tools and collect real evidence. You do not reason
    about correctness — you measure it. You run pytest, mypy, ruff, and
    the proofloop API compatibility checker. You record exact tool
    output: exit codes, test counts, error messages. You never
    summarize or paraphrase tool output — you capture it verbatim.
    You then assemble the Proof Pack with every piece of evidence labeled
    as either deterministic or LLM-reasoning.
  whenToUse: >-
    Use after repair is complete, or when the proofloop orchestrator
    requests verification. Runs all configured checks and writes
    verification-evidence.json and proof-pack.json.
  customInstructions: |-
    1. Run: python -m pytest checkoutlab/tests/ -v --tb=short --json-report
    2. Run: python -m mypy checkoutlab/ --strict
    3. Run: python -m ruff check checkoutlab/
    4. Run: python proofloop/cli.py verify --all
    5. Capture exact exit codes and output.
    6. Write verification-evidence.json with all results.
    7. Run: python proofloop/cli.py proof-pack to assemble the Proof Pack.
    8. Report final status: VERIFIED / VERIFIED_WITH_WARNINGS / FAILED.
  groups:
    - read
    - command
    - skill
```

### Bob settings (`.bob/settings.json`)

```json
{
  "tools": {
    "allowed": [
      "run_shell_command(python -m pytest*)",
      "run_shell_command(python -m mypy*)",
      "run_shell_command(python -m ruff*)",
      "run_shell_command(python proofloop/cli.py*)",
      "run_shell_command(git diff*)",
      "run_shell_command(git status*)",
      "run_shell_command(git log*)"
    ]
  }
}
```

### AGENTS.md — Project context

The AGENTS.md provides all agents with:
- ProofLoop workflow description
- Session artifact directory location (`.proofloop/session/`)
- Change Contract schema reference
- Proof Pack schema reference
- CheckoutLab architecture summary
- Verification CLI commands
- Evidence standards (deterministic vs LLM-reasoning distinction)
- Both team members' areas of ownership

### Subagents and parallel execution

The `proofloop` mode spawns four subagents in parallel after Change Contract approval:

| Subagent | Instruction | Output file |
|---|---|---|
| Architect Agent | Identify affected components, data flows, schema risks, architectural invariants | `architect-findings.json` |
| Test Agent | Identify test gaps, required tests, regression risks, existing coverage holes | `test-findings.json` |
| Security Agent | Identify auth implications, input validation risks, data exposure, OWASP categories | `security-findings.json` |
| API Contract Agent | Identify affected endpoints, breaking changes, backward compatibility risks | `api-findings.json` |

Each subagent receives: the Change Contract JSON + relevant source files via context mention.

Each subagent is prohibited from: writing code, modifying files, running shell commands.

**What runs in parallel:** The four analysis agents above.

**What runs sequentially:** Adversarial → Repair → Verify (these depend on each other's output).

### Human approval gates

| Gate | Description |
|---|---|
| Gate 1 | Developer reviews and approves the Change Contract before implementation begins |
| Gate 2 | Developer reviews the adversarial report before the repair phase begins |
| Gate 3 | Developer reviews the final Proof Pack before marking the change complete |

### Agent communication protocol

All agents communicate exclusively via JSON files in `.proofloop/session/`. No agent writes to another agent's file. The `proofloop` mode reads all files to synthesize.

```
.proofloop/session/
  change-contract.json          ← created by proofloop mode
  architect-findings.json       ← created by Architect subagent
  test-findings.json            ← created by Test subagent
  security-findings.json        ← created by Security subagent
  api-findings.json             ← created by API subagent
  adversarial-report.json       ← created by adversarial mode
  repair-log.json               ← created by repair agent
  verification-evidence.json    ← created by proofloop CLI
  proof-pack.json               ← assembled by proofloop CLI
```

---

## 10. Two-Person Work Split

### Team Member 1 — Bob Workflow Engineer

**Primary ownership:**

- AGENTS.md
- `.bob/custom_modes.yaml` (all three modes)
- `.bob/rules-proofloop/`, `.bob/rules-adversarial/`, `.bob/rules-verifier/`
- `.bob/skills/change-contract/SKILL.md`
- `.bob/skills/adversarial-check/SKILL.md`
- `.bob/skills/proof-pack/SKILL.md`
- `proofloop/schemas/` (Change Contract, adversarial report, repair log, Proof Pack Pydantic schemas)
- `proofloop/assembler.py` (Proof Pack assembly)
- `proofloop/cli.py` (CLI entry point + `proof-pack` and `status` commands)
- Scenario S01 Change Contract JSON (`benchmark/scenarios/s01_coupon_support.json`)
- Architecture documentation (`ARCHITECTURE.md`)
- Presentation slides

**Bob sessions that generate screenshot evidence:**

1. Session A1: Use proofloop mode to generate the S01 Change Contract from scratch
2. Session A2: Run adversarial mode against the seeded S01 implementation — find the negative payment invariant violation
3. Session A3: Demonstrate parallel subagent spawning for S01 impact analysis
4. Session A4: Run verifier mode to assemble the final Proof Pack for S01

---

### Team Member 2 — Verification/Application Engineer

**Primary ownership:**

- `checkoutlab/` (entire FastAPI application, models, services, tests)
- `checkoutlab/openapi_baseline.json` (captured before changes)
- Seeded defect in CheckoutLab S01 (negative payment calculation)
- `proofloop/verifiers/` (test_runner.py, type_checker.py, linter.py, api_compat.py)
- `proofloop/cli.py` `verify` subcommand implementation
- `dashboard/` (static HTML/CSS/JS)
- `benchmark/scenarios/` (S02–S05)
- `benchmark/results/` (populated from real runs)
- `BENCHMARK.md`
- `DEMO.md`
- Demo environment setup

**Bob sessions that generate screenshot evidence:**

1. Session B1: Use Bob (code or agent mode) to build CheckoutLab foundation with tests
2. Session B2: Use Bob to write the proofloop verification CLI verifiers
3. Session B3: Use Bob to build the dashboard HTML/JS
4. Session B4: Use Bob to run the full S01 scenario end-to-end and capture results

---

## 11. Change Contract Schema

### Schema (Pydantic, also representable as JSON Schema)

```python
class ChangeRequest(BaseModel):
    original_text: str
    requester: str

class FunctionalRequirement(BaseModel):
    id: str
    description: str

class AffectedComponent(BaseModel):
    name: str
    reason: str
    risk_level: Literal["low", "medium", "high", "critical"]

class Invariant(BaseModel):
    id: str
    description: str
    verification_method: Literal["test", "type_check", "lint", "schema_validation", "api_check", "manual_review"]
    criticality: Literal["must_pass", "should_pass", "informational"]

class EvidenceRequired(BaseModel):
    type: Literal["test_pass", "type_check_pass", "lint_pass", "schema_valid", "api_compatible", "security_check_pass", "regression_pass"]
    description: str
    is_blocking: bool

class ChangeContract(BaseModel):
    id: str
    version: str
    created_at: datetime
    status: Literal["draft", "approved", "in_progress", "challenged", "repaired", "verified", "failed"]
    request: ChangeRequest
    intent_summary: str
    functional_requirements: list[FunctionalRequirement]
    affected_components: list[AffectedComponent]
    invariants: list[Invariant]
    security_concerns: list[str]
    rollback_strategy: str
    evidence_required: list[EvidenceRequired]
```

### Example: S01 — Coupon support with negative-payment seeded defect

```json
{
  "id": "cc-s01",
  "version": "1.0",
  "created_at": "2025-01-15T10:00:00Z",
  "status": "approved",
  "request": {
    "original_text": "Add promotional coupon support to checkout.",
    "requester": "developer"
  },
  "intent_summary": "Allow customers to apply a promotional coupon code at checkout to receive a discount. Coupons have a code, discount type (percentage or fixed), value, expiry date, and usage limit.",
  "functional_requirements": [
    { "id": "fr-01", "description": "Checkout API accepts an optional coupon_code field" },
    { "id": "fr-02", "description": "Valid coupon reduces the order total" },
    { "id": "fr-03", "description": "Invalid or expired coupons return a descriptive 400 error" }
  ],
  "affected_components": [
    { "name": "checkout_service", "reason": "Primary checkout business logic", "risk_level": "high" },
    { "name": "order_model", "reason": "Schema must store coupon_code and discount_applied", "risk_level": "medium" },
    { "name": "payment_service", "reason": "Payment amount must reflect discounted total", "risk_level": "high" }
  ],
  "invariants": [
    {
      "id": "inv-01",
      "description": "Payment amount sent to payment service is always >= 0",
      "verification_method": "test",
      "criticality": "must_pass"
    },
    {
      "id": "inv-02",
      "description": "Order total after coupon application is always >= 0",
      "verification_method": "test",
      "criticality": "must_pass"
    },
    {
      "id": "inv-03",
      "description": "Coupon discount never exceeds the order subtotal",
      "verification_method": "test",
      "criticality": "must_pass"
    },
    {
      "id": "inv-04",
      "description": "Checkout flow without a coupon code is unaffected",
      "verification_method": "test",
      "criticality": "must_pass"
    },
    {
      "id": "inv-05",
      "description": "API response is backward compatible for requests without coupon_code",
      "verification_method": "api_check",
      "criticality": "must_pass"
    }
  ],
  "security_concerns": [
    "Coupon codes must be validated server-side only",
    "Invalid coupon code must not leak existence of other valid codes in error response"
  ],
  "rollback_strategy": "Feature flag: COUPON_SUPPORT_ENABLED. Set to false to disable without migration rollback.",
  "evidence_required": [
    { "type": "test_pass", "description": "All 5 invariant tests pass", "is_blocking": true },
    { "type": "type_check_pass", "description": "mypy passes on all modified files", "is_blocking": true },
    { "type": "lint_pass", "description": "ruff passes on all modified files", "is_blocking": true },
    { "type": "api_compatible", "description": "POST /checkout backward compatible for no-coupon requests", "is_blocking": true },
    { "type": "regression_pass", "description": "All existing checkout tests continue to pass", "is_blocking": true }
  ]
}
```

---

## 12. Verification Architecture

### Strict separation of evidence types

Every item in the Proof Pack carries an evidence category label. These must never be conflated.

| Category | Tools | Example |
|---|---|---|
| `deterministic` | Real tool output | `pytest` exit code + output, `mypy` error count, `ruff` violations |
| `llm_reasoning` | Bob agent analysis | Adversarial finding, architectural risk identification |

### ProofLoop CLI commands

```
python proofloop/cli.py verify --tests        → runs pytest, captures JSON report
python proofloop/cli.py verify --types        → runs mypy, captures output
python proofloop/cli.py verify --lint         → runs ruff, captures output
python proofloop/cli.py verify --api-compat   → diffs OpenAPI spec against baseline
python proofloop/cli.py verify --all          → all of the above → verification-evidence.json
python proofloop/cli.py proof-pack            → assembles proof-pack.json from all session files
python proofloop/cli.py status                → prints current contract status
python proofloop/cli.py reset                 → clears session for a new scenario
```

### Verification evidence schema

```json
{
  "verification_id": "ver-s01-002",
  "timestamp": "2025-01-15T11:30:00Z",
  "change_contract_id": "cc-s01",
  "cycle": 2,
  "results": [
    {
      "category": "deterministic",
      "tool": "pytest",
      "command": "python -m pytest checkoutlab/tests/ -v --tb=short",
      "exit_code": 0,
      "passed": 24,
      "failed": 0,
      "output_excerpt": "24 passed in 3.4s",
      "evidence_type": "test_pass"
    },
    {
      "category": "deterministic",
      "tool": "mypy",
      "command": "python -m mypy checkoutlab/ --strict",
      "exit_code": 0,
      "error_count": 0,
      "output_excerpt": "Success: no issues found in 8 source files",
      "evidence_type": "type_check_pass"
    },
    {
      "category": "deterministic",
      "tool": "ruff",
      "command": "python -m ruff check checkoutlab/",
      "exit_code": 0,
      "violation_count": 0,
      "output_excerpt": "All checks passed.",
      "evidence_type": "lint_pass"
    },
    {
      "category": "deterministic",
      "tool": "api_compat",
      "command": "python proofloop/cli.py verify --api-compat",
      "exit_code": 0,
      "breaking_changes": 0,
      "output_excerpt": "No breaking changes detected vs baseline.",
      "evidence_type": "api_compatible"
    }
  ],
  "summary": {
    "total_checks": 4,
    "passed": 4,
    "failed": 0,
    "warnings": 0,
    "overall_status": "PASS"
  }
}
```

---

## 13. Adversarial Architecture

### The Adversarial Agent's job

The adversarial mode is given:
- The Change Contract (invariants, requirements)
- The implementation diff
- The test results from the first verification run (if available)

It asks, for each invariant in the contract:

1. "Is this invariant actually tested?"
2. "Is the test testing the right thing?"
3. "What edge case can break this?"

For the S01 demo scenario, the adversarial agent is specifically instructed (via `.bob/rules-adversarial/01-adversarial-mindset.md`) to:

> For any change involving discount or price reduction, test the boundary condition where the discount equals or exceeds the total. Verify the payment amount cannot be negative.

This makes the S01 finding reliable and deterministic without being fabricated.

### Adversarial report schema

```json
{
  "report_id": "adv-s01-001",
  "timestamp": "2025-01-15T11:00:00Z",
  "change_contract_id": "cc-s01",
  "findings": [
    {
      "finding_id": "af-01",
      "severity": "critical",
      "category": "invariant_violation",
      "invariant_id": "inv-01",
      "title": "Negative payment amount when coupon exceeds subtotal",
      "description": "Current implementation applies coupon discount without checking that the discount amount does not exceed the order subtotal. Example: subtotal=$50, coupon=$75, computed total=-$25. A negative payment amount is sent to the payment service.",
      "code_location": "checkoutlab/app/services/checkout.py:line_approx",
      "evidence": "Mathematical: discount application is subtotal - discount_value with no floor(0) guard",
      "evidence_category": "llm_reasoning",
      "remediation_task": "Add validation: final_total = max(0, subtotal - discount_amount). Also add test: coupon discount > subtotal → total clamped to 0, not negative.",
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

### Repair-then-reverify loop

```
adversarial-report.json produced
        ↓
For each finding where is_blocking = true:
        ↓
   Repair Agent (runs inside proofloop mode) reads finding
   Applies targeted fix
   Appends to repair-log.json
        ↓
   proofloop CLI: verify --all
        ↓
   Check verification-evidence.json
   Did the specific invariant test pass?
        ↓
   YES → finding resolved
   NO  → repeat (max 3 cycles, then status = FAILED)
        ↓
All blocking findings resolved?
   YES → assemble Proof Pack → status = VERIFIED
   NO  → Proof Pack → status = FAILED
```

### Repair log schema

```json
{
  "repair_log_id": "rep-s01-001",
  "timestamp": "2025-01-15T11:15:00Z",
  "change_contract_id": "cc-s01",
  "repairs": [
    {
      "repair_id": "r-01",
      "addresses_finding": "af-01",
      "description": "Added floor guard to coupon application: final_total = max(0.0, subtotal - discount_amount)",
      "files_modified": ["checkoutlab/app/services/checkout.py"],
      "test_added": "test_coupon_exceeds_subtotal_clamps_to_zero",
      "reasoning": "Invariant inv-01 requires payment amount >= 0. The fix adds max(0) to the calculation and a regression test for the boundary condition."
    }
  ]
}
```

---

## 14. Proof Pack Design

### Final Proof Pack schema

```json
{
  "proof_pack_id": "pp-s01",
  "generated_at": "2025-01-15T11:45:00Z",
  "change_contract_id": "cc-s01",
  "original_request": "Add promotional coupon support to checkout.",
  "final_status": "VERIFIED",
  "summary": {
    "requirements_met": "3/3",
    "tests_passed": "24/24",
    "type_check": "PASS",
    "lint": "PASS",
    "api_compatibility": "PASS",
    "regression": "PASS",
    "adversarial_findings_total": 1,
    "adversarial_findings_resolved": 1,
    "adversarial_findings_unresolved": 0,
    "repair_cycles": 1,
    "residual_warnings": 0
  },
  "agents_involved": ["architect", "test", "security", "api_contract", "adversarial", "repair", "verifier"],
  "deterministic_evidence": [
    { "tool": "pytest", "result": "24/24 PASS", "evidence_type": "test_pass" },
    { "tool": "mypy", "result": "0 errors", "evidence_type": "type_check_pass" },
    { "tool": "ruff", "result": "0 violations", "evidence_type": "lint_pass" },
    { "tool": "api_compat", "result": "0 breaking changes", "evidence_type": "api_compatible" }
  ],
  "llm_evidence": [
    { "agent": "adversarial", "finding": "Negative payment invariant violation", "resolved": true }
  ],
  "changed_files": [
    "checkoutlab/app/services/checkout.py",
    "checkoutlab/app/models.py",
    "checkoutlab/app/schemas.py",
    "checkoutlab/tests/test_checkout.py"
  ],
  "residual_risks": [],
  "rollback_validated": true,
  "final_status_reason": "All 5 invariant tests pass. One adversarial finding (critical: negative payment) resolved in repair cycle 1. All deterministic checks pass."
}
```

### Proof Pack final status values

| Status | Meaning |
|---|---|
| `VERIFIED` | All blocking evidence requirements met, no unresolved blocking findings |
| `VERIFIED_WITH_WARNINGS` | All blocking requirements met; residual non-blocking warnings exist |
| `FAILED` | One or more blocking requirements not met |
| `INCOMPLETE` | Verification did not finish (tool error or loop limit reached) |

---

## 15. Web Dashboard — Visual Design

### Purpose

Visualize the ProofLoop loop for judges and developers. Reads JSON artifacts from `.proofloop/session/`. No backend.

### Visual identity

The dashboard is NOT a CI/CD status board. It is a story in three acts:

**Act 1: Intent** — What was asked, and what the contract requires  
**Act 2: Challenge** — What the adversarial agent found wrong  
**Act 3: Proof** — What evidence confirms the change is correct

### Pipeline stages (vertical scroll, dark theme)

```
┌─────────────────────────────────────────────────┐
│  CHANGE REQUEST                    [COMPLETE]   │
│  "Add promotional coupon support to checkout"   │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│  CHANGE CONTRACT                   [COMPLETE]   │
│  3 requirements · 5 invariants · 2 components   │
│  [KEY INVARIANT] Payment amount must be >= 0    │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│  IMPACT ANALYSIS                   [COMPLETE]   │
│  ⚡ Architect · 🧪 Test · 🔒 Security · 📡 API   │
│  checkout_service [HIGH] · payment_service [HIGH]│
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│  IMPLEMENTATION                    [COMPLETE]   │
│  4 files modified                               │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐  ← HERO SECTION
│  ADVERSARIAL CHECK                [FAILED ❌]   │
│                                                 │
│  ❌ INVARIANT VIOLATION (CRITICAL)              │
│                                                 │
│  subtotal:        $50.00                        │
│  coupon discount: $75.00                        │
│  computed total:  −$25.00                       │
│                                                 │
│  A negative payment amount was sent to the      │
│  payment service.                               │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│  REPAIR                            [COMPLETE]   │
│  Added max(0, total) guard in checkout_service  │
│  Added invariant test: coupon > subtotal → $0   │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│  VERIFICATION                      [PASS ✅]    │
│  ✓ pytest  24/24                                │
│  ✓ mypy    0 errors                             │
│  ✓ ruff    0 violations                         │
│  ✓ api     no breaking changes                  │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐  ← PROOF PACK HERO
│  ✅ VERIFIED                                    │
│                                                 │
│  Requirements:      3/3                         │
│  Tests:             24/24                       │
│  Type check:        PASS                        │
│  API compatibility: PASS                        │
│  Adversarial:       1 found · 1 resolved        │
│  Repair cycles:     1                           │
│  Residual risks:    0                           │
│                                                 │
│  Not just code. Evidence.                       │
└─────────────────────────────────────────────────┘
```

### Technical implementation

- Dark background (`#0a0a0a`), white text, red for failures (`#ff3b30`), green for verified (`#30d158`), amber for warnings (`#ff9f0a`)
- Stage cards with subtle border and shadow — NOT colored status lights
- The adversarial finding card is the largest element on the page
- Numbers in the Proof Pack summary are large typography (48px+)
- The tagline "Not just code. Evidence." is the final element

### Data loading

```javascript
// poll every 2 seconds during demo
async function refreshData() {
  const [contract, adversarial, repair, evidence, pack] = await Promise.all([
    fetch('/session/change-contract.json').then(r => r.json()).catch(() => null),
    fetch('/session/adversarial-report.json').then(r => r.json()).catch(() => null),
    fetch('/session/repair-log.json').then(r => r.json()).catch(() => null),
    fetch('/session/verification-evidence.json').then(r => r.json()).catch(() => null),
    fetch('/session/proof-pack.json').then(r => r.json()).catch(() => null),
  ]);
  renderPipeline({ contract, adversarial, repair, evidence, pack });
}
setInterval(refreshData, 2000);
```

---

## 16. CheckoutLab Architecture

### Design principles

- Small enough to understand in 3 minutes of code reading
- Complex enough to have real cross-component risks
- Real FastAPI application with real tests
- SQLite eliminates all infrastructure dependencies
- Pydantic models mean mypy has real work to do
- pytest covers genuine business invariants, not just HTTP status codes

### Directory structure

```
checkoutlab/
├── app/
│   ├── main.py               ← FastAPI app, router registration
│   ├── database.py           ← SQLAlchemy + SQLite setup
│   ├── models.py             ← SQLAlchemy ORM models
│   ├── schemas.py            ← Pydantic request/response models
│   └── services/
│       ├── checkout.py       ← checkout business logic (discount calculation here)
│       ├── payment.py        ← payment stub (validates amount >= 0)
│       ├── inventory.py      ← inventory reservation stub
│       └── notification.py   ← async notification stub
│   └── api/
│       └── routes/
│           ├── checkout.py   ← POST /checkout
│           └── orders.py     ← GET /orders/{id}
├── migrations/               ← Alembic migration scripts
│   └── versions/
├── tests/
│   ├── conftest.py           ← pytest fixtures, test database setup
│   ├── test_checkout.py      ← checkout business logic tests
│   ├── test_payment.py       ← payment service tests
│   ├── test_invariants.py    ← business invariant tests (key file)
│   └── test_api.py           ← API integration tests
├── openapi_baseline.json     ← snapshot before any S01 changes
├── pyproject.toml
└── requirements.txt
```

### Seeded defect for S01

In `checkoutlab/app/services/checkout.py`, the initial coupon implementation will contain:

```python
# SEEDED DEFECT: no floor guard
final_total = order_subtotal - discount_amount
```

The correct implementation after repair:

```python
# FIXED: payment amount cannot be negative
final_total = max(Decimal("0.00"), order_subtotal - discount_amount)
```

The test that catches it:

```python
def test_coupon_exceeding_subtotal_does_not_produce_negative_total():
    # subtotal $50, coupon $75 → total should be $0, not -$25
    result = apply_coupon(subtotal=Decimal("50.00"), discount=Decimal("75.00"))
    assert result.final_total >= Decimal("0.00")
    assert result.final_total == Decimal("0.00")
```

### Initial test suite (before S01 changes)

20 tests covering:
- Checkout creates an order correctly
- Payment amount matches order total
- Insufficient inventory blocks checkout
- Invalid products block checkout
- Order total calculation (single item, multiple items)
- Payment service rejects negative amounts
- Payment service rejects zero amounts
- API returns 200 for valid checkout
- API returns 400 for invalid input
- Database rollback on payment failure

These tests all pass before S01 changes and must continue passing after (regression suite).

---

## 17. Benchmark Scenarios

All scenarios target CheckoutLab. S01 is the hero demo scenario.

### S01 — Coupon Support (HERO DEMO)

| Field | Value |
|---|---|
| Request | "Add promotional coupon support to checkout." |
| Seeded defect | No floor guard: discount > subtotal → negative total |
| Adversarial finding | Negative payment invariant violation |
| Expected ProofLoop outcome | FAILED on first pass → VERIFIED after 1 repair cycle |
| Demo use | Primary 3-minute demo scenario |
| Judge explanation | "$50 order, $75 coupon = −$25 payment. Bob caught it." |

### S02 — Payment Retry Regression

| Field | Value |
|---|---|
| Request | "Add retry with exponential backoff to the payment service." |
| Hidden risk | Retry without idempotency key can charge customer multiple times |
| Seeded defect | No idempotency key on retry calls |
| Expected outcome | FAILED (idempotency test added by test agent, fails on implementation) |

### S03 — API Contract Break

| Field | Value |
|---|---|
| Request | "Rename the 'total_price' field to 'order_total' in the checkout response." |
| Hidden risk | Breaking change for API consumers using old field name |
| Seeded defect | Old field removed entirely instead of aliased |
| Expected outcome | FAILED (OpenAPI diff against baseline detects breaking change) |

### S04 — Authentication Security Regression

| Field | Value |
|---|---|
| Request | "Add API key authentication to the checkout endpoint." |
| Hidden risk | Middleware applied globally breaks unauthenticated health check |
| Seeded defect | Health check endpoint returns 401 after change |
| Expected outcome | FAILED (regression test for health check fails) |

### S05 — Schema Migration Incompatibility

| Field | Value |
|---|---|
| Request | "Add a line_items field to order records." |
| Hidden risk | Existing rows become null-value inconsistent without backfill migration |
| Seeded defect | Migration adds column but does not backfill existing rows |
| Expected outcome | FAILED (schema validation detects nullable constraint violation) |

### S06–S10 (secondary — post-MVP)

- S06: Tax calculation boundary value bug
- S07: Dependency upgrade API surface change
- S08: Inventory reservation persistence across restart
- S09: Duplicate notification on retry
- S10: Currency rounding float vs Decimal

---

## 18. Metrics

### What we measure

| Metric | Definition | Source |
|---|---|---|
| Contract generation time | Seconds from request to Change Contract written | Timestamps in change-contract.json |
| Risk findings pre-implementation | Count of findings in architect + security + api files | Count items in findings JSONs |
| Tests identified before coding | Count of test requirements in test-findings.json | Count items |
| Seeded defects detected | Count of seeded defects found by adversarial agent | Manual check against scenario definitions |
| Repair cycles | Count of adversarial → repair → verify iterations | Count entries in repair-log.json |
| Tests passed (post-repair) | Count from verification-evidence.json | Direct from JSON |
| Evidence items in Proof Pack | Count of deterministic evidence entries | Count items in proof-pack.json |
| Total workflow time | Contract approval to Proof Pack complete | Timestamps |

### Baseline (manual developer workflow for S01)

Without ProofLoop, a developer would:

1. Implement coupon support without a formal contract
2. Write tests based on what they remembered to test
3. Likely miss the discount-exceeds-subtotal edge case (it requires explicit boundary thinking)
4. Submit a PR — reviewer might catch it in code review, or might not
5. No adversarial challenge
6. No formal Proof Pack

**Baseline misses:** The negative-payment invariant violation — the exact bug that ProofLoop catches.

### Note on metrics

Numerical results must NOT be invented. The BENCHMARK.md will be filled in after real runs against CheckoutLab.

---

## 19. 3-Minute Demo Storyboard

### Act 1: Problem + Contract (0:00–0:50)

| Time | What happens |
|---|---|
| 0:00–0:08 | Dashboard open, all stages grey/empty. Tagline: "AI generates code. ProofLoop proves it." |
| 0:08–0:20 | Developer types into Bob (proofloop mode): "Add promotional coupon support to checkout." |
| 0:20–0:40 | Bob generates Change Contract. Dashboard Stage 2 lights up. Camera holds on the Change Contract — specifically on the invariant: **"Payment amount must be >= 0"**. Narrator: "Before writing a line of code, ProofLoop defines what must be true." |
| 0:40–0:50 | Developer approves the contract. Narrator: "Four agents analyze the change in parallel." |

### Act 2: Investigation + Adversarial Finding (0:50–1:50)

| Time | What happens |
|---|---|
| 0:50–1:10 | Dashboard Stage 3 (IMPACT ANALYSIS) + Stage 4 agent cards light up simultaneously. Four agent cards: Architect / Test / Security / API. Bob spawning subagents visible. |
| 1:10–1:20 | Brief cut: Bob implements the coupon feature. Dashboard Stage 5 (IMPLEMENTATION) lights up. |
| 1:20–1:50 | **HERO MOMENT begins.** Adversarial mode activates. Dashboard Stage 6 card appears: **"❌ INVARIANT VIOLATION — CRITICAL"**. Numbers animate in: subtotal $50.00 / coupon $75.00 / computed total **−$25.00**. Narrator: "The adversarial agent assumed the implementation was wrong. It was." |

### Act 3: Repair + Proof Pack (1:50–3:00)

| Time | What happens |
|---|---|
| 1:50–2:10 | Dashboard Stage 7 (REPAIR) appears. "Bob modified checkout calculation: added max(0, total) guard." Repair log entry visible. |
| 2:10–2:30 | Verification runs. Dashboard Stage 8 (VERIFICATION) lights up green: pytest 24/24 ✓ / mypy 0 errors ✓ / ruff clean ✓ / API compat ✓ |
| 2:30–2:55 | **PROOF PACK hero card animates in.** Large text: **✅ VERIFIED**. Numbers appear: Requirements 3/3 / Tests 24/24 / Adversarial: 1 found, 1 resolved / Repair cycles: 1 / Residual risks: 0. |
| 2:55–3:00 | Final screen holds on Proof Pack. Tagline: **"Not just code. Evidence."** |

### Demo reliability

**Development mode:** Live Bob session running the real workflow against CheckoutLab.

**Demo mode (for video and live backup):** 
- Pre-run the S01 scenario and save all JSON artifacts to `demo/session-snapshot/`
- Dashboard `serve.py` can be pointed at either live `.proofloop/session/` or `demo/session-snapshot/`
- The demo video shows the real Bob session but uses pre-computed artifacts for dashboard display speed
- The JSON artifacts in the snapshot are REAL — generated by an actual ProofLoop run

**Backup plan if Bob is slow in live demo:** Switch to the recorded video of the Bob session while talking through the dashboard stages in real time.

---

## 20. Repository Structure

```
IBMBOB/
├── AGENTS.md                               ← Project context for all Bob agents
├── README.md                               ← Overview, quick start, demo instructions
├── ARCHITECTURE.md                         ← System design with diagrams
├── BENCHMARK.md                            ← Benchmark scenarios and results
├── DEMO.md                                 ← 3-minute demo script
├── .gitignore
├── .bobignore
│
├── .bob/
│   ├── custom_modes.yaml                   ← proofloop + adversarial + verifier modes
│   ├── settings.json                       ← Allowed tools/commands
│   ├── rules/
│   │   ├── 01-proofloop-principles.md      ← Evidence standards, artifact formats
│   │   └── 02-session-artifacts.md         ← Session directory, file conventions
│   ├── rules-proofloop/
│   │   ├── 01-workflow.md
│   │   ├── 02-change-contract.md
│   │   └── 03-agent-coordination.md
│   ├── rules-adversarial/
│   │   ├── 01-adversarial-mindset.md
│   │   ├── 02-invariant-checking.md        ← Explicit: check negative-payment invariant
│   │   └── 03-finding-format.md
│   ├── rules-verifier/
│   │   ├── 01-evidence-collection.md
│   │   └── 02-proof-pack-assembly.md
│   └── skills/
│       ├── change-contract/
│       │   └── SKILL.md
│       ├── adversarial-check/
│       │   └── SKILL.md
│       └── proof-pack/
│           └── SKILL.md
│
├── proofloop/                              ← Layer B: orchestration Python package
│   ├── __init__.py
│   ├── cli.py                              ← CLI entry point
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── change_contract.py              ← Pydantic schema
│   │   ├── adversarial_report.py           ← Pydantic schema
│   │   ├── repair_log.py                   ← Pydantic schema
│   │   ├── verification_evidence.py        ← Pydantic schema
│   │   └── proof_pack.py                   ← Pydantic schema
│   ├── verifiers/
│   │   ├── __init__.py
│   │   ├── test_runner.py                  ← wraps pytest
│   │   ├── type_checker.py                 ← wraps mypy
│   │   ├── linter.py                       ← wraps ruff
│   │   └── api_compat.py                   ← diffs OpenAPI against baseline
│   └── assembler.py                        ← builds proof-pack.json
│
├── .proofloop/                             ← Runtime session data (in .gitignore)
│   └── session/
│       ├── change-contract.json
│       ├── architect-findings.json
│       ├── test-findings.json
│       ├── security-findings.json
│       ├── api-findings.json
│       ├── adversarial-report.json
│       ├── repair-log.json
│       ├── verification-evidence.json
│       └── proof-pack.json
│
├── checkoutlab/                            ← Layer B: synthetic demo application
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services/
│   │       ├── checkout.py                 ← SEEDED DEFECT for S01 here
│   │       ├── payment.py
│   │       ├── inventory.py
│   │       └── notification.py
│   │   └── api/
│   │       └── routes/
│   │           ├── checkout.py
│   │           └── orders.py
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_checkout.py
│   │   ├── test_payment.py
│   │   ├── test_invariants.py              ← Invariant tests (the ones that catch the bug)
│   │   └── test_api.py
│   ├── openapi_baseline.json               ← API spec snapshot before S01 changes
│   ├── pyproject.toml
│   └── requirements.txt
│
├── benchmark/
│   ├── scenarios/
│   │   ├── s01_coupon_support.json
│   │   ├── s02_payment_retry.json
│   │   ├── s03_api_contract.json
│   │   ├── s04_auth_regression.json
│   │   └── s05_schema_migration.json
│   ├── results/                            ← populated after real runs
│   │   └── .gitkeep
│   └── README.md
│
├── dashboard/                              ← Layer C: static web visualization
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── serve.py                            ← python -m http.server wrapper with CORS
│
├── demo/
│   ├── session-snapshot/                   ← Pre-recorded real artifacts for reliable demo
│   │   ├── change-contract.json
│   │   ├── adversarial-report.json
│   │   ├── repair-log.json
│   │   ├── verification-evidence.json
│   │   └── proof-pack.json
│   └── screenshots/
│       ├── member1/                        ← TM1 Bob session screenshots
│       └── member2/                        ← TM2 Bob session screenshots
│
├── docs/
│   ├── architecture-diagrams.md
│   └── slides/
│
└── .env.example
```

---

## 21. Hackathon Submission Strategy

### Judging criteria alignment

| Criterion | How ProofLoop addresses it | Key artefact |
|---|---|---|
| **Application of Technology** | Bob is the workflow engine — not used behind the scenes. All three custom modes, skills, subagents, AGENTS.md, rules all visibly active | `.bob/` directory, AGENTS.md, Bob screenshots |
| **Presentation** | 3-minute demo has a single unforgettable moment: AI found −$25 bug | Demo video, dashboard |
| **Business Value** | Closes the verification gap in AI-assisted development; produces evidence not just code | Proof Pack, benchmark results |
| **Originality** | Change Contract + Adversarial Verification + Proof Pack is a genuinely new pattern | ARCHITECTURE.md, dashboard |

### Screenshot evidence from both team members

Both team members must have real Bob session screenshots. The work split is designed so each person has 4 distinct Bob sessions to screenshot.

**Team Member 1 screenshots to capture:**
- A1: proofloop mode generating the Change Contract for S01
- A2: adversarial mode finding the negative payment invariant violation
- A3: parallel subagent spawning (four agents in parallel)
- A4: verifier mode assembling the Proof Pack

**Team Member 2 screenshots to capture:**
- B1: Bob building CheckoutLab with tests
- B2: Bob writing the proofloop verification CLI
- B3: Bob building the dashboard
- B4: Bob running the full S01 end-to-end scenario

---

## 22. Security

### What must never be committed

- API keys or cloud credentials of any kind
- Database passwords
- Personal data
- Client or company-confidential data

### Repository practices

`.gitignore` must include:
```
.env
*.env
.env.*
!.env.example
.proofloop/session/
__pycache__/
*.pyc
*.db
*.sqlite
*.sqlite3
.DS_Store
```

`.bobignore` must include:
```
.env
*.env
.env.*
*.db
*.sqlite
*.sqlite3
```

### CheckoutLab data

CheckoutLab uses only synthetic test data. No real payment data, no real personal information.

---

## 23. Technical Risks

| Risk | Severity | Likelihood | Impact |
|---|---|---|---|
| Bob adversarial mode does not reliably find the seeded defect | HIGH | LOW | Demo fails |
| proofloop CLI tool errors mid-session break the demo | HIGH | LOW | Demo fails |
| Dashboard does not update in time for demo pacing | MEDIUM | LOW | Demo looks manual |
| pytest-json-report not available or incompatible | MEDIUM | LOW | Verification evidence collection breaks |
| mypy is too strict and fails on CheckoutLab before the defect is added | MEDIUM | MEDIUM | Verification looks wrong |
| API compat diff gives false positives on minor spec changes | MEDIUM | MEDIUM | Proof Pack shows false FAILED |
| OpenAPI spec baseline is not stable before S01 changes | MEDIUM | MEDIUM | API compat check unreliable |
| Bob session is slow (>30 seconds per agent step) | HIGH | MEDIUM | Demo pacing breaks |

---

## 24. Mitigations

| Risk | Mitigation |
|---|---|
| Adversarial mode misses seeded defect | Rules file `.bob/rules-adversarial/02-invariant-checking.md` explicitly instructs: "For any change involving discount/price: verify payment amount cannot be negative." This makes the finding reliable without fabrication. |
| CLI errors break demo | Fault-tolerant assembler: missing session files produce warnings, not exceptions. Provide a `demo` flag that uses session-snapshot/ instead of live session. |
| Dashboard update timing | Poll every 2 seconds. Test in demo environment before recording video. |
| pytest-json-report unavailable | Use `pytest --tb=short -v` and parse stdout with regex as fallback. Both outputs are deterministic. |
| mypy too strict | Start with `mypy checkoutlab/ --ignore-missing-imports` rather than `--strict`. Add strict incrementally. |
| API compat false positives | Use simple JSON key comparison of Pydantic model fields instead of full OpenAPI diff tool. More reliable, same demonstration value. |
| OpenAPI baseline instability | Capture baseline BEFORE writing any S01 code. Lock it in `openapi_baseline.json`. |
| Bob session slowness | Pre-record Bob session. Use real output files from recording. Show video of Bob session in demo while demo dashboard renders live from saved artifacts. |

---

## 25. Implementation Phases

### Phase 0 — Foundation and First End-to-End Slice

**Owner:** Both team members  
**Goal:** Prove the concept works end-to-end before building anything else

Steps:
1. Repository scaffold (README, .gitignore, .bobignore, .env.example)
2. AGENTS.md (minimal, enough to run S01)
3. Bob custom modes (`.bob/custom_modes.yaml`) — all three modes
4. Bob rules files (`.bob/rules-proofloop/`, `.bob/rules-adversarial/`, `.bob/rules-verifier/`)
5. Bob skills (change-contract, adversarial-check, proof-pack)
6. CheckoutLab core: FastAPI app, SQLite, Pydantic models, 20 initial tests, all passing
7. proofloop Python package: schemas (Pydantic) for all 5 artifact types
8. proofloop CLI: `verify --tests` and `verify --types` commands
9. Seeded defect in checkout_service.py
10. End-to-end S01 run in Bob WITHOUT dashboard — artifacts produced
11. **FIRST MILESTONE CHECKPOINT**

### Phase 1 — Adversarial Loop

**Owner:** Team Member 1 (adversarial) + Team Member 2 (verification CLI)  
**Goal:** Make the adversarial finding + repair + re-verify loop real

Steps:
12. Adversarial mode rules tuned for negative-payment finding
13. `adversarial-report.json` produced by adversarial mode
14. Repair log schema + repair agent behavior
15. `verify --lint` command (ruff)
16. `verify --api-compat` command (baseline JSON diff)
17. `proof-pack` command (assembler)
18. Complete S01 loop: contract → agents → implement → adversarial → repair → verify → proof pack

### Phase 2 — Dashboard

**Owner:** Team Member 2  
**Goal:** Make the loop visible for judges

Steps:
19. `dashboard/serve.py` local HTTP server
20. `dashboard/styles.css` (dark theme, visual identity)
21. `dashboard/app.js` (polling, stage rendering)
22. `dashboard/index.html` (pipeline structure)
23. Dashboard reads live `.proofloop/session/` artifacts
24. Adversarial finding card (the hero visual)
25. Proof Pack summary card

### Phase 3 — Secondary Benchmark

**Owner:** Team Member 2  
**Goal:** Demonstrate ProofLoop generalizes to multiple scenarios

Steps:
26. CheckoutLab baseline stable (20+ tests, all clean)
27. Scenario S02 (payment retry) — run against ProofLoop
28. Scenario S03 (API contract break) — run against ProofLoop
29. Scenario S04 (auth regression) — run against ProofLoop
30. Scenario S05 (schema migration) — run against ProofLoop
31. BENCHMARK.md filled in with real results

### Phase 4 — Submission Polish

**Owner:** Both team members  
**Goal:** Repository is hackathon-submission-ready

Steps:
32. Demo session snapshot saved (`demo/session-snapshot/`)
33. Screenshots from all 8 Bob sessions captured and organized
34. README final pass
35. ARCHITECTURE.md with Mermaid diagrams
36. Presentation slides
37. 3-minute demo video recorded
38. Repository public on GitHub
39. Final security check: no credentials, no sensitive data

---

## BUILD ORDER

1. Repo scaffold (README, .gitignore, .bobignore, .env.example)
2. AGENTS.md (working draft)
3. `.bob/custom_modes.yaml` (all three modes)
4. `.bob/settings.json` (tool permissions)
5. `.bob/rules-proofloop/` (all 3 rule files)
6. `.bob/rules-adversarial/` (all 3 rule files — especially invariant-checking.md)
7. `.bob/rules-verifier/` (both rule files)
8. `.bob/skills/change-contract/SKILL.md`
9. `.bob/skills/adversarial-check/SKILL.md`
10. `.bob/skills/proof-pack/SKILL.md`
11. `proofloop/schemas/` (all 5 Pydantic schemas)
12. `checkoutlab/` core — FastAPI app + models + database + routes
13. `checkoutlab/tests/` — 20 initial tests, all passing
14. `checkoutlab/openapi_baseline.json` — captured now, before any changes
15. Seeded defect added to `checkoutlab/app/services/checkout.py`
16. `proofloop/cli.py` with `verify --tests` and `verify --types`
17. **First end-to-end milestone: S01 in Bob, no dashboard**
18. Tune adversarial mode rules to ensure negative-payment finding fires
19. `proofloop/verifiers/linter.py` + `api_compat.py`
20. `proofloop/assembler.py` + `proof-pack` CLI command
21. Complete S01 loop: full artifacts in `.proofloop/session/`
22. `dashboard/serve.py`
23. `dashboard/styles.css`
24. `dashboard/app.js` + `index.html`
25. Dashboard reads live artifacts — adversarial finding card renders correctly
26. Proof Pack summary card renders correctly
27. `demo/session-snapshot/` populated from real S01 run
28. Scenarios S02–S05 run and documented
29. BENCHMARK.md with real results
30. Screenshots from all team member Bob sessions
31. README + ARCHITECTURE.md + DEMO.md final versions
32. Slides
33. Demo video
34. Repository public, final security review

---

## FIRST END-TO-END SLICE

**Target:** After build order items 1–17

The smallest implementation that proves the concept:

1. Developer opens Bob in `proofloop` mode
2. Types: "Add promotional coupon support to checkout."
3. Bob activates the `change-contract` skill and generates `change-contract.json` for S01
4. Developer approves the contract
5. Bob spawns at least ONE subagent (Architect Agent) — produces `architect-findings.json`
6. Bob implements the coupon feature in CheckoutLab (with the seeded defect present)
7. Bob switches to `adversarial` mode
8. Adversarial mode reads the contract and implementation → produces `adversarial-report.json` with the negative-payment finding
9. Repair agent (inside proofloop mode) fixes the defect
10. `python proofloop/cli.py verify --tests` runs pytest → all 24 tests pass
11. `python proofloop/cli.py verify --types` runs mypy → 0 errors
12. `python proofloop/cli.py proof-pack` produces `proof-pack.json` with status VERIFIED

**This is the first end-to-end slice.** Dashboard is not required for this milestone. The JSON artifacts are the proof.

---

## DO NOT BUILD YET

Until the first end-to-end slice is complete and working, do NOT build:

- Web dashboard (build after slice is working)
- Scenarios S02–S05 (S01 only until first slice passes)
- `verify --api-compat` command (S03 needs it; S01 demo does not)
- Alembic migration tooling (CheckoutLab SQLite schema can be created directly for MVP)
- BENCHMARK.md with results (fill in from real runs)
- Scenarios S06–S10 (explicitly post-hackathon)
- Presentation slides (Phase 4)
- Demo video (Phase 4)
- Mobile-responsive dashboard
- WebSocket real-time updates
- Any integration beyond the local filesystem
- Performance or load testing

---

## FINAL MVP DEFINITION

ProofLoop is hackathon-demo ready when ALL of the following are true:

### Functional completeness

- [ ] `proofloop` mode in Bob generates a Change Contract for a natural-language request
- [ ] At least two subagents run and produce findings files
- [ ] Bob implements a change in CheckoutLab
- [ ] `adversarial` mode finds the seeded negative-payment invariant violation in S01
- [ ] Repair agent fixes the defect
- [ ] `proofloop verify --all` runs and produces real tool output
- [ ] `proofloop proof-pack` assembles a valid `proof-pack.json`
- [ ] Proof Pack shows `VERIFIED` status with 1 repair cycle documented

### Evidence quality

- [ ] Proof Pack contains real pytest output (not mocked)
- [ ] Proof Pack contains real mypy output (not mocked)
- [ ] Adversarial finding is labeled `llm_reasoning`
- [ ] Deterministic tool results are labeled `deterministic`
- [ ] At least one invariant test added during the repair cycle passes

### IBM Bob integration

- [ ] All three custom modes active and used in S01
- [ ] AGENTS.md is present and meaningful
- [ ] At least two custom skills activated during the workflow
- [ ] At least one subagent spawned in parallel

### Dashboard

- [ ] Dashboard renders all 9 pipeline stages
- [ ] Adversarial finding card shows the −$25 invariant violation
- [ ] Proof Pack summary card shows VERIFIED with real numbers
- [ ] Dashboard reads live `proof-pack.json` (not hardcoded)

### Reliability

- [ ] S01 scenario end-to-end run is reproducible
- [ ] `demo/session-snapshot/` contains real artifacts from at least one successful run
- [ ] Dashboard works when served from `dashboard/serve.py`
- [ ] 3-minute demo script exists and has been rehearsed

### Submission

- [ ] Repository is public on GitHub
- [ ] No credentials or sensitive data in any committed file
- [ ] Screenshots from both team members in `demo/screenshots/`
- [ ] README contains working setup instructions (<15 minutes from clone to demo)
- [ ] ARCHITECTURE.md explains the system with diagrams
