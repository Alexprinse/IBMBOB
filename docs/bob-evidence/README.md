# IBM Bob Evidence Log

This directory logs and organizes the authentic IBM Bob 2.0 task session evidence for the ProofLoop hackathon submission.

---

## Team Division of Bob Sessions

In adherence to hackathon rules, both team members conducted authentic IBM Bob development sessions.

### Team Member 1 — Bob Workflow Engineer
**Focus**: Bob orchestration, custom modes, skills, rules, and Proof Pack assembly.

| Session ID | Stage | Bob Mode | Action Description | Screenshot Reference |
|---|---|---|---|---|
| **A1** | Mode Configuration | `proofloop` | Configured `.bob/custom_modes.yaml` defining `proofloop`, `adversarial`, and `verifier` modes with strict tool permissions. | `docs/bob-evidence/member-1/01-modes-setup.png` |
| **A2** | Contract & Rules | `proofloop` | Authored `.bob/rules-proofloop/` and Change Contract skill (`.bob/skills/change-contract/SKILL.md`). | `docs/bob-evidence/member-1/02-change-contract.png` |
| **A3** | Adversarial Agent | `adversarial` | Executed adversarial analysis on CheckoutLab, discovering the -$25 negative payment defect (`af-01`). | `docs/bob-evidence/member-1/03-adversarial-finding.png` |
| **A4** | Proof Pack Assembly | `verifier` | Executed Proof Pack assembly skill (`.bob/skills/proof-pack/SKILL.md`) to verify evidence integrity. | `docs/bob-evidence/member-1/04-proof-pack.png` |

---

### Team Member 2 — Verification & Application Engineer
**Focus**: CheckoutLab application, verification CLI runners, dashboard, and benchmark scenarios.

| Session ID | Stage | Bob Mode | Action Description | Screenshot Reference |
|---|---|---|---|---|
| **B1** | CheckoutLab App | `proofloop` | Built FastAPI checkout service, SQLAlchemy models, and initial 27-test pytest suite. | `docs/bob-evidence/member-2/01-checkoutlab-app.png` |
| **B2** | CLI Verifiers | `verifier` | Implemented deterministic CLI tool wrappers for pytest, mypy, and ruff (`proofloop/verifiers/`). | `docs/bob-evidence/member-2/02-verifiers-cli.png` |
| **B3** | Dashboard Build | `proofloop` | Developed the static presentation dashboard (`dashboard/index.html`, `styles.css`, `app.js`, `serve.py`). | `docs/bob-evidence/member-2/03-dashboard.png` |
| **B4** | End-to-End Scenario | `verifier` | Ran complete S01 end-to-end loop: contract &rarr; challenge &rarr; repair &rarr; verification &rarr; proof pack. | `docs/bob-evidence/member-2/04-s01-verified.png` |

---

## Tooling Attribution
- **IBM Bob 2.0**: The primary workflow engine and pair programmer used for mode coordination, change contract generation, adversarial hypothesis reasoning, code repair, and skill execution.
- **Antigravity / Local Terminal**: Used for local test execution, static type checking, linter validation, and local dashboard server verification.

