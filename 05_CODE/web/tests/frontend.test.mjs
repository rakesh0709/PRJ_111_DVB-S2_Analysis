import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const webDir = path.resolve(__dirname, "..");

test("PRJ_111 Frontend Test Suite: Offline Data Verification", async (t) => {
  await t.test("MPEG-TS empirical dataset matches authoritative metrics", async () => {
    const offlineDataFile = path.join(webDir, "lib", "offlineData.ts");
    assert.ok(fs.existsSync(offlineDataFile), "offlineData.ts must exist");
    const content = fs.readFileSync(offlineDataFile, "utf-8");

    // Assert key values
    assert.ok(content.includes('"format": "MPEG_TS"'), "MPEG_TS format present");
    assert.ok(content.includes('"total_units": 18176'), "18,176 TS packets present");
    assert.ok(content.includes('"total_windows": 91'), "91 analysis windows present");
    assert.ok(content.includes('"window_size": 200'), "Window size 200 present");
    assert.ok(content.includes('"integrity_ratio": 100.0'), "100.0% integrity present");
    assert.ok(content.includes('"peak_anomaly_score": 0.8576'), "Peak anomaly score 0.8576 present");
  });

  await t.test("GSE empirical dataset matches authoritative metrics", async () => {
    const offlineDataFile = path.join(webDir, "lib", "offlineData.ts");
    const content = fs.readFileSync(offlineDataFile, "utf-8");

    assert.ok(content.includes('"format": "GSE"'), "GSE format present");
    assert.ok(content.includes('"total_units": 14'), "14 PDUs present");
    assert.ok(content.includes('"total_windows": 5'), "5 analysis windows present");
    assert.ok(content.includes('"window_size": 3'), "Window size 3 present");
    assert.ok(content.includes('"peak_anomaly_score": 0.5018'), "Peak anomaly score 0.5018 present");
  });

  await t.test("BBFrame empirical dataset matches authoritative metrics", async () => {
    const offlineDataFile = path.join(webDir, "lib", "offlineData.ts");
    const content = fs.readFileSync(offlineDataFile, "utf-8");

    assert.ok(content.includes('"format": "BB_FRAME"'), "BB_FRAME format present");
    assert.ok(content.includes('"total_units": 4309'), "4,309 frames present");
    assert.ok(content.includes('"total_windows": 87'), "87 analysis windows present");
    assert.ok(content.includes('"window_size": 50'), "Window size 50 present");
    assert.ok(content.includes('"peak_anomaly_score": 0.7406'), "Peak anomaly score 0.7406 present");
  });
});

test("PRJ_111 Frontend Test Suite: F6 Semantic Barrier & Guard", async (t) => {
  await t.test("Comparison data enforces 2 comparable vs 9 incommensurable metrics", async () => {
    const compFile = path.resolve(webDir, "..", "..", "06_RESULTS", "comparisons", "comparison_cross_format_ts_bbframe.json");
    assert.ok(fs.existsSync(compFile), "Cross format comparison file must exist");
    const compData = JSON.parse(fs.readFileSync(compFile, "utf-8"));

    const common = compData.common?.metrics || compData.common;
    assert.ok(common.total_payload_bytes, "total_payload_bytes must exist");
    assert.ok(common.integrity_ratio, "integrity_ratio must exist");
    assert.notEqual(common.total_payload_bytes.classification, "NOT_COMPARABLE");
    assert.notEqual(common.integrity_ratio.classification, "NOT_COMPARABLE");

    // Incommensurable metrics
    const incommensurable = [
      "total_units",
      "valid_units",
      "invalid_units",
      "truncated_units",
      "mean_payload_bytes",
      "payload_ratio",
      "error_count",
      "error_rate",
      "entropy"
    ];

    for (const m of incommensurable) {
      assert.equal(common[m].classification, "NOT_COMPARABLE", `${m} must be classified NOT_COMPARABLE`);
    }

    // Safety guard checks
    const guard = compData.unsupported_inferences_guard;
    assert.ok(Array.isArray(guard), "Guard must be an array");
    assert.ok(guard.length >= 5, "Guard must contain all physical layer prohibitions");
  });
});

test("PRJ_111 Frontend Test Suite: Next.js Production Build Artifacts", async (t) => {
  await t.test("Build output directory contains compiled routes", async () => {
    const nextDir = path.join(webDir, ".next");
    assert.ok(fs.existsSync(nextDir), ".next build directory must exist");
    const buildManifest = path.join(nextDir, "build-manifest.json");
    assert.ok(fs.existsSync(buildManifest), "build-manifest.json must exist");
  });

  await t.test("Design tokens & CSS rules enforce non-negotiable styling constraints", async () => {
    const cssFile = path.join(webDir, "app", "globals.css");
    assert.ok(fs.existsSync(cssFile), "globals.css must exist");
    const cssContent = fs.readFileSync(cssFile, "utf-8");

    // Strict color tokens
    assert.ok(cssContent.includes("#0A0A0A"), "Background #0A0A0A token present");
    assert.ok(cssContent.includes("#141414"), "Surface #141414 token present");
    assert.ok(cssContent.includes("#E8E8E8"), "Text Primary #E8E8E8 token present");
    assert.ok(cssContent.includes("#737373"), "Text Secondary #737373 token present");
    assert.ok(cssContent.includes("#262626"), "Border #262626 token present");
    assert.ok(cssContent.includes("#FF6B35"), "Single Accent #FF6B35 token present");

    // Non-negotiable zero-rounding
    assert.ok(cssContent.includes("border-radius: 0px !important"), "Zero rounding enforced");
    assert.ok(cssContent.includes("box-shadow: none !important"), "Zero shadows enforced");
  });
});
