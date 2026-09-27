# ProofLoop — Hackathon Live Presentation Guide

This guide explains how to present the **Live Session** option during the IBM Bob 2.0 hackathon demo.

---

## 1. Setup (Before You Present)

1. **Start the Dashboard Server**:
   ```bash
   python dashboard/serve.py --port 8080
   ```
2. **Arrange Split Screen**:
   - **Left Half**: Terminal window (with venv activated).
   - **Right Half**: Browser showing `http://localhost:8080/`.
3. **Verify Settings**:
   - Source dropdown is set to **`Live Session (.proofloop/session)`**.
   - If previous artifacts are visible, click **Reset** in the top navigation (or press `R` on your keyboard) to return to the clean awaiting state.

---

## 2. Presentation Options

You have two presentation modes depending on your pitching style:

### Option A: Paced Automatic Demo (Recommended)
Run:
```bash
python proofloop/cli.py demo --delay 2.0
```
This automatically steps through each stage with a 2-second pause, giving you time to speak while the dashboard live-updates.

### Option B: Interactive Step-by-Step Demo
Run:
```bash
python proofloop/cli.py demo --step
```
This pauses at every single stage and waits for you to press `[Enter]` before continuing, allowing complete control over your spoken narrative.

---

## 3. Step-by-Step Presentation Script

| Step & Terminal Output | Dashboard Visual Transition | What to Tell the Judges |
|---|---|---|
| **0. Initial State**<br>`python proofloop/cli.py reset` | All cards show `AWAITING EVIDENCE`. | *"ProofLoop is evidence-backed. We never fake results or show verified state before real tools run."* |
| **1. Intent & Change Contract**<br>`>> [STAGE 1: PROOFLOOP MODE]` | Contract card locks in with raw intent and 3 non-negotiable invariants (`inv-01`). Stage 2 switches to `HUNTING INVARIANTS...` with active radar animation. | *"The developer asked to 'add promotional coupon support'. ProofLoop converts this into a machine-readable Change Contract with invariant `inv-01`: payment must never be negative."* |
| **2. Adversarial Challenge**<br>`>> [STAGE 2: ADVERSARIAL MODE]` | Hero card reveals the $-\$25$ defect breakdown with red `VIOLATION IDENTIFIED` badge! Stage 3 enters `REPAIR IN PROGRESS...` spinner. | *"Now IBM Bob switches to adversarial mode. It deliberately hunts for edge cases where the contract fails. Here, it discovers that a \$75 coupon on a \$50 cart results in -\$25 unchecked charge."* |
| **3. Repair Cycle**<br>`>> [STAGE 3: REPAIR CYCLE]` | Repair card displays the floor guard implementation and passing regression test. Stage 4 enters `RUNNING VERIFICATION...` spinner. | *"ProofLoop applies the remediation: a floor guard `max(0, subtotal - discount)` and writes an invariant regression test."* |
| **4. Deterministic Verifiers**<br>`>> [STAGE 4: VERIFIER MODE]` | 3 tool cards turn green with exit code `0` (`pytest: 27/27 passed`, `mypy: 0 errors`, `ruff: 0 violations`). Stage 5 enters `ASSEMBLING...`. | *"Crucial distinction: LLM claims are not verification. ProofLoop executes real deterministic tools—pytest, mypy, and ruff—capturing exact process exit codes."* |
| **5. Proof Pack Assembly**<br>`FINAL STATUS: VERIFIED` | Proof Pack card locks in with `VERIFIED` status, SHA-256 fingerprint, and segregated deterministic vs LLM reasoning evidence table. | *"Finally, the assembler compiles the auditable Proof Pack. The change is officially VERIFIED with complete traceability."* |

---

## 4. Key Takeaway to Emphasize

> **"AI code generation without verification creates invisible liability. ProofLoop closes the verification loop by pairing adversarial reasoning with deterministic tool evidence."**

