# Benchmark Directory Structure

This directory contains the machine-readable benchmark scenario definitions for ProofLoop.

```
benchmark/
├── README.md               ← this file
├── scenarios/              ← ChangeContract definitions for S01-S05
│   ├── s01_coupon_support.json
│   ├── s02_payment_idempotency.json
│   ├── s03_api_contract.json
│   ├── s04_authentication_regression.json
│   └── s05_schema_migration.json
└── results/                ← future run artifacts for secondary scenarios
```

See [BENCHMARK.md](../BENCHMARK.md) for full scenario descriptions, invariants, and benchmark matrix.

