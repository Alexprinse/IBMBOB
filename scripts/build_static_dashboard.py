#!/usr/bin/env python3
"""Build static distribution for Vercel / GitHub Pages / Netlify.

Generates a standalone 'public' directory containing the dashboard HTML/CSS/JS,
the pre-recorded S01 hero session artifacts, and pre-computed /api/session responses.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path


def build() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    public_dir = repo_root / "public"
    dashboard_dir = repo_root / "dashboard"
    snapshot_dir = repo_root / "demo" / "session-snapshot"

    # Reset public dir
    if public_dir.is_dir():
        shutil.rmtree(public_dir)
    public_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy dashboard assets
    for item in dashboard_dir.glob("*"):
        if item.is_file() and item.suffix in (".html", ".css", ".js", ".ico", ".png", ".svg"):
            shutil.copy2(item, public_dir / item.name)

    # 2. Copy snapshot to demo/session-snapshot and .proofloop/session
    public_snapshot = public_dir / "demo" / "session-snapshot"
    public_session = public_dir / ".proofloop" / "session"
    public_snapshot.mkdir(parents=True, exist_ok=True)
    public_session.mkdir(parents=True, exist_ok=True)

    for f in snapshot_dir.glob("*.json"):
        shutil.copy2(f, public_snapshot / f.name)
        shutil.copy2(f, public_session / f.name)

    # 3. Create static /api/session and /api/run-status JSON endpoints
    def read_json(p: Path) -> dict:
        return json.loads(p.read_text(encoding="utf-8-sig"))

    contract_data = read_json(snapshot_dir / "change-contract.json")
    adv_data = read_json(snapshot_dir / "adversarial-report.json")
    repair_data = read_json(snapshot_dir / "repair-log.json")
    verif_data = read_json(snapshot_dir / "verification-evidence.json")
    pack_data = read_json(snapshot_dir / "proof-pack.json")

    api_payload = {
        "source": "snapshot",
        "source_dir": "demo/session-snapshot",
        "exists": True,
        "files_present": {
            "change_contract": True,
            "adversarial_report": True,
            "repair_log": True,
            "verification_evidence": True,
            "proof_pack": True,
        },
        "artifacts": {
            "change_contract": contract_data,
            "adversarial_report": adv_data,
            "repair_log": repair_data,
            "verification_evidence": verif_data,
            "proof_pack": pack_data,
        },
        "run_state": {
            "is_running": False,
            "stage": "complete",
            "message": "Verified S01 Proof Pack (Demo Snapshot)",
            "details": {
                "pack_id": pack_data.get("pack_id", "pp-s01-001"),
                "final_status": "VERIFIED",
            },
            "started_at": None,
            "completed_at": None,
            "error": None,
            "result": {
                "final_status": "VERIFIED",
            },
        },
    }

    api_dir = public_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    (api_dir / "session").write_text(json.dumps(api_payload, indent=2), encoding="utf-8")
    (api_dir / "run-status").write_text(json.dumps(api_payload["run_state"], indent=2), encoding="utf-8")

    print(f"[OK] Static distribution built in: {public_dir}")


if __name__ == "__main__":
    build()

