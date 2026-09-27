/**
 * ProofLoop Dashboard — Vanilla JavaScript Application
 *
 * Visualizes ProofLoop session artifacts (.proofloop/session/ or demo snapshot).
 * Features progressive step-by-step loading states as artifacts arrive,
 * adaptive fast polling (800ms during active execution, 2000ms when stable),
 * and clean developer-tool observability design.
 */

(function () {
  "use strict";

  // State
  let currentSource = "session"; // "session" or "snapshot"
  let cachedData = null;
  let lastDataString = "";
  let pollTimer = null;
  let currentPollInterval = 2000;
  let activeRawTab = "change-contract.json";

  // DOM Elements
  const sourceSelect = document.getElementById("sourceSelect");
  const pulseDot = document.getElementById("pulseDot");
  const pollText = document.getElementById("pollText");
  const refreshBtn = document.getElementById("refreshBtn");
  const resetBtn = document.getElementById("resetBtn");
  const headerFinalBadge = document.getElementById("headerFinalBadge");

  const sourceTag = document.getElementById("sourceTag");
  const sourceInfo = document.getElementById("sourceInfo");
  const sourceTime = document.getElementById("sourceTime");

  const adversarialContent = document.getElementById("adversarialContent");
  const advStatusBadge = document.getElementById("advStatusBadge");

  const contractContent = document.getElementById("contractContent");
  const contractStatusBadge = document.getElementById("contractStatusBadge");

  const repairContent = document.getElementById("repairContent");
  const repairStatusBadge = document.getElementById("repairStatusBadge");

  const verificationContent = document.getElementById("verificationContent");
  const verifStatusBadge = document.getElementById("verifStatusBadge");

  const proofPackContent = document.getElementById("proofPackContent");
  const packFinalStatusBadge = document.getElementById("packFinalStatusBadge");
  const matrixS01Status = document.getElementById("matrixS01Status");

  const rawViewerFilename = document.getElementById("rawViewerFilename");
  const rawViewerCode = document.getElementById("rawViewerCode");
  const copyRawBtn = document.getElementById("copyRawBtn");

  // ── Helper: Safe Escaping ──────────────────────────────────────────────────
  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // ── Data Fetching ─────────────────────────────────────────────────────────
  async function fetchArtifactFile(basePath, candidates) {
    for (const name of candidates) {
      try {
        const res = await fetch(`${basePath}/${name}`, { cache: "no-store" });
        if (res.ok) {
          const json = await res.json();
          return { data: json, filename: name };
        }
      } catch (err) {
        // continue
      }
    }
    return { data: null, filename: candidates[0] };
  }

  async function loadArtifacts() {
    // 1. Try server API endpoint first (/api/session?source=...)
    try {
      const apiRes = await fetch(`/api/session?source=${currentSource}`, { cache: "no-store" });
      if (apiRes.ok) {
        const bundle = await apiRes.json();
        return {
          source: bundle.source,
          source_dir: bundle.source_dir,
          artifacts: bundle.artifacts,
          run_state: bundle.run_state || null,
        };
      }
    } catch (e) {
      // Fall through to direct static file fetching
    }

    // 2. Direct static file fetching fallback
    let basePath = currentSource === "snapshot"
      ? "/demo/session-snapshot"
      : "/.proofloop/session";

    let [contractRes, advRes, repairRes, verifRes, packRes] = await Promise.all([
      fetchArtifactFile(basePath, ["change-contract.json", "change_contract.json"]),
      fetchArtifactFile(basePath, ["adversarial-report.json", "adversarial_report.json"]),
      fetchArtifactFile(basePath, ["repair-log.json", "repair_log.json"]),
      fetchArtifactFile(basePath, ["verification-evidence.json", "verification_evidence.json"]),
      fetchArtifactFile(basePath, ["proof-pack.json", "proof_pack.json"]),
    ]);

    // On static deployments (e.g. Vercel, GitHub Pages) without live local backend,
    // automatically fall back to the verified hero snapshot if session is absent.
    let resolvedSource = currentSource;
    if (!contractRes.data && !packRes.data && currentSource === "session") {
      basePath = "/demo/session-snapshot";
      resolvedSource = "snapshot";
      [contractRes, advRes, repairRes, verifRes, packRes] = await Promise.all([
        fetchArtifactFile(basePath, ["change-contract.json", "change_contract.json"]),
        fetchArtifactFile(basePath, ["adversarial-report.json", "adversarial_report.json"]),
        fetchArtifactFile(basePath, ["repair-log.json", "repair_log.json"]),
        fetchArtifactFile(basePath, ["verification-evidence.json", "verification_evidence.json"]),
        fetchArtifactFile(basePath, ["proof-pack.json", "proof_pack.json"]),
      ]);
    }

    return {
      source: resolvedSource,
      source_dir: basePath.replace(/^\//, ""),
      artifacts: {
        change_contract: contractRes.data,
        adversarial_report: advRes.data,
        repair_log: repairRes.data,
        verification_evidence: verifRes.data,
        proof_pack: packRes.data,
      },
      run_state: null,
    };
  }

  // ── Render Workflow Pipeline Ribbon ───────────────────────────────────────
  function renderPipeline(artifacts, runState) {
    const contract = artifacts.change_contract;
    const adversarial = artifacts.adversarial_report;
    const repair = artifacts.repair_log;
    const verification = artifacts.verification_evidence;
    const pack = artifacts.proof_pack;

    const isRunning = runState && runState.is_running;
    const stage = runState ? runState.stage : "idle";

    // Progressive step status
    let steps = [
      { id: "step-intent", complete: Boolean(contract), active: !contract },
      { id: "step-contract", complete: Boolean(contract), active: false },
      { id: "step-implement", complete: Boolean(adversarial || repair || verification), active: Boolean(contract && !adversarial) },
      { id: "step-challenge", complete: Boolean(adversarial), active: Boolean(contract && !adversarial) },
      { id: "step-repair", complete: Boolean(repair && repair.repairs && repair.repairs.length > 0), active: Boolean(adversarial && (!repair || !repair.repairs.length)) },
      { id: "step-verify", complete: Boolean(verification), active: Boolean(repair && !verification) },
      { id: "step-proof", complete: Boolean(pack), active: Boolean(verification && !pack) },
    ];

    if (isRunning) {
      if (stage === "starting" || stage === "init") {
        steps[0].active = true;
      } else if (stage === "contract") {
        steps[1].active = true;
      } else if (stage === "contract_ready") {
        steps[1].complete = true;
        steps[2].active = true;
      } else if (stage === "challenge") {
        steps[1].complete = true;
        steps[2].complete = true;
        steps[3].active = true;
      } else if (stage === "challenge_uncovered") {
        steps[3].complete = true;
        steps[4].active = true;
      } else if (stage === "repair" || stage === "repair_complete") {
        steps[3].complete = true;
        steps[4].complete = true;
        steps[5].active = true;
      } else if (stage === "verify" || stage === "verify_complete") {
        steps[4].complete = true;
        steps[5].complete = true;
        steps[6].active = true;
      } else if (stage === "proof_pack") {
        steps[5].complete = true;
        steps[6].active = true;
      }
    }

    steps.forEach((s) => {
      const el = document.getElementById(s.id);
      if (!el) return;
      el.classList.remove("completed", "active");
      if (s.complete) {
        el.classList.add("completed");
      } else if (s.active) {
        el.classList.add("active");
      }
    });

    // Update connector lines
    for (let i = 1; i <= 6; i++) {
      const conn = document.getElementById(`conn-${i}`);
      if (conn) {
        if (steps[i - 1].complete && (steps[i].complete || steps[i].active)) {
          conn.classList.add("active");
        } else {
          conn.classList.remove("active");
        }
      }
    }
  }

  // ── Render Adversarial Finding (HERO CARD) ─────────────────────────────────
  function renderAdversarial(report, contract) {
    if (!report || !report.findings || report.findings.length === 0) {
      // Check if Stage 1 (Contract) is done, meaning Adversarial is actively scanning
      if (contract) {
        advStatusBadge.textContent = "HUNTING INVARIANTS...";
        advStatusBadge.className = "status-badge badge-loading";
        adversarialContent.innerHTML = `
          <div class="stage-active-box">
            <div class="stage-radar">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <h3 style="font-size: 0.95rem; font-weight: 600; color: var(--color-blue); margin-bottom: 4px;">
              Adversarial Agent Auditing Implementation...
            </h3>
            <p style="font-size: 0.8rem; color: var(--text-muted); max-width: 520px; margin: 0 auto 6px auto;">
              Auditing <code>checkoutlab/app/services/checkout.py</code> against invariant <code>inv-01</code>. Testing boundary discount combinations.
            </p>
            <span style="font-size: 0.72rem; color: var(--text-subtle); font-family: var(--font-mono);">
              [adversarial mode] hunting for edge-case invariant violations
            </span>
          </div>
        `;
        return;
      }

      advStatusBadge.textContent = "AWAITING EVIDENCE";
      advStatusBadge.className = "status-badge badge-incomplete";
      adversarialContent.innerHTML = `
        <div class="awaiting-evidence">
          <div class="awaiting-icon">⏳</div>
          <h3>Awaiting Adversarial Challenge</h3>
          <p>Adversarial report (<code>adversarial-report.json</code>) has not yet been written to the session directory.</p>
          <p class="awaiting-sub">Execute IBM Bob in <code>adversarial</code> mode or run the ProofLoop CLI.</p>
        </div>
      `;
      return;
    }

    const findings = report.findings;
    const heroFinding = findings.find((f) => f.finding_id === "af-01") || findings[0];
    const isResolved = heroFinding.status === "resolved";

    advStatusBadge.textContent = isResolved ? "RESOLVED BY REPAIR" : "VIOLATION IDENTIFIED";
    advStatusBadge.className = isResolved
      ? "status-badge badge-verified"
      : "status-badge badge-failed";

    let html = `
      <div class="defect-box fade-in">
        <div class="defect-header">
          <div class="defect-title">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <span>Seeded Defect Discovered: Payment Amount Can Become Negative</span>
          </div>
          <span class="defect-badge">${escapeHtml(heroFinding.severity)}</span>
        </div>

        <!-- The Defect Math Breakdown Box (Iconic S01 Presentation Moment) -->
        <div class="calc-breakdown">
          <div class="calc-item">
            <span class="calc-label">Cart Subtotal</span>
            <span class="calc-val">$50.00</span>
          </div>
          <div class="calc-item">
            <span class="calc-label">Promotional Coupon</span>
            <span class="calc-val">$75.00</span>
          </div>
          <div class="calc-item">
            <span class="calc-label">Unchecked Charge Result</span>
            <span class="calc-val negative">-$25.00</span>
          </div>
          <div class="calc-violation">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" style="margin-right: 4px;">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            VIOLATION
          </div>
        </div>

        <div class="invariant-callout">
          <div class="inv-title">Critical Invariant Violated</div>
          <code>inv-01: Payment amount charged to customer must always be &ge; $0.00</code>
        </div>

        <div class="defect-source">
          <strong>Vulnerable Code:</strong> <code>${escapeHtml(heroFinding.evidence)}</code>
        </div>
        <div class="defect-source" style="margin-top: 6px;">
          <strong>Suggested Repair:</strong> <code>${escapeHtml(heroFinding.suggested_repair)}</code>
        </div>
      </div>
    `;

    adversarialContent.innerHTML = html;
  }

  // ── Render Change Contract ────────────────────────────────────────────────
  function renderContract(contract) {
    if (!contract) {
      contractStatusBadge.textContent = "AWAITING EVIDENCE";
      contractStatusBadge.className = "status-badge badge-incomplete";
      contractContent.innerHTML = `
        <div class="awaiting-evidence">
          <div class="awaiting-icon">📄</div>
          <h3>Awaiting Change Contract</h3>
          <p>Change contract (<code>change-contract.json</code>) not found in <code>.proofloop/session/</code>.</p>
          <p class="awaiting-sub">Initiate S01 or run Bob in <code>proofloop</code> mode to formulate the contract.</p>
        </div>
      `;
      return;
    }

    contractStatusBadge.textContent = `CONTRACT: ${contract.contract_id || "ACTIVE"}`;
    contractStatusBadge.className = "status-badge badge-verified";

    const invs = contract.invariants || [];
    const components = contract.affected_components || [];

    const invItemsHtml = invs.map((inv) => `
      <li style="margin-bottom: 6px; font-size: 0.82rem;">
        <code>${escapeHtml(inv.id)}</code>: <strong>${escapeHtml(inv.description)}</strong>
      </li>
    `).join("");

    const compPillsHtml = components.map((c) => `
      <span style="display: inline-block; background: #ffffff; border: 1px solid var(--border-light); padding: 2px 7px; border-radius: var(--radius-sm); font-family: var(--font-mono); font-size: 0.74rem; margin-right: 6px; margin-bottom: 6px;">
        ${escapeHtml(c)}
      </span>
    `).join("");

    contractContent.innerHTML = `
      <div class="fade-in">
        <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 14px 16px; margin-bottom: 14px;">
          <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 4px;">Developer Raw Intent</span>
          <blockquote style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">
            &ldquo;${escapeHtml(contract.request_raw || "Add promotional coupon support to checkout.")}&rdquo;
          </blockquote>
          <div style="font-size: 0.78rem; color: var(--text-secondary);">
            <strong>Normalized Intent:</strong> ${escapeHtml(contract.request_normalized || "")}
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
          <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 12px 14px;">
            <h4 style="font-size: 0.74rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">Business Invariants (${invs.length})</h4>
            <ul style="list-style: none; padding-left: 0;">
              ${invItemsHtml || "<li>No invariants specified</li>"}
            </ul>
          </div>
          <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 12px 14px;">
            <h4 style="font-size: 0.74rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">Affected Components (${components.length})</h4>
            <div>${compPillsHtml || "<span>None</span>"}</div>
          </div>
        </div>
      </div>
    `;
  }

  // ── Render Repair Log ─────────────────────────────────────────────────────
  function renderRepair(repairLog, adversarialReport) {
    const repairs = repairLog ? repairLog.repairs || [] : [];
    if (!repairLog || repairs.length === 0) {
      // Check if adversarial finding is open, meaning Repair is currently in progress
      if (adversarialReport && adversarialReport.findings && adversarialReport.findings.length > 0) {
        repairStatusBadge.textContent = "REPAIR IN PROGRESS...";
        repairStatusBadge.className = "status-badge badge-loading";
        repairContent.innerHTML = `
          <div class="stage-active-box">
            <div class="stage-spinner"></div>
            <h3 style="font-size: 0.95rem; font-weight: 600; color: #7c3aed; margin-bottom: 4px;">
              Formulating Defect Remediation...
            </h3>
            <p style="font-size: 0.8rem; color: var(--text-muted); max-width: 520px; margin: 0 auto 6px auto;">
              Applying floor guard <code>max(Decimal('0.00'), subtotal - discount_amount)</code> to <code>checkout.py</code> and verifying invariant regression test.
            </p>
            <span style="font-size: 0.72rem; color: var(--text-subtle); font-family: var(--font-mono);">
              [repair cycle] safeguarding inv-01 invariant
            </span>
          </div>
        `;
        return;
      }

      repairStatusBadge.textContent = "AWAITING EVIDENCE";
      repairStatusBadge.className = "status-badge badge-incomplete";
      repairContent.innerHTML = `
        <div class="awaiting-evidence">
          <div class="awaiting-icon">🔧</div>
          <h3>Awaiting Repair Log</h3>
          <p>Repair log (<code>repair-log.json</code>) has not yet been recorded.</p>
          <p class="awaiting-sub">Generated when an adversarial finding is remediated with an invariant floor guard.</p>
        </div>
      `;
      return;
    }

    const repair = repairs[0];
    repairStatusBadge.textContent = "REPAIR VERIFIED";
    repairStatusBadge.className = "status-badge badge-verified";

    const files = repair.files_modified || [];
    const filesHtml = files.map((f) => `<li>${escapeHtml(f)}</li>`).join("");

    repairContent.innerHTML = `
      <div class="fade-in">
        <div style="margin-bottom: 12px; font-size: 0.95rem; font-weight: 600; color: var(--text-primary);">
          ${escapeHtml(repair.description)}
        </div>

        <div class="repair-grid">
          <div class="repair-card-item">
            <h4>Applied Floor Guard Implementation</h4>
            <div class="guard-code-box">
              final_total = max(Decimal("0.00"), order_subtotal - discount_amount)
            </div>
            <p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 8px;">
              Enforces invariant <code>inv-01</code>: charges never fall below zero even when discount exceeds cart total.
            </p>
          </div>

          <div class="repair-card-item">
            <h4>Modified Files & Regression Suites</h4>
            <ul class="modified-files-list">
              ${filesHtml || "<li>checkoutlab/app/services/checkout.py</li>"}
            </ul>
            <div style="margin-top: 10px; display: flex; gap: 8px;">
              <span class="tool-exit-badge">pytest: ${repair.post_repair_pytest_exit_code ?? 0}</span>
              <span class="tool-exit-badge">mypy: ${repair.post_repair_mypy_exit_code ?? 0}</span>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // ── Render Deterministic Verification ─────────────────────────────────────
  function renderVerification(evidence, repairLog) {
    if (!evidence) {
      // Check if repair log is done, meaning deterministic tools are actively executing
      if (repairLog && repairLog.repairs && repairLog.repairs.length > 0) {
        verifStatusBadge.textContent = "RUNNING VERIFICATION...";
        verifStatusBadge.className = "status-badge badge-loading";
        verificationContent.innerHTML = `
          <div class="stage-active-box">
            <div class="stage-spinner"></div>
            <h3 style="font-size: 0.95rem; font-weight: 600; color: #0d9488; margin-bottom: 4px;">
              Executing Real Deterministic Verification Tools...
            </h3>
            <p style="font-size: 0.8rem; color: var(--text-muted); max-width: 520px; margin: 0 auto 6px auto;">
              Running <code>pytest</code> test suite, <code>mypy</code> strict type checker, and <code>ruff</code> linter to capture exact exit codes.
            </p>
            <span style="font-size: 0.72rem; color: var(--text-subtle); font-family: var(--font-mono);">
              [verifier mode] capturing deterministic process exit codes
            </span>
          </div>
        `;
        return;
      }

      verifStatusBadge.textContent = "AWAITING EVIDENCE";
      verifStatusBadge.className = "status-badge badge-incomplete";
      verificationContent.innerHTML = `
        <div class="awaiting-evidence">
          <div class="awaiting-icon">🧪</div>
          <h3>Awaiting Verification Evidence</h3>
          <p>Tool evidence (<code>verification-evidence.json</code>) not present in <code>.proofloop/session/</code>.</p>
          <p class="awaiting-sub">Run <code>python proofloop/cli.py verify --all</code> to execute verification tools.</p>
        </div>
      `;
      return;
    }

    const pytest = evidence.pytest || {};
    const mypy = evidence.mypy || {};
    const ruff = evidence.ruff || {};

    const allPass = pytest.exit_code === 0 && mypy.exit_code === 0 && ruff.exit_code === 0;
    verifStatusBadge.textContent = allPass ? "ALL PASS (EXIT 0)" : "FAILURES DETECTED";
    verifStatusBadge.className = allPass ? "status-badge badge-verified" : "status-badge badge-failed";

    verificationContent.innerHTML = `
      <div class="tools-grid fade-in">
        <!-- Pytest Card -->
        <div class="tool-card">
          <div class="tool-card-header">
            <div class="tool-name">
              <span>pytest</span>
              <span class="evidence-pill pill-deterministic">TEST SUITE</span>
            </div>
            <span class="tool-exit-badge">EXIT ${pytest.exit_code ?? 0}</span>
          </div>
          <div class="tool-metric-val">${pytest.tests_passed ?? 0} / ${pytest.tests_total ?? 0}</div>
          <div class="tool-metric-sub">tests passed in ${Number(pytest.duration_seconds || 0).toFixed(2)}s</div>
        </div>

        <!-- Mypy Card -->
        <div class="tool-card">
          <div class="tool-card-header">
            <div class="tool-name">
              <span>mypy</span>
              <span class="evidence-pill pill-deterministic">TYPE CHECK</span>
            </div>
            <span class="tool-exit-badge">EXIT ${mypy.exit_code ?? 0}</span>
          </div>
          <div class="tool-metric-val">${mypy.error_count ?? 0}</div>
          <div class="tool-metric-sub">type errors detected</div>
        </div>

        <!-- Ruff Card -->
        <div class="tool-card">
          <div class="tool-card-header">
            <div class="tool-name">
              <span>ruff</span>
              <span class="evidence-pill pill-deterministic">LINTER</span>
            </div>
            <span class="tool-exit-badge">EXIT ${ruff.exit_code ?? 0}</span>
          </div>
          <div class="tool-metric-val">${ruff.violation_count ?? 0}</div>
          <div class="tool-metric-sub">lint / security violations</div>
        </div>
      </div>
    `;
  }

  // ── Render Proof Pack ─────────────────────────────────────────────────────
  function renderProofPack(pack, evidence) {
    if (!pack) {
      if (evidence) {
        packFinalStatusBadge.textContent = "ASSEMBLING...";
        packFinalStatusBadge.className = "status-badge badge-loading";
        headerFinalBadge.textContent = "ASSEMBLING...";
        headerFinalBadge.className = "status-badge badge-loading";
        if (matrixS01Status) {
          matrixS01Status.textContent = "ASSEMBLING";
          matrixS01Status.className = "status-badge badge-running";
        }
        proofPackContent.innerHTML = `
          <div class="stage-active-box">
            <div class="stage-spinner"></div>
            <h3 style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
              Assembling Traceable Proof Pack...
            </h3>
            <p style="font-size: 0.8rem; color: var(--text-muted); max-width: 520px; margin: 0 auto 6px auto;">
              Validating schema constraints, segregating deterministic vs LLM reasoning evidence, and generating cryptographic SHA-256 fingerprint.
            </p>
            <span style="font-size: 0.72rem; color: var(--text-subtle); font-family: var(--font-mono);">
              [proofloop assembler] compiling proof-pack.json
            </span>
          </div>
        `;
        return;
      }

      packFinalStatusBadge.textContent = "INCOMPLETE";
      packFinalStatusBadge.className = "status-badge badge-incomplete";
      headerFinalBadge.textContent = "INCOMPLETE";
      headerFinalBadge.className = "status-badge badge-incomplete";
      if (matrixS01Status) {
        matrixS01Status.textContent = "AWAITING EVIDENCE";
        matrixS01Status.className = "status-badge badge-incomplete";
      }

      proofPackContent.innerHTML = `
        <div class="awaiting-evidence">
          <div class="awaiting-icon">📦</div>
          <h3>Awaiting Proof Pack Assembly</h3>
          <p>Proof Pack artifact (<code>proof-pack.json</code>) has not yet been assembled.</p>
          <p class="awaiting-sub">Run <code>python proofloop/cli.py proof-pack</code> once deterministic verification passes.</p>
        </div>
      `;
      return;
    }

    const status = pack.final_status || "INCOMPLETE";
    packFinalStatusBadge.textContent = status;
    headerFinalBadge.textContent = status;
    if (matrixS01Status) {
      matrixS01Status.textContent = status;
      matrixS01Status.className = "status-badge badge-verified";
    }

    let badgeClass = "badge-incomplete";
    if (status === "VERIFIED") badgeClass = "badge-verified";
    else if (status === "FAILED") badgeClass = "badge-failed";

    packFinalStatusBadge.className = `status-badge ${badgeClass}`;
    headerFinalBadge.className = `status-badge ${badgeClass}`;

    const items = pack.evidence_items || [];
    const tableRows = items.map((item) => `
      <tr>
        <td><strong class="req-badge">${escapeHtml(item.requirement_id)}</strong></td>
        <td>${escapeHtml(item.requirement_description)}</td>
        <td>
          <span class="evidence-pill ${item.evidence_category === "deterministic" ? "pill-deterministic" : "pill-reasoning"}">
            ${escapeHtml(item.evidence_category)}
          </span>
        </td>
        <td>
          <span class="status-badge ${item.met ? "badge-verified" : "badge-failed"}">
            ${item.met ? "MET" : "NOT MET"}
          </span>
        </td>
        <td style="font-family: var(--font-mono); font-size: 0.74rem; color: var(--text-muted);">
          ${escapeHtml(item.detail)}
        </td>
      </tr>
    `).join("");

    proofPackContent.innerHTML = `
      <div class="fade-in">
        <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 14px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <span style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); display: block;">Assembly Conclusion</span>
            <span style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary);">${escapeHtml(pack.conclusion || "")}</span>
          </div>
          <div style="text-align: right;">
            <span style="font-family: var(--font-mono); font-size: 0.74rem; color: var(--text-muted); display: block;">Pack ID: ${escapeHtml(pack.pack_id || "pp-s01-001")}</span>
            <span style="font-family: var(--font-mono); font-size: 0.74rem; color: var(--text-muted);">Fingerprint: ${escapeHtml((pack.verification_fingerprint || "").slice(0, 16))}...</span>
          </div>
        </div>

        <div class="evidence-table-container">
          <table class="evidence-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Requirement / Invariant</th>
                <th>Evidence Category</th>
                <th>Status</th>
                <th>Audit Detail</th>
              </tr>
            </thead>
            <tbody>
              ${tableRows || "<tr><td colspan='5'>No evidence items</td></tr>"}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  // ── Render Raw JSON Inspector ─────────────────────────────────────────────
  function updateRawViewer(artifacts) {
    let targetData = null;
    let filename = activeRawTab;

    if (activeRawTab.includes("contract")) {
      targetData = artifacts.change_contract;
    } else if (activeRawTab.includes("adversarial")) {
      targetData = artifacts.adversarial_report;
    } else if (activeRawTab.includes("repair")) {
      targetData = artifacts.repair_log;
    } else if (activeRawTab.includes("verification")) {
      targetData = artifacts.verification_evidence;
    } else if (activeRawTab.includes("proof")) {
      targetData = artifacts.proof_pack;
    }

    rawViewerFilename.textContent = filename;
    if (targetData) {
      rawViewerCode.textContent = JSON.stringify(targetData, null, 2);
    } else {
      rawViewerCode.textContent = `// Artifact "${filename}" is currently not present in this session.\n// Run the corresponding ProofLoop step to generate it.`;
    }
  }

  // ── Main Update Cycle ─────────────────────────────────────────────────────
  async function refreshDashboard() {
    try {
      const bundle = await loadArtifacts();
      const arts = bundle.artifacts;
      const runState = bundle.run_state;

      // Determine if a live run or progressive transition is occurring
      const isInProgress = (arts.change_contract && !arts.proof_pack) || (runState && runState.is_running);

      if (isInProgress) {
        pulseDot.classList.add("running");
        pollText.textContent = "Live (Active)";
        sourceInfo.innerHTML = `<strong>Live Session:</strong> Pipeline in progress... updating step-by-step`;
      } else {
        pulseDot.classList.remove("running");
        pollText.textContent = "Live (2s)";
      }

      // Adaptive polling rate adjustment
      const desiredInterval = isInProgress ? 800 : 2000;
      if (desiredInterval !== currentPollInterval) {
        currentPollInterval = desiredInterval;
        clearInterval(pollTimer);
        pollTimer = setInterval(refreshDashboard, currentPollInterval);
      }

      const stringified = JSON.stringify(bundle);
      if (stringified === lastDataString) {
        sourceTime.textContent = `Last checked: ${new Date().toLocaleTimeString()}`;
        return;
      }

      lastDataString = stringified;
      cachedData = bundle;

      // Update banner
      if (bundle.source === "snapshot") {
        sourceTag.textContent = "DEMO SNAPSHOT";
        sourceInfo.innerHTML = `Reading pre-recorded verified run from <code>demo/session-snapshot/</code>`;
      } else if (!isInProgress) {
        sourceTag.textContent = "LIVE SESSION";
        sourceInfo.innerHTML = `Reading live artifacts from <code>.proofloop/session/</code>`;
      }
      sourceTime.textContent = `Updated: ${new Date().toLocaleTimeString()}`;

      // Render all visual sections with progressive loading state support
      renderPipeline(arts, runState);
      renderContract(arts.change_contract);
      renderAdversarial(arts.adversarial_report, arts.change_contract);
      renderRepair(arts.repair_log, arts.adversarial_report);
      renderVerification(arts.verification_evidence, arts.repair_log);
      renderProofPack(arts.proof_pack, arts.verification_evidence);
      updateRawViewer(arts);
    } catch (err) {
      console.error("[ProofLoop Dashboard] Error loading session artifacts:", err);
    }
  }

  // ── Session Reset Trigger ─────────────────────────────────────────────────
  async function triggerReset() {
    try {
      const res = await fetch("/api/reset", { method: "POST" });
      if (res.status === 409) {
        alert("Cannot reset while a run is in progress.");
        return;
      }
      lastDataString = "";
      refreshDashboard();
    } catch (err) {
      console.error("Failed to reset session:", err);
    }
  }

  // ── Event Handlers ────────────────────────────────────────────────────────
  function setupEvents() {
    // Reset button
    if (resetBtn) {
      resetBtn.addEventListener("click", triggerReset);
    }

    // Source dropdown change
    sourceSelect.addEventListener("change", (e) => {
      currentSource = e.target.value;
      lastDataString = "";
      refreshDashboard();
    });

    // Refresh button
    refreshBtn.addEventListener("click", () => {
      lastDataString = "";
      refreshDashboard();
    });

    // Raw tab clicks
    document.querySelectorAll(".raw-tab").forEach((tab) => {
      tab.addEventListener("click", (e) => {
        document.querySelectorAll(".raw-tab").forEach((t) => t.classList.remove("active"));
        e.target.classList.add("active");
        activeRawTab = e.target.textContent.trim();
        if (cachedData) {
          updateRawViewer(cachedData.artifacts);
        }
      });
    });

    // Copy Raw JSON button
    copyRawBtn.addEventListener("click", async () => {
      const text = rawViewerCode.textContent;
      try {
        await navigator.clipboard.writeText(text);
        const original = copyRawBtn.textContent;
        copyRawBtn.textContent = "Copied!";
        setTimeout(() => {
          copyRawBtn.textContent = original;
        }, 1500);
      } catch (e) {
        console.error("Clipboard copy failed:", e);
      }
    });

    // Keyboard shortcut: Press 'R' to reset session
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.target.tagName === "TEXTAREA") return;
      if (e.key === "r" || e.key === "R") {
        triggerReset();
      }
    });
  }

  // ── Initialization ────────────────────────────────────────────────────────
  function init() {
    setupEvents();
    refreshDashboard();
    pollTimer = setInterval(refreshDashboard, currentPollInterval);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
