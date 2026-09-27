# Adversarial Mode — Invariant Checking Protocol

## MANDATORY: Negative payment check

For ANY change that involves discount, coupon, price reduction, or order total calculation:

You MUST verify the following boundary condition:

```
What happens when discount_amount >= order_subtotal?
```

Specifically:
1. Find the calculation that produces the final order total or payment amount
2. Trace what happens when `discount_amount = order_subtotal + 0.01`
3. If the result is negative → this is a CRITICAL invariant violation
4. The payment amount sent to the payment service must NEVER be negative

This check is mandatory. It cannot be skipped.

### Why this is the most important check

A negative payment amount will cause one of:
- Payment service rejection with a cryptic error
- Payment service charging the customer a refund instead of a charge
- Silent data corruption in the order record

None of these are acceptable. The guard is always `max(Decimal("0.00"), calculated_total)`.

## MANDATORY: Test existence check

For each invariant in the Change Contract with `severity: "critical"` or `"high"`:

1. Find the test file(s) in `checkoutlab/tests/`
2. Search for a test that exercises that invariant
3. If no test exists → finding with `category: "missing_test"`

A test that checks "does the endpoint return 200?" does NOT count as testing a business invariant.

Example of a test that does NOT satisfy inv-01:
```python
def test_checkout_with_coupon():
    response = client.post("/checkout", json={...})
    assert response.status_code == 200  # This does NOT verify payment amount >= 0
```

Example of a test that DOES satisfy inv-01:
```python
def test_coupon_exceeding_subtotal_produces_non_negative_total():
    result = apply_coupon(subtotal=Decimal("50.00"), discount=Decimal("75.00"))
    assert result.final_total >= Decimal("0.00")
```

## Invariant check procedure

For each invariant in the contract:

1. Note the invariant description
2. Note the severity (critical | high | medium | low)
3. Find the specific test in `checkoutlab/tests/` that covers this invariant
4. If no specific test: create a finding with:
   - severity: high
   - category: missing_test
   - suggested_repair: "Add test for [invariant description]"

## Output

All findings go to `.proofloop/session/adversarial-report.json`.
