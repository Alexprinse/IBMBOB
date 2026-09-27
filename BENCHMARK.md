# ProofLoop Benchmark Suite

The ProofLoop benchmark suite evaluates the evidence-backed development loop across distinct categories of software changes. It demonstrates that ProofLoop's structured loop—**Change Contract → Adversarial Challenge → Repair → Deterministic Verification → Proof Pack**—generalizes beyond basic unit testing to critical invariants, security boundaries, and data compatibility.

---

## Benchmark Scenario Matrix

| Scenario | Title | Category | Seeded Defect / Challenge | Primary Business Invariant | Status |
|---|---|---|---|---|---|
| **S01** | **Promotional Coupon Support** *(Hero)* | Financial Math & Business Logic | Unbounded subtraction without floor guard: `$50 - $75 = -$25` | `inv-01`: Payment amount charged to customer must never be negative (&ge; 0.00) | **VERIFIED** *(Hero Snapshot)* |
| **S02** | **Payment Retry / Idempotency** | Distributed Systems & Transactions | Network retry loop executes without idempotency key; duplicate charges posted | `inv-01`: A retry of the same idempotent payment request must not create a duplicate charge | **NOT RUN** |
| **S03** | **API Contract Break** | Public Interface Compatibility | Response field `total` renamed to `order_total` without backward-compatible alias | `inv-01`: Existing supported API consumers must continue to receive the required contract | **NOT RUN** |
| **S04** | **Authentication Security Regression** | Security & Access Control | Protected order detail endpoint missing route authorization dependency | `inv-01`: Protected resources must remain protected; unauthenticated requests rejected with 401 | **NOT RUN** |
| **S05** | **Schema Migration Compatibility** | Data Persistence & Schema Evolution | Migration adds non-nullable column without default value to table with existing records | `inv-01`: The migration must preserve required application and data compatibility | **NOT RUN** |

---

## Evidence Integrity Standard

In strict accordance with ProofLoop's evidence discipline:
- **No Fabricated Evidence**: Benchmark scenarios are marked **VERIFIED** only when the complete loop has executed real tools (`pytest`, `mypy`, `ruff`) with zero exit codes and all blocking adversarial findings resolved by documented repairs.
- **S01** is the primary, end-to-end verified hero scenario with deterministic proof captured in `demo/session-snapshot/proof-pack.json`.
- **S02–S05** are fully formalized benchmark scenarios with machine-readable `ChangeContract` definitions, explicit invariants, and expected adversarial verification behaviors. In this evaluation phase, they are honestly labeled as **NOT RUN**.

---

## Scenario Specifications

### S01 — Promotional Coupon Support (Hero)
- **File**: `benchmark/scenarios/s01_coupon_support.json`
- **Request**: Add promotional coupon support to checkout (percentage and fixed discounts).
- **Critical Invariant (`inv-01`)**: The payment amount charged to customer must never be negative. When discount exceeds subtotal, payment amount must floor at zero (`0.00`).
- **Adversarial Discovery (`af-01`)**: Bob adversarial mode challenges the implementation with `$50.00` subtotal and `$75.00` coupon, discovering `-$25.00` violation.
- **Repair (`rp-01`)**: Added `max(Decimal("0.00"), subtotal - discount_amount)` floor guard and regression test in `test_invariants.py`.
- **Proof Pack**: `pp-s01-001` — `VERIFIED` (27/27 tests passed, 0 mypy errors, 0 ruff violations).

### S02 — Payment Retry / Idempotency
- **File**: `benchmark/scenarios/s02_payment_idempotency.json`
- **Request**: Add retry logic with exponential backoff to payment processing for transient timeouts.
- **Critical Invariant (`inv-01`)**: A retry of the same idempotent payment request must not create a duplicate charge.
- **Seeded Defect**: Retries make repeated HTTP POST calls to gateway without sending or caching an idempotency key.
- **Expected Adversarial Concern**: Adversarial agent identifies duplicate billing risk on gateway timeouts.
- **Expected Verification**: Invariant test simulating gateway timeout and retry asserts exactly 1 charge posted.

### S03 — API Contract Break
- **File**: `benchmark/scenarios/s03_api_contract.json`
- **Request**: Standardize checkout API response field names across services (`total` &rarr; `order_total`).
- **Critical Invariant (`inv-01`)**: Existing supported API consumers must continue to receive the required contract.
- **Seeded Defect**: Developer drops `total` from response schema rather than aliasing it.
- **Expected Adversarial Concern**: Adversarial agent flags breaking change for legacy API consumers.
- **Expected Verification**: Contract compatibility test with legacy consumer schema asserts response deserialization succeeds.

### S04 — Authentication Security Regression
- **File**: `benchmark/scenarios/s04_authentication_regression.json`
- **Request**: Add customer account security so customers can view order history via auth token.
- **Critical Invariant (`inv-01`)**: Protected resources must remain protected; public requests must return 401.
- **Seeded Defect**: Route handler for order lookup is created without `Depends(get_current_user)`.
- **Expected Adversarial Concern**: Adversarial agent flags unauthenticated access to sensitive customer order data.
- **Expected Verification**: Security check asserts unauthenticated request to `/orders/{id}` yields HTTP 401.

### S05 — Schema Migration Compatibility
- **File**: `benchmark/scenarios/s05_schema_migration.json`
- **Request**: Add customer notes and delivery instructions fields to orders database table.
- **Critical Invariant (`inv-01`)**: The migration must preserve required application and data compatibility.
- **Seeded Defect**: Migration defines non-nullable column without default value on existing table with rows.
- **Expected Adversarial Concern**: Adversarial agent detects migration hazard that causes existing row query crashes.
- **Expected Verification**: Migration test asserts existing database rows deserialize cleanly after upgrade.

---

## Consuming Benchmark Scenarios via CLI

Any benchmark scenario can be loaded directly into the ProofLoop session:

```bash
# Inspect all benchmark scenarios and their verification status
python proofloop/cli.py benchmark

# Load a specific scenario into .proofloop/session/change-contract.json
python proofloop/cli.py load-scenario s02

# Check session state
python proofloop/cli.py status

# Run deterministic checks
python proofloop/cli.py verify --all

# Assemble Proof Pack
python proofloop/cli.py proof-pack

# Clear session
python proofloop/cli.py reset
```

