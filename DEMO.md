# ProofLoop — 3-Minute Demo Video Script

**Target Duration**: 3 minutes (180 seconds)  
**Hero Scenario**: S01 — Promotional Coupon Support  
**Theme**: *"AI generates code. ProofLoop proves it."*

---

## Screen & Audio Timeline

| Timestamp | Stage | Visual Action | Narration Script |
|---|---|---|---|
| **0:00–0:08** | **The Hook** | Dashboard full-screen hero banner. Tagline visible: *"AI generates code. ProofLoop proves it."* | *"AI-assisted coding is fast—but how do you know the code is actually correct? AI generates code. ProofLoop proves it."* |
| **0:08–0:40** | **Change Contract** | Switch to IBM Bob in `proofloop` mode. Show developer request: `"Add promotional coupon support to checkout."` Scroll to generated Change Contract card in dashboard. Highlight `inv-01`. | *"We ask IBM Bob to add promotional coupon support to our checkout service. Instead of blindly writing code, Bob first commits to a machine-readable Change Contract. It identifies functional requirements and a non-negotiable business invariant: the customer's payment amount must never be negative."* |
| **0:40–1:10** | **Investigation & Architecture** | Show multi-agent investigation: Architect, Security, and API subagent findings in Bob terminal. Workflow ribbon advancing: `Intent → Contract → Implement`. | *"Four specialized Bob subagents analyze the blast radius across SQLAlchemy models, payment services, and API schemas before a single line of application code is touched. Every requirement has a formal verification method mapped upfront."* |
| **1:10–1:20** | **Implementation** | Show CheckoutLab `checkout.py` coupon discount logic. | *"Bob implements the coupon logic: percentage and fixed discounts in CheckoutLab. The code looks clean, type hints match, and basic happy-path unit tests pass."* |
| **1:20–1:50** | **The WOW Moment (Hero Finding)** | Switch to Bob `adversarial` mode. Focus camera on the Dashboard **Adversarial Hero Card** (`af-01`). Show the math callout box: **Subtotal $50, Coupon $75 &rarr; -$25.00 payment**. | *"Now comes the breakthrough: ProofLoop switches to Adversarial Mode. The adversarial agent assumes the implementation is broken and deliberately hunts for boundary violations. And it catches a critical defect: if an order subtotal is $50 and a customer enters a $75 coupon, the checkout charges -$25.00! Invariant inv-01 is breached. The store pays the customer."* |
| **1:50–2:15** | **Repair & Invariant Test** | Show Repair Agent log (`rp-01`) in dashboard and `checkoutlab/app/services/checkout.py`. Highlight `max(Decimal('0.00'), subtotal - discount_amount)` and regression test `test_invariants.py`. | *"ProofLoop doesn't just flag the defect—the repair agent patches it with a mathematical floor guard and adds an invariant regression test that permanently prevents negative billing."* |
| **2:15–2:40** | **Deterministic Verification** | Terminal run or dashboard card: `python proofloop/cli.py verify --all`. Show exact exit codes: `pytest PASS (27/27)`, `mypy PASS (0 errors)`, `ruff PASS (0 violations)`. | *"Next, deterministic verification executes real tools. No LLM hallucinations or paraphrasing. pytest runs 27 real tests—all pass. mypy reports 0 type errors. ruff reports 0 lint violations. Every exit code is 0."* |
| **2:40–3:00** | **Proof Pack Verdict** | Zoom in on Proof Pack hero card: **`VERIFIED`**. Show Evidence Audit Matrix table with green badges. | *"Finally, the Proof Pack assembler compiles the cryptographically auditable evidence artifact. Verdict: VERIFIED. ProofLoop closes the verification gap. Not just code. Evidence."* |

---

## Rehearsal Checklist

1. **Dashboard Local URL**: `http://localhost:8080` (run `python dashboard/serve.py`).
2. **Terminal Command Sequence**:
   ```bash
   # 1. Reset / inspect state
   python proofloop/cli.py status

   # 2. Run deterministic verification
   python proofloop/cli.py verify --all

   # 3. Assemble Proof Pack
   python proofloop/cli.py proof-pack
   ```
3. **Screen Resolution**: 1920x1080 (1080p) or 2560x1440 at 16:9 ratio.
4. **Browser Zoom**: Set browser zoom to 100% or 110% so all monospace badges and math values (`$50 - $75 = -$25`) are crisp and prominent.

