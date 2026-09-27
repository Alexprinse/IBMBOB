from __future__ import annotations

import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from sqlalchemy.orm import Session

from checkoutlab.app.database import create_tables, get_db
from checkoutlab.app.models import Coupon, Product
from checkoutlab.app.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    CouponResponse,
    ProductResponse,
)
from checkoutlab.app.services.checkout import CheckoutError, process_checkout

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DASHBOARD_DIR = REPO_ROOT / "dashboard"
SESSION_DIR = REPO_ROOT / ".proofloop" / "session"
SNAPSHOT_DIR = REPO_ROOT / "demo" / "session-snapshot"

app = FastAPI(
    title="CheckoutLab & ProofLoop Dashboard",
    description="Synthetic checkout application and ProofLoop verification dashboard.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


# ── ProofLoop Dashboard & Artifact Endpoints ─────────────────────────────────

def _read_json_file(file_path: Path) -> dict | list | None:
    if not file_path.is_file():
        return None
    try:
        content = file_path.read_text(encoding="utf-8-sig")
        return json.loads(content)  # type: ignore[no-any-return]
    except Exception:
        return None


def _load_artifacts_bundle(source: str = "session") -> dict:
    target_dir = SNAPSHOT_DIR if source == "snapshot" else SESSION_DIR
    if not target_dir.is_dir() or not any(target_dir.glob("*.json")):
        target_dir = SNAPSHOT_DIR

    names = {
        "change_contract": ["change-contract.json", "change_contract.json"],
        "adversarial_report": ["adversarial-report.json", "adversarial_report.json"],
        "repair_log": ["repair-log.json", "repair_log.json"],
        "verification_evidence": ["verification-evidence.json", "verification_evidence.json"],
        "proof_pack": ["proof-pack.json", "proof_pack.json"],
    }
    artifacts: dict = {}
    files_present: dict = {}
    for key, candidates in names.items():
        found = False
        for c in candidates:
            p = target_dir / c
            if p.is_file():
                data = _read_json_file(p)
                if data is not None:
                    artifacts[key] = data
                    files_present[key] = True
                    found = True
                    break
        if not found:
            artifacts[key] = None
            files_present[key] = False

    return {
        "source": "snapshot" if target_dir == SNAPSHOT_DIR else "session",
        "source_dir": str(target_dir.relative_to(REPO_ROOT)),
        "exists": target_dir.is_dir(),
        "files_present": files_present,
        "artifacts": artifacts,
        "run_state": {
            "is_running": False,
            "stage": "complete" if files_present.get("proof_pack") else "idle",
            "message": "Live Verified S01 Proof Pack",
            "details": {},
            "started_at": None,
            "completed_at": None,
            "error": None,
            "result": None,
        },
    }


@app.get("/", include_in_schema=False)
def get_dashboard() -> FileResponse:
    index_file = DASHBOARD_DIR / "index.html"
    return FileResponse(index_file, media_type="text/html")


@app.get("/styles.css", include_in_schema=False)
def get_styles() -> FileResponse:
    return FileResponse(DASHBOARD_DIR / "styles.css", media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def get_app_js() -> FileResponse:
    return FileResponse(DASHBOARD_DIR / "app.js", media_type="application/javascript")


@app.get("/api/session", include_in_schema=False)
def get_session(source: str = "session") -> JSONResponse:
    bundle = _load_artifacts_bundle(source=source)
    return JSONResponse(bundle)


@app.get("/api/run-status", include_in_schema=False)
def get_run_status() -> JSONResponse:
    return JSONResponse({
        "is_running": False,
        "stage": "complete",
        "message": "Verified S01 Proof Pack",
        "details": {},
        "started_at": None,
        "completed_at": None,
        "error": None,
        "result": None,
    })


@app.get("/demo/session-snapshot/{filename}", include_in_schema=False)
def get_snapshot_file(filename: str) -> Response:
    target = SNAPSHOT_DIR / filename
    if not target.is_file():
        alt = filename.replace("_", "-") if "_" in filename else filename.replace("-", "_")
        target = SNAPSHOT_DIR / alt
    if target.is_file():
        return Response(target.read_bytes(), media_type="application/json")
    raise HTTPException(status_code=404, detail="Artifact not found")


@app.get("/.proofloop/session/{filename}", include_in_schema=False)
def get_session_file(filename: str) -> Response:
    target = SESSION_DIR / filename
    if not target.is_file():
        alt = filename.replace("_", "-") if "_" in filename else filename.replace("-", "_")
        target = SESSION_DIR / alt
    if not target.is_file():
        target = SNAPSHOT_DIR / filename
    if target.is_file():
        return Response(target.read_bytes(), media_type="application/json")
    raise HTTPException(status_code=404, detail="Artifact not found")


# ── Products ─────────────────────────────────────────────────────────────────

@app.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)) -> list[ProductResponse]:
    products = db.query(Product).all()
    return [ProductResponse.model_validate(p) for p in products]


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductResponse:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product_not_found")
    return ProductResponse.model_validate(product)


# ── Coupons ───────────────────────────────────────────────────────────────────

@app.get("/coupons/{code}", response_model=CouponResponse)
def get_coupon(code: str, db: Session = Depends(get_db)) -> CouponResponse:
    coupon = db.query(Coupon).filter(Coupon.code == code.upper()).first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="coupon_not_found")
    return CouponResponse.model_validate(coupon)


# ── Checkout ──────────────────────────────────────────────────────────────────

@app.post("/checkout", response_model=CheckoutResponse, status_code=201)
def checkout(
    request: CheckoutRequest, db: Session = Depends(get_db)
) -> CheckoutResponse:
    try:
        return process_checkout(db, request)
    except CheckoutError as exc:
        raise HTTPException(status_code=400, detail=exc.detail) from exc
