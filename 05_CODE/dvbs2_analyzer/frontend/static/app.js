/**
 * PRJ_111: DVB-S2 Receiver Output Stream Analyzer - Frontend Application
 * Review-2 Functional Prototype Milestone
 * 
 * Engineering Workstation Client-Side Logic consuming frozen backend API (F1-F7).
 * Zero hard-coded analytical constants. Real backend telemetry only.
 * Uses vendored Chart.js offline.
 */

// Application State
let currentAnalysis = null;
let currentComparison = null;
let chartHealthAnomaly = null;
let chartActivity = null;
let activeTripartiteFilter = "ALL";
let selectedUploadFile = null;
let timerInterval = null;

// Document Ready Initialization
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  fetchStatus();
  fetchPresets();
  setupEventListeners();
  setupUploadDropzone();

  const params = new URLSearchParams(window.location.search);
  if (params.get("autoload") === "ts") {
    setTimeout(async () => {
      const customIn = document.getElementById("customPathInput");
      if (customIn) customIn.value = "01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts";
      await executeAnalysis();
      if (params.get("tab")) {
        switchTab(params.get("tab"));
      }
    }, 150);
  } else if (params.get("autocompare") === "1") {
    setTimeout(async () => {
      switchTab("tab-comparison");
      const compA = document.getElementById("compStreamA");
      const compB = document.getElementById("compStreamB");
      if (compA) compA.value = "01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts";
      if (compB) compB.value = "01_RAW_DATA/03_TS/DVBS2_toolkit/corrupted_sample.ts";
      await executeComparison(false);
    }, 150);
  } else if (params.get("tab")) {
    switchTab(params.get("tab"));
  }
});

// -----------------------------------------------------------------------------
// 1. Navigation & Tabs
// -----------------------------------------------------------------------------

function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.getAttribute("data-tab");
      switchTab(target);
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll(".nav-tab").forEach((t) => {
    t.classList.toggle("active", t.getAttribute("data-tab") === tabId);
  });
  document.querySelectorAll(".view-section").forEach((s) => {
    s.classList.toggle("active", s.id === tabId);
  });

  // Resize charts if timeline tab becomes active
  if (tabId === "tab-timeline") {
    if (chartHealthAnomaly) chartHealthAnomaly.resize();
    if (chartActivity) chartActivity.resize();
  }
}

// -----------------------------------------------------------------------------
// 2. Status & Preset Datasets
// -----------------------------------------------------------------------------

async function fetchStatus() {
  try {
    const res = await fetch("/api/status");
    if (!res.ok) return;
    const data = await res.json();
    const lbl = document.getElementById("backendStatusLabel");
    if (lbl && data.backend_status) {
      lbl.textContent = `${data.backend_status} | ${data.test_suite}`;
    }
  } catch (err) {
    console.warn("Status fetch failed:", err);
  }
}

async function fetchPresets() {
  try {
    const res = await fetch("/api/presets");
    if (!res.ok) return;
    const data = await res.json();
    const select = document.getElementById("presetSelect");
    if (!select || !data.presets) return;

    data.presets.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.absolute_path || p.relative_path;
      opt.textContent = `${p.label} [${p.format}]`;
      opt.dataset.format = p.format;
      opt.dataset.winSize = p.default_window_size;
      select.appendChild(opt);
    });

    select.addEventListener("change", () => {
      const selOpt = select.options[select.selectedIndex];
      if (selOpt && selOpt.value) {
        selectedUploadFile = null;
        const fileInput = document.getElementById("streamFileInput");
        if (fileInput) fileInput.value = "";
        const metaPanel = document.getElementById("fileMetaPanel");
        if (metaPanel) metaPanel.style.display = "none";

        document.getElementById("customPathInput").value = selOpt.value;
        const fmtSelect = document.getElementById("formatSelect");
        if (fmtSelect && selOpt.dataset.format) {
          fmtSelect.value = selOpt.dataset.format;
        }
        const winInput = document.getElementById("windowSizeInput");
        if (winInput && selOpt.dataset.winSize) {
          winInput.value = selOpt.dataset.winSize;
        }
        const compA = document.getElementById("compStreamA");
        if (compA && !compA.value) {
          compA.value = selOpt.value;
        }
      }
    });
  } catch (err) {
    console.warn("Presets fetch failed:", err);
  }
}

// -----------------------------------------------------------------------------
// 3. File Upload & Dropzone Handling
// -----------------------------------------------------------------------------

function setupUploadDropzone() {
  const dropzone = document.getElementById("uploadDropzone");
  const fileInput = document.getElementById("streamFileInput");
  if (!dropzone || !fileInput) return;

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });
}

function handleFileSelected(file) {
  selectedUploadFile = file;
  const panel = document.getElementById("fileMetaPanel");
  const nameEl = document.getElementById("fileMetaName");
  const sizeEl = document.getElementById("fileMetaSize");
  const statusEl = document.getElementById("fileMetaStatus");

  if (panel && nameEl && sizeEl) {
    nameEl.textContent = file.name;
    const kb = (file.size / 1024).toFixed(1);
    const mb = (file.size / (1024 * 1024)).toFixed(2);
    const sizeStr = file.size > 1024 * 1024 ? `${mb} MB (${file.size.toLocaleString()} bytes)` : `${kb} KB (${file.size.toLocaleString()} bytes)`;
    sizeEl.textContent = sizeStr;
    statusEl.textContent = "READY FOR UPLOAD";
    statusEl.className = "badge badge-info";
    panel.style.display = "flex";
  }

  // Format selection: Respect explicit user selection; if AUTO, allow backend content detection to determine format
  const ext = file.name.split(".").pop().toLowerCase();
  const fmtSelect = document.getElementById("formatSelect");
  const winInput = document.getElementById("windowSizeInput");
  if (fmtSelect && fmtSelect.value === "AUTO") {
    if (ext === "pcap") {
      fmtSelect.value = "BB_FRAME";
      if (winInput && !winInput.value) winInput.value = "50";
    } else if (ext === "gse") {
      fmtSelect.value = "GSE";
      if (winInput && !winInput.value) winInput.value = "3";
    }
    // For .ts files, keep AUTO so backend content-aware detection correctly distinguishes MPEG-TS and GSE!
  }

  // Reset preset dropdown selection
  const presetSelect = document.getElementById("presetSelect");
  if (presetSelect) presetSelect.selectedIndex = 0;
  document.getElementById("customPathInput").value = `05_CODE/uploads/${file.name}`;
}

// -----------------------------------------------------------------------------
// 4. Comparison State Reset & Event Listeners
// -----------------------------------------------------------------------------

function resetComparisonState(keepInputs = false) {
  currentComparison = null;
  const resDiv = document.getElementById("comparisonResults");
  if (resDiv) resDiv.style.display = "none";

  if (!keepInputs) {
    const compA = document.getElementById("compStreamA");
    if (compA) compA.value = "";
    const compB = document.getElementById("compStreamB");
    if (compB) compB.value = "";
  }

  const badgeEquiv = document.getElementById("compFormatEquiv");
  if (badgeEquiv) {
    badgeEquiv.textContent = "AWAITING COMPARISON INPUT";
    badgeEquiv.className = "stat-value";
  }

  const namesEl = document.getElementById("compFormatNames");
  if (namesEl) namesEl.textContent = "Stream A vs Stream B";

  const alignModeEl = document.getElementById("compAlignmentMode");
  if (alignModeEl) alignModeEl.textContent = "--";

  const alignCountEl = document.getElementById("compAlignedCount");
  if (alignCountEl) alignCountEl.textContent = "Awaiting comparison input";

  const payloadDeltaEl = document.getElementById("compPayloadDelta");
  if (payloadDeltaEl) payloadDeltaEl.textContent = "--";

  const payloadSigEl = document.getElementById("compPayloadSig");
  if (payloadSigEl) payloadSigEl.textContent = "Significance: --";

  const tbody = document.getElementById("semanticAuditTableBody");
  if (tbody) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted); padding:16px;">Awaiting comparison execution</td></tr>';
  }
}

function setupEventListeners() {
  const runBtn = document.getElementById("runAnalysisBtn");
  if (runBtn) {
    runBtn.addEventListener("click", executeAnalysis);
  }

  const clearBtn = document.getElementById("clearDataBtn");
  if (clearBtn) {
    clearBtn.addEventListener("click", clearAnalysis);
  }

  const compHalvesBtn = document.getElementById("btnCompHalves");
  if (compHalvesBtn) {
    compHalvesBtn.addEventListener("click", () => executeComparison(true));
  }

  const compBtn = document.getElementById("btnRunComparison");
  if (compBtn) {
    compBtn.addEventListener("click", () => executeComparison(false));
  }

  // Input change listeners: Invalidate previous comparison when inputs change
  const compA = document.getElementById("compStreamA");
  if (compA) {
    compA.addEventListener("input", () => resetComparisonState(true));
    compA.addEventListener("change", () => resetComparisonState(true));
  }
  const compB = document.getElementById("compStreamB");
  if (compB) {
    compB.addEventListener("input", () => resetComparisonState(true));
    compB.addEventListener("change", () => resetComparisonState(true));
  }

  // Tripartite finding filter buttons
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeTripartiteFilter = btn.getAttribute("data-filter");
      renderReportFindings();
    });
  });
}

function openTermsModal() {
  const m = document.getElementById("termsModal");
  if (m) m.style.display = "flex";
}

function closeTermsModal() {
  const m = document.getElementById("termsModal");
  if (m) m.style.display = "none";
}

function showNotification(msg, isError = false) {
  const b = document.getElementById("notificationBanner");
  if (!b) return;
  b.style.display = "block";
  b.style.backgroundColor = isError ? "var(--red-subtle)" : "var(--green-subtle)";
  b.style.color = isError ? "var(--red)" : "var(--green)";
  b.style.borderBottom = isError ? "1px solid rgba(248, 81, 73, 0.3)" : "1px solid rgba(63, 185, 80, 0.3)";
  b.textContent = msg;
  setTimeout(() => {
    b.style.display = "none";
  }, 6000);
}

// -----------------------------------------------------------------------------
// 5. Execution Pipeline with Visual Checklist (F1-F7)
// -----------------------------------------------------------------------------

function updateStepStatus(stepId, status, label) {
  const stepEl = document.getElementById(stepId);
  const badgeEl = document.getElementById(`badge-${stepId}`);
  if (!stepEl || !badgeEl) return;

  stepEl.classList.remove("active", "done", "skipped");
  badgeEl.className = "badge";

  if (status === "RUNNING") {
    stepEl.classList.add("active");
    badgeEl.classList.add("badge-info");
    badgeEl.textContent = label || "RUNNING";
  } else if (status === "DONE") {
    stepEl.classList.add("done");
    badgeEl.classList.add("badge-healthy");
    badgeEl.textContent = label || "DONE";
  } else if (status === "WAITING") {
    stepEl.classList.add("skipped");
    badgeEl.classList.add("badge-dim");
    badgeEl.textContent = label || "AWAITING COMPARISON INPUT";
  } else {
    badgeEl.classList.add("badge-dim");
    badgeEl.textContent = label || "STANDBY";
  }
}

function resetChecklist() {
  updateStepStatus("step-ingest", "STANDBY");
  updateStepStatus("step-f1", "STANDBY");
  updateStepStatus("step-f2", "STANDBY");
  updateStepStatus("step-f3", "STANDBY");
  updateStepStatus("step-f4", "STANDBY");
  updateStepStatus("step-f5", "STANDBY");
  updateStepStatus("step-f6", "WAITING", "AWAITING COMPARISON INPUT");
  updateStepStatus("step-f7", "STANDBY");
}

async function executeAnalysis() {
  let pathInput = document.getElementById("customPathInput").value.trim();
  const formatVal = document.getElementById("formatSelect").value;
  const winSizeVal = document.getElementById("windowSizeInput").value.trim();

  if (!selectedUploadFile && !pathInput) {
    showNotification("Please select a capture file to upload or choose a verified test capture.", true);
    return;
  }

  const runBtn = document.getElementById("runAnalysisBtn");
  const spinner = document.getElementById("btnSpinner");
  const btnText = document.getElementById("btnText");
  const timerEl = document.getElementById("execTimer");

  runBtn.disabled = true;
  spinner.style.display = "inline-block";
  btnText.textContent = "Analyzing Stream...";

  // Start wall-clock timer
  const startTime = performance.now();
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    const elapsed = (performance.now() - startTime) / 1000.0;
    if (timerEl) timerEl.textContent = `Elapsed: ${elapsed.toFixed(2)} s`;
  }, 50);

  resetChecklist();

  try {
    // Phase 1: Upload file if selected
    if (selectedUploadFile) {
      updateStepStatus("step-ingest", "RUNNING", "STAGING FILE");
      const statusEl = document.getElementById("fileMetaStatus");
      if (statusEl) {
        statusEl.textContent = "STAGING LOCAL FILE";
        statusEl.className = "badge badge-info";
      }

      const uploadUrl = `/api/upload?filename=${encodeURIComponent(selectedUploadFile.name)}`;
      const uploadRes = await fetch(uploadUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/octet-stream",
          "X-File-Name": selectedUploadFile.name,
        },
        body: selectedUploadFile,
      });

      const uploadData = await uploadRes.json();
      if (!uploadRes.ok || !uploadData.success) {
        throw new Error(uploadData.error || "File upload staging failed");
      }

      pathInput = uploadData.file_path;
      document.getElementById("customPathInput").value = uploadData.relative_path || uploadData.file_path;
      if (statusEl) {
        statusEl.textContent = "STAGED LOCALLY";
        statusEl.className = "badge badge-healthy";
      }
    }

    updateStepStatus("step-ingest", "RUNNING", "PARSING & VALIDATING");
    updateStepStatus("step-f1", "RUNNING");
    updateStepStatus("step-f2", "RUNNING");
    updateStepStatus("step-f3", "RUNNING");
    updateStepStatus("step-f4", "RUNNING");
    updateStepStatus("step-f5", "RUNNING");
    updateStepStatus("step-f7", "RUNNING");

    const payload = {
      file_path: pathInput,
      format: formatVal,
      window_size: winSizeVal ? parseInt(winSizeVal, 10) : null,
    };

    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonStringifySafe(payload),
    });

    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || "Analysis failed");
    }

    // Stop timer
    if (timerInterval) clearInterval(timerInterval);
    const finalElapsed = (performance.now() - startTime) / 1000.0;
    if (timerEl) timerEl.textContent = `Completed: ${finalElapsed.toFixed(2)} s`;

    // Mark steps as done
    updateStepStatus("step-ingest", "DONE");
    updateStepStatus("step-f1", "DONE");
    updateStepStatus("step-f2", "DONE");
    updateStepStatus("step-f3", "DONE");
    updateStepStatus("step-f4", "DONE");
    updateStepStatus("step-f5", "DONE");
    updateStepStatus("step-f6", "WAITING", "AWAITING COMPARISON INPUT");
    updateStepStatus("step-f7", "DONE");

    currentAnalysis = data;
    renderDashboardView(data);
    renderAnomalyView(data);
    renderTimelineView(data);
    renderReportView(data);

    // Pre-populate comparison stream A with current stream and invalidate previous comparison
    const compA = document.getElementById("compStreamA");
    if (compA) {
      compA.value = pathInput;
    }
    resetComparisonState(true);

    showNotification(`F1-F5 and F7 analysis executed on uploaded stream: ${data.stream_info.file_name}; F6 comparison available when a comparison input is provided.`);
  } catch (err) {
    if (timerInterval) clearInterval(timerInterval);
    console.error("Analysis error:", err);
    showNotification(`Analysis Error: ${err.message}`, true);

    // Invalidate stale previous analysis state on failure
    currentAnalysis = null;
    const resultsDiv = document.getElementById("dashboardResults");
    if (resultsDiv) resultsDiv.style.display = "none";
    const emptyDiv = document.getElementById("dashboardEmptyState");
    if (emptyDiv) emptyDiv.style.display = "block";

    const hdrBadge = document.getElementById("headerFormatBadge");
    if (hdrBadge) {
      hdrBadge.textContent = "ANALYSIS FAILED";
      hdrBadge.className = "badge badge-critical";
    }

    resetComparisonState(true);
    resetChecklist();
    updateStepStatus("step-ingest", "STANDBY", "FAILED");
  } finally {
    runBtn.disabled = false;
    spinner.style.display = "none";
    btnText.textContent = "Analyze Stream (F1-F5, F7)";
  }
}

function clearAnalysis() {
  currentAnalysis = null;
  selectedUploadFile = null;
  if (timerInterval) clearInterval(timerInterval);
  const timerEl = document.getElementById("execTimer");
  if (timerEl) timerEl.textContent = "Elapsed: 0.00 s";

  document.getElementById("dashboardResults").style.display = "none";
  document.getElementById("dashboardEmptyState").style.display = "block";
  document.getElementById("customPathInput").value = "";
  document.getElementById("presetSelect").selectedIndex = 0;
  document.getElementById("streamFileInput").value = "";

  const metaPanel = document.getElementById("fileMetaPanel");
  if (metaPanel) metaPanel.style.display = "none";

  document.getElementById("headerFormatBadge").textContent = "NO STREAM LOADED";
  document.getElementById("headerFormatBadge").className = "badge badge-dim";

  resetChecklist();
  resetComparisonState(false);
}

// -----------------------------------------------------------------------------
// 6. Render View 1: Dashboard
// -----------------------------------------------------------------------------

function renderDashboardView(data) {
  document.getElementById("dashboardEmptyState").style.display = "none";
  const resultsDiv = document.getElementById("dashboardResults");
  resultsDiv.style.display = "block";

  const info = data.stream_info;
  const f1 = data.f1_health;
  const f2 = data.f2_anomalies;
  const f3 = data.f3_patterns;

  // Header badge
  const headerBadge = document.getElementById("headerFormatBadge");
  headerBadge.textContent = `${info.detected_format} (${info.file_name})`;
  headerBadge.className = "badge badge-info";

  // Stat Boxes
  const hScore = document.getElementById("statHealthScore");
  hScore.textContent = `${f1.overall_health_score.toFixed(1)}%`;
  hScore.className = `stat-value ${f1.overall_health_score >= 99 ? "green" : (f1.overall_health_score >= 80 ? "amber" : "red")}`;

  document.getElementById("statHealthStatus").textContent = `Status: ${f1.health_classification}`;
  document.getElementById("statIntegrityRatio").textContent = `${f1.integrity_ratio.toFixed(2)}%`;
  document.getElementById("statUnitsRatio").textContent = `Valid / Total: ${f1.valid_units.toLocaleString()} / ${info.total_units.toLocaleString()}`;

  const anomVal = document.getElementById("statAnomalyCount");
  anomVal.textContent = `${f2.anomaly_window_count} / ${f2.total_windows}`;
  anomVal.className = `stat-value ${f2.anomaly_window_count > 0 ? "amber" : "green"}`;
  document.getElementById("statPeakAnomaly").textContent = `Peak Score: ${f2.peak_anomaly_score.toFixed(4)} (Thresh: ${f2.decision_threshold.toFixed(2)})`;

  document.getElementById("statPayloadKb").textContent = `${info.total_payload_kb.toLocaleString()} KB`;
  document.getElementById("statFileSize").textContent = `Capture Size: ${info.file_size_kb.toLocaleString()} KB`;

  // Priority-1 Checks Table
  const tbody = document.getElementById("p1ChecksTableBody");
  tbody.innerHTML = "";
  f1.priority_1_checks.forEach((chk) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><code>${escapeHtml(chk.name)}</code></td>
      <td><span class="badge ${chk.status === "PASS" ? "badge-healthy" : "badge-critical"}">${escapeHtml(chk.status)}</span></td>
      <td>${escapeHtml(chk.details)}</td>
    `;
    tbody.appendChild(tr);
  });

  const hBadge = document.getElementById("dashHealthBadge");
  hBadge.textContent = f1.health_classification;
  hBadge.className = `badge ${f1.health_classification === "HEALTHY" ? "badge-healthy" : (f1.health_classification === "WARNING" ? "badge-warning" : "badge-critical")}`;

  // F3 Summary
  document.getElementById("f3DominantComponent").textContent = f3.dominant_component;
  document.getElementById("f3ActiveComponents").textContent = `Composition: ${f3.active_components}`;
  document.getElementById("f3EntropyLabel").textContent = f3.entropy;
  document.getElementById("f3TransitionsLabel").textContent = `State Transitions: ${f3.transition_count} detected`;
}

// -----------------------------------------------------------------------------
// 7. Render View 2: Anomaly Analysis (F2 + F5)
// -----------------------------------------------------------------------------

function renderAnomalyView(data) {
  const f2 = data.f2_anomalies;

  document.getElementById("anomTotalWindows").textContent = f2.total_windows;
  document.getElementById("anomFlaggedCount").textContent = f2.anomaly_window_count;
  document.getElementById("anomRatePct").textContent = `Anomaly Rate: ${f2.anomaly_rate_pct.toFixed(2)}%`;
  document.getElementById("anomPeakScore").textContent = f2.peak_anomaly_score.toFixed(4);

  const tbody = document.getElementById("anomaliesTableBody");
  tbody.innerHTML = "";

  if (!f2.anomalous_windows || f2.anomalous_windows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--green); padding: 16px;">No anomalous windows detected. Stream behavior is nominal across all windows.</td></tr>`;
    return;
  }

  f2.anomalous_windows.forEach((w) => {
    const tr = document.createElement("tr");
    const sevBadge = w.severity === "CRITICAL" ? "badge-critical" : (w.severity === "HIGH" ? "badge-critical" : (w.severity === "MEDIUM" ? "badge-warning" : "badge-info"));
    
    tr.innerHTML = `
      <td><strong>Window ${w.window_index}</strong></td>
      <td><code>[${w.unit_range[0]}..${w.unit_range[1]})</code></td>
      <td><code>[${w.byte_range[0]}..${w.byte_range[1]})</code></td>
      <td><span style="font-weight:600; font-family:var(--font-mono); color: ${w.score >= 0.7 ? 'var(--red)' : 'var(--amber)'};">${w.score.toFixed(4)}</span></td>
      <td><span class="badge ${sevBadge}">${w.severity}</span></td>
      <td>${escapeHtml(w.explanation || "Statistical deviation from baseline")}</td>
      <td><button class="btn btn-secondary btn-sm" onclick="inspectAnomalyWindow(${w.window_index})">Inspect</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function inspectAnomalyWindow(winIdx) {
  if (!currentAnalysis || !currentAnalysis.f5_explanations) return;
  const expls = currentAnalysis.f5_explanations.explanations || [];
  const expl = expls.find((e) => e.window_index === winIdx);

  const detailCard = document.getElementById("anomalyDetailCard");
  const title = document.getElementById("anomDetailTitle");
  const body = document.getElementById("anomDetailBody");

  if (!expl) {
    title.innerHTML = `Window ${winIdx} Diagnostic Details`;
    body.innerHTML = `<p style="color:var(--text-dim);">No dedicated F5 diagnostic finding recorded for Window ${winIdx}.</p>`;
    detailCard.style.display = "block";
    detailCard.scrollIntoView({ behavior: "smooth" });
    return;
  }

  title.innerHTML = `Window ${winIdx} Diagnostic Deep Dive [${expl.explanation_id}]`;

  let driversHtml = "";
  if (expl.primary_drivers && expl.primary_drivers.length > 0) {
    driversHtml = expl.primary_drivers.map((d) => `
      <div style="background: var(--bg-canvas); border: 1px solid var(--border-default); border-radius: 3px; padding: 10px; margin-top: 6px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <strong style="color: var(--accent); font-family:var(--font-mono); font-size:12px;">${escapeHtml(d.feature_name)}</strong>
          <span class="badge ${d.direction === "BELOW_BASELINE" ? "badge-warning" : "badge-info"}">${d.direction}</span>
        </div>
        <p style="color: var(--text-dim); margin-bottom: 4px; font-size:11.5px;">${escapeHtml(d.description)}</p>
        <div style="font-size: 11px; font-family: var(--font-mono); color: var(--text-muted);">
          Evidence: ${escapeHtml(d.evidence)} | Subsystem: ${escapeHtml(d.native_component)}
        </div>
        <div style="font-size: 11px; color: var(--green); margin-top: 3px;">
          Safe Inference: ${escapeHtml(d.safe_inference)}
        </div>
      </div>
    `).join("");
  } else {
    driversHtml = `<p style="color: var(--text-dim); margin-top: 4px; font-size:11.5px;">Features within nominal baseline dispersion.</p>`;
  }

  body.innerHTML = `
    <div class="grid-2" style="margin-bottom: 12px;">
      <div>
        <p><strong>What Happened:</strong> ${escapeHtml(expl.what_happened)}</p>
        <p style="margin-top: 4px;"><strong>Native Component:</strong> <code>${escapeHtml(expl.native_component)}</code></p>
        <p style="margin-top: 4px;"><strong>Evidence Summary:</strong> ${escapeHtml(expl.evidence_summary)}</p>
      </div>
      <div>
        <p><strong>Anomaly Score:</strong> <span style="font-weight:600; font-family:var(--font-mono); color:var(--red);">${expl.anomaly_score.toFixed(4)}</span> (Threshold: ${expl.anomaly_threshold.toFixed(2)})</p>
        <p style="margin-top: 4px;"><strong>Physical Offsets:</strong> Units [${expl.unit_offset_start}..${expl.unit_offset_end}), Bytes [${expl.byte_offset_start}..${expl.byte_offset_end})</p>
        <p style="margin-top: 4px;"><strong>Safe Conclusion:</strong> <span style="color: var(--green);">${escapeHtml(expl.safe_conclusion)}</span></p>
      </div>
    </div>
    <div style="margin-top: 10px;">
      <h4 style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing:0.3px; color: var(--text-main);">Primary Feature Drivers (Bounded Z-Score Magnitude with Deviation Direction):</h4>
      ${driversHtml}
    </div>
  `;

  detailCard.style.display = "block";
  detailCard.scrollIntoView({ behavior: "smooth" });
}

// -----------------------------------------------------------------------------
// 8. Render View 3: Timeline (F4)
// -----------------------------------------------------------------------------

function renderTimelineView(data) {
  const tl = data.f4_timeline;
  const points = tl.points || [];

  document.getElementById("timelineWindowCountBadge").textContent = `${points.length} Windows`;

  const labels = points.map((p) => `W${p.window_index}`);
  const healthData = points.map((p) => p.health_score);
  const anomData = points.map((p) => p.anomaly_score);
  const threshold = tl.anomaly_threshold || 0.50;
  const thresholdData = Array(points.length).fill(threshold);

  const payloadData = points.map((p) => p.payload_kb);

  let fmtMetricName = "Format Metric";
  let fmtData = [];
  const fmtStr = tl.format || "MPEG_TS";

  if (fmtStr.includes("MPEG_TS")) {
    fmtMetricName = "PID Entropy (bits)";
    fmtData = points.map((p) => p.format_specific_metrics?.pid_entropy || 0.0);
  } else if (fmtStr.includes("GSE")) {
    fmtMetricName = "Fragmentation Ratio";
    fmtData = points.map((p) => p.format_specific_metrics?.fragmentation_ratio || 0.0);
  } else if (fmtStr.includes("BB_FRAME")) {
    fmtMetricName = "Modal DFL (bits)";
    fmtData = points.map((p) => p.format_specific_metrics?.modal_dfl_bits || 0.0);
  }

  // Chart 1: Rolling Health & Anomaly
  const ctx1 = document.getElementById("healthAnomalyCanvas");
  if (ctx1 && window.Chart) {
    if (chartHealthAnomaly) chartHealthAnomaly.destroy();
    chartHealthAnomaly = new Chart(ctx1, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Stream Health (%)",
            data: healthData,
            borderColor: "#3fb950",
            backgroundColor: "rgba(63, 185, 80, 0.08)",
            borderWidth: 1.5,
            yAxisID: "yHealth",
            tension: 0.1,
            pointRadius: points.length > 50 ? 1.5 : 3,
          },
          {
            label: "F2 Anomaly Score",
            data: anomData,
            borderColor: "#f85149",
            backgroundColor: "rgba(248, 81, 73, 0.1)",
            borderWidth: 1.5,
            borderDash: [3, 3],
            yAxisID: "yAnomaly",
            tension: 0.1,
            pointRadius: points.length > 50 ? 1.5 : 3,
          },
          {
            label: `Decision Threshold (${threshold.toFixed(2)})`,
            data: thresholdData,
            borderColor: "#d29922",
            borderWidth: 1.2,
            borderDash: [5, 5],
            pointRadius: 0,
            yAxisID: "yAnomaly",
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          x: { grid: { color: "#21262d" }, ticks: { color: "#8b949e", font: { family: "ui-monospace, monospace", size: 10 } } },
          yHealth: {
            type: "linear",
            position: "left",
            min: 0,
            max: 100,
            grid: { color: "#21262d" },
            ticks: { color: "#3fb950", font: { family: "ui-monospace, monospace", size: 10 } },
            title: { display: true, text: "Health Score (%)", color: "#3fb950" },
          },
          yAnomaly: {
            type: "linear",
            position: "right",
            min: 0.0,
            max: 1.0,
            grid: { drawOnChartArea: false },
            ticks: { color: "#f85149", font: { family: "ui-monospace, monospace", size: 10 } },
            title: { display: true, text: "Anomaly Score [0..1]", color: "#f85149" },
          },
        },
        plugins: {
          legend: { labels: { color: "#f0f6fc", font: { family: "-apple-system, sans-serif", size: 11 } } },
        },
      },
    });
  }

  // Chart 2: Payload Volume & Format Metric
  const ctx2 = document.getElementById("activityCanvas");
  if (ctx2 && window.Chart) {
    if (chartActivity) chartActivity.destroy();
    chartActivity = new Chart(ctx2, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            type: "bar",
            label: "Payload Volume (KB)",
            data: payloadData,
            backgroundColor: "rgba(56, 139, 253, 0.35)",
            borderColor: "#388bfd",
            borderWidth: 1,
            yAxisID: "yPayload",
          },
          {
            type: "line",
            label: fmtMetricName,
            data: fmtData,
            borderColor: "#bc8cff",
            borderWidth: 1.5,
            yAxisID: "yFmt",
            tension: 0.1,
            pointRadius: points.length > 50 ? 1.5 : 3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          x: { grid: { color: "#21262d" }, ticks: { color: "#8b949e", font: { family: "ui-monospace, monospace", size: 10 } } },
          yPayload: {
            type: "linear",
            position: "left",
            grid: { color: "#21262d" },
            ticks: { color: "#388bfd", font: { family: "ui-monospace, monospace", size: 10 } },
            title: { display: true, text: "Payload (KB)", color: "#388bfd" },
          },
          yFmt: {
            type: "linear",
            position: "right",
            grid: { drawOnChartArea: false },
            ticks: { color: "#bc8cff", font: { family: "ui-monospace, monospace", size: 10 } },
            title: { display: true, text: fmtMetricName, color: "#bc8cff" },
          },
        },
        plugins: {
          legend: { labels: { color: "#f0f6fc", font: { family: "-apple-system, sans-serif", size: 11 } } },
        },
      },
    });
  }

  // Window Telemetry Table
  const tbody = document.getElementById("timelineTableBody");
  tbody.innerHTML = "";
  points.forEach((p) => {
    const tr = document.createElement("tr");
    const hColor = p.health_score >= 99 ? "var(--green)" : (p.health_score >= 80 ? "var(--amber)" : "var(--red)");
    const aColor = p.is_anomaly ? "var(--red)" : "var(--text-dim)";
    const evBadge = p.events && p.events.length > 0 ? `<span class="badge badge-purple">${p.events.length} event(s)</span>` : `<span class="badge badge-dim">None</span>`;

    tr.innerHTML = `
      <td><strong>W${p.window_index}</strong></td>
      <td><code>[${p.unit_offset_start}..${p.unit_offset_end})</code></td>
      <td><code>[${p.byte_offset_start}..${p.byte_offset_end})</code></td>
      <td>${p.payload_kb.toFixed(1)} KB</td>
      <td><span style="font-weight:600; font-family:var(--font-mono); color:${hColor};">${p.health_score.toFixed(1)}%</span></td>
      <td><span style="font-weight:600; font-family:var(--font-mono); color:${aColor};">${p.anomaly_score.toFixed(4)}</span></td>
      <td><span class="badge ${p.anomaly_severity === "CRITICAL" ? "badge-critical" : (p.is_anomaly ? "badge-warning" : "badge-dim")}">${p.anomaly_severity}</span></td>
      <td>${evBadge}</td>
    `;
    tbody.appendChild(tr);
  });
}

// -----------------------------------------------------------------------------
// 9. Render View 4: Comparison (F6)
// -----------------------------------------------------------------------------

async function executeComparison(isHalf = false) {
  const pathA = document.getElementById("compStreamA").value.trim() || document.getElementById("customPathInput").value.trim();
  const pathB = isHalf ? pathA : document.getElementById("compStreamB").value.trim();

  if (!pathA) {
    showNotification("Please specify Stream A path for comparison.", true);
    return;
  }
  if (!isHalf && !pathB) {
    showNotification("Please specify Stream B path for comparison.", true);
    return;
  }

  showNotification("Executing F6 comparison engine...");

  try {
    const payload = {
      file_path_a: pathA,
      file_path_b: pathB,
      is_half_comparison: isHalf,
    };

    const res = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonStringifySafe(payload),
    });

    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || "Comparison failed");
    }

    currentComparison = data;
    renderComparisonView(data);
    switchTab("tab-comparison");
    showNotification("Stream comparison complete.");
  } catch (err) {
    console.error("Comparison error:", err);
    showNotification(`Comparison Error: ${err.message}`, true);
  }
}

function renderComparisonView(data) {
  const resDiv = document.getElementById("comparisonResults");
  resDiv.style.display = "block";

  const comp = data.comparison;
  const sameFmt = comp.is_same_format;

  document.getElementById("compFormatEquiv").textContent = sameFmt ? "SAME FORMAT" : "CROSS FORMAT";
  document.getElementById("compFormatEquiv").className = `stat-value ${sameFmt ? "green" : "amber"}`;
  document.getElementById("compFormatNames").textContent = `${comp.format_a} vs ${comp.format_b}`;

  const winAlign = comp.windows || {};
  document.getElementById("compAlignmentMode").textContent = winAlign.alignment_mode || "DIRECT_INDEX";
  document.getElementById("compAlignedCount").textContent = `Aligned windows: ${winAlign.aligned_window_count || 0}`;

  // Read total_payload_bytes from comp.common.metrics dynamically
  const payloadMetric = comp.common?.metrics?.total_payload_bytes;
  if (payloadMetric && payloadMetric.absolute_difference !== null) {
    const absDiff = payloadMetric.absolute_difference;
    const relPct = payloadMetric.relative_difference_pct;
    const pctStr = relPct !== null ? `${relPct > 0 ? "+" : ""}${relPct.toFixed(2)}%` : "N/A";
    const deltaStr = `${absDiff > 0 ? "+" : ""}${Math.round(absDiff).toLocaleString()} B (${pctStr})`;
    document.getElementById("compPayloadDelta").textContent = deltaStr;
    document.getElementById("compPayloadSig").textContent = `Significance: ${payloadMetric.significance || payloadMetric.classification || "N/A"}`;
  } else if (payloadMetric && payloadMetric.classification === "NOT_COMPARABLE") {
    document.getElementById("compPayloadDelta").textContent = "NOT COMPARABLE";
    document.getElementById("compPayloadSig").textContent = payloadMetric.incompatibility_reason || "Format invariant";
  } else {
    document.getElementById("compPayloadDelta").textContent = "--";
    document.getElementById("compPayloadSig").textContent = "Significance: --";
  }

  const tbody = document.getElementById("semanticAuditTableBody");
  tbody.innerHTML = "";

  const auditRows = [
    {
      metric: "total_payload_bytes",
      status: "COMPARABLE",
      badge: "badge-healthy",
      rationale: "Normalized physical byte throughput carries invariant physical meaning across all framing layers.",
      result: "Compared",
    },
    {
      metric: "integrity_ratio",
      status: "COMPARABLE",
      badge: "badge-healthy",
      rationale: "Normalized syntactic validity proportion [0.0..1.0] reflects error-free framing compliance.",
      result: "Compared",
    },
    {
      metric: "total_units",
      status: "NOT_COMPARABLE",
      badge: "badge-critical",
      rationale: "188B TS packet vs variable GSE PDU vs ~7.2KB BBFrame represent physically incompatible containers.",
      result: sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard",
    },
    {
      metric: "valid_units",
      status: "NOT_COMPARABLE",
      badge: "badge-critical",
      rationale: "Unit boundaries and framing capacities differ fundamentally across formats.",
      result: sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard",
    },
    {
      metric: "invalid_units",
      status: "NOT_COMPARABLE",
      badge: "badge-critical",
      rationale: "BBFrames and TS packets represent substantially different framing capacities; unit-level counts are not comparable.",
      result: sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard",
    },
    {
      metric: "mean_payload_bytes",
      status: "NOT_COMPARABLE",
      badge: "badge-critical",
      rationale: "Reflects framing container capacity, not transmission throughput.",
      result: sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard",
    },
    {
      metric: "payload_ratio",
      status: "NOT_COMPARABLE",
      badge: "badge-critical",
      rationale: "TS measures packet presence; GSE and BBFrame measure byte packing efficiency.",
      result: sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard",
    },
    {
      metric: "error_count",
      status: "NOT_COMPARABLE",
      badge: "badge-critical",
      rationale: "Aggregates heterogeneous failure classes (TS sync byte vs BBHeader CRC-8 vs GSE PDU syntax).",
      result: sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard",
    },
    {
      metric: "error_rate",
      status: "NOT_COMPARABLE",
      badge: "badge-critical",
      rationale: "Normalized per framing unit with physically incomparable denominators.",
      result: sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard",
    },
    {
      metric: "entropy",
      status: "NOT_COMPARABLE",
      badge: "badge-critical",
      rationale: "Measures distinct state spaces (PID multiplex vs EtherType network protocol vs continuous DFL sizing).",
      result: sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard",
    },
  ];

  auditRows.forEach((row) => {
    const tr = document.createElement("tr");
    const mData = comp.common?.metrics?.[row.metric];

    let resultCell = sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard";
    if (mData) {
      if (mData.absolute_difference !== null) {
        const sign = mData.absolute_difference > 0 ? "+" : "";
        const relStr = mData.relative_difference_pct !== null ? ` (${sign}${mData.relative_difference_pct.toFixed(2)}%)` : "";
        resultCell = `${sign}${mData.absolute_difference.toLocaleString()}${mData.unit || ""}${relStr} [${mData.significance || mData.classification}]`;
      } else if (mData.classification === "NOT_COMPARABLE") {
        resultCell = sameFmt ? "Evaluated within same format" : "Blocked by F6 Cross-Format Guard";
      }
    }

    tr.innerHTML = `
      <td><code>${escapeHtml(row.metric)}</code></td>
      <td><span class="badge ${row.badge}">${row.status}</span></td>
      <td>${escapeHtml(row.rationale)}</td>
      <td><code>${escapeHtml(resultCell)}</code></td>
    `;
    tbody.appendChild(tr);
  });
}

// -----------------------------------------------------------------------------
// 10. Render View 5: Automatic Report (F7)
// -----------------------------------------------------------------------------

function renderReportView(data) {
  const rep = data.f7_report;
  if (!rep) return;

  document.getElementById("repStreamTitle").innerHTML = `Automatic Analysis Report: <code>${escapeHtml(data.stream_info.file_name)}</code>`;
  document.getElementById("repTimestamp").textContent = `Report ID: ${rep.report_id} | Mode: ${rep.mode} | Generated: ${rep.timestamp}`;

  document.getElementById("btnDownloadJson").href = "/api/export?format=json&mode=analysis";
  document.getElementById("btnDownloadMd").href = "/api/export?format=markdown&mode=analysis";
  document.getElementById("btnDownloadTxt").href = "/api/export?format=text&mode=analysis";
  document.getElementById("btnDownloadHtml").href = "/api/export?format=html&mode=analysis";

  renderReportFindings();
}

function renderReportFindings() {
  const container = document.getElementById("reportFindingsContainer");
  if (!currentAnalysis || !currentAnalysis.f7_report) {
    container.innerHTML = `<p style="color: var(--text-dim); font-size:12px;">No analysis report generated yet.</p>`;
    return;
  }

  const findings = currentAnalysis.f7_report.tripartite_findings || [];
  const filtered = activeTripartiteFilter === "ALL" 
    ? findings 
    : findings.filter((f) => f.category === activeTripartiteFilter);

  if (filtered.length === 0) {
    container.innerHTML = `<p style="color: var(--text-dim); font-size:12px;">No findings found under category <code>${activeTripartiteFilter}</code>.</p>`;
    return;
  }

  container.innerHTML = filtered.map((f) => {
    let catBadge = "badge-info";
    if (f.category === "OBSERVED_FACT") catBadge = "badge-healthy";
    if (f.category === "STATISTICAL_FINDING") catBadge = "badge-purple";
    if (f.category === "ENGINEERING_INTERPRETATION") catBadge = "badge-warning";

    return `
      <div style="background: var(--bg-canvas); border: 1px solid var(--border-default); border-radius: 3px; padding: 10px 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <strong style="color: var(--text-main); font-size: 12.5px;">${escapeHtml(f.summary)}</strong>
          <span class="badge ${catBadge}">${escapeHtml(f.category)}</span>
        </div>
        <div style="font-size: 11.5px; color: var(--text-dim); margin-bottom: 4px;">
          ${escapeHtml(f.evidence)}
        </div>
        <div style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">
          Epistemic Grounding: ${escapeHtml(f.epistemic_grounding || "Telemetry")}
        </div>
      </div>
    `;
  }).join("");
}

// -----------------------------------------------------------------------------
// Utilities
// -----------------------------------------------------------------------------

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function jsonStringifySafe(obj) {
  return JSON.stringify(obj, (k, v) => (typeof v === "number" && isNaN(v) ? null : v));
}
