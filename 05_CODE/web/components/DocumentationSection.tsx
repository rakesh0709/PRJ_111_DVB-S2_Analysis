"use client";

import React from "react";
import { Tooltip } from "@/components/Tooltip";

export const DocumentationSection: React.FC = () => {
  return (
    <section id="documentation" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="border-b border-[var(--border-main)] pb-4 mb-8">
          <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase mb-1 flex items-center gap-2">
            <span>SECTION [07]</span>
            <span>//</span>
            <Tooltip content="Architecture specifications, component breakdown, dependencies, and reproducible build instructions">
              <span>SPECIFICATIONS &amp; ENGINEERING REPRODUCIBILITY</span>
            </Tooltip>
          </div>
          <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[var(--text-main)]">
            SYSTEM DOCUMENTATION &amp; TECH STACK
          </h2>
          <p className="text-[14px] text-[var(--text-muted)] max-w-[800px] mt-2 leading-relaxed">
            Complete technical specification, verified software requirements, and installation protocol
            for the PRJ_111 DVB-S2 multi-format receiver output analyzer.
          </p>
        </div>

        {/* Technologies Used Table */}
        <div className="mb-10">
          <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase mb-3 flex items-center justify-between">
            <span>[TECHNOLOGIES_USED_MATRIX]</span>
            <span className="text-[#FF6B35] font-semibold">VERIFIED ACTIVE STACK</span>
          </div>

          <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] overflow-x-auto transition-colors duration-150">
            <table className="w-full border-collapse font-mono text-[12px] text-left">
              <thead>
                <tr className="border-b border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-muted)]">
                  <th className="p-3 border-r border-[var(--border-main)]">LAYER</th>
                  <th className="p-3 border-r border-[var(--border-main)]">TECHNOLOGY / RUNTIME</th>
                  <th className="p-3 border-r border-[var(--border-main)]">VERSION</th>
                  <th className="p-3">OPERATIONAL PURPOSE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-dim)] text-[var(--text-main)]">
                <tr className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
                  <td className="p-3 border-r border-[var(--border-main)] font-bold">Frontend Framework</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">Next.js (App Router)</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[#FF6B35]">15.2+ (15.5.26)</td>
                  <td className="p-3 text-[var(--text-muted)]">High-performance engineering workstation &amp; hybrid showcase</td>
                </tr>
                <tr className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
                  <td className="p-3 border-r border-[var(--border-main)] font-bold">UI Component Core</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">React</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[#FF6B35]">19.0+ (19.3.0)</td>
                  <td className="p-3 text-[var(--text-muted)]">Server &amp; Client components with zero 3rd-party component libraries</td>
                </tr>
                <tr className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
                  <td className="p-3 border-r border-[var(--border-main)] font-bold">Type System</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">TypeScript</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[#FF6B35]">5.7+ (5.9.3)</td>
                  <td className="p-3 text-[var(--text-muted)]">Strict compile-time schema safety for all F1-F7 API responses</td>
                </tr>
                <tr className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
                  <td className="p-3 border-r border-[var(--border-main)] font-bold">Styling &amp; Design Tokens</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">Tailwind CSS</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[#FF6B35]">v4.0+ (4.3.3)</td>
                  <td className="p-3 text-[var(--text-muted)]">Swiss typography scale, industrial 0px radius, zero box-shadows</td>
                </tr>
                <tr className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
                  <td className="p-3 border-r border-[var(--border-main)] font-bold">Analysis Backend</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">Python</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[#FF6B35]">3.12+ (3.12.3)</td>
                  <td className="p-3 text-[var(--text-muted)]">Binary parsers (TS, GSE, BBFrame), feature extraction, health check</td>
                </tr>
                <tr className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
                  <td className="p-3 border-r border-[var(--border-main)] font-bold">HTTP / REST API</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">ThreadingHTTPServer</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-muted)]">Standard Library</td>
                  <td className="p-3 text-[var(--text-muted)]">Multi-threaded REST endpoints on localhost:8080 (zero external web framework overhead)</td>
                </tr>
                <tr className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
                  <td className="p-3 border-r border-[var(--border-main)] font-bold">AI / Anomaly Detection</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">scikit-learn (Isolation Forest)</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[#FF6B35]">1.5+</td>
                  <td className="p-3 text-[var(--text-muted)]">Feature F2 unsupervised framing anomaly detection</td>
                </tr>
                <tr className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
                  <td className="p-3 border-r border-[var(--border-main)] font-bold">Numerical Computation</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">NumPy</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[#FF6B35]">1.26+</td>
                  <td className="p-3 text-[var(--text-muted)]">Window aggregation, rolling feature matrices, bounded Z-score computation</td>
                </tr>
                <tr className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
                  <td className="p-3 border-r border-[var(--border-main)] font-bold">Automated Test Suite</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">Python unittest</td>
                  <td className="p-3 border-r border-[var(--border-main)] text-[var(--text-main)]">240 Tests</td>
                  <td className="p-3 text-[var(--text-muted)]">207 Backend + 33 Frontend integration tests (100% pass invariant)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Installation & Reproduction Protocol (Asymmetric 8/4 Split) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Reproduction Commands (8 cols) */}
          <div className="lg:col-span-8 border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 space-y-6 transition-colors duration-150">
            <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase border-b border-[var(--border-dim)] pb-2">
              [INSTALLATION_AND_STARTUP_PROTOCOL]
            </div>

            {/* Step 1: Backend */}
            <div className="space-y-2">
              <div className="font-mono text-[14px] text-[var(--text-main)] font-bold">
                1. START PYTHON ANALYSIS BACKEND (PORT 8080):
              </div>
              <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)] font-mono text-[12px] text-[var(--text-main)]">
                <div className="text-[var(--text-muted)]"># From repository root:</div>
                <div>cd 05_CODE</div>
                <div>.venv\Scripts\python.exe run_frontend.py</div>
                <div className="text-[var(--text-muted)] mt-1"># Verified output: PRJ_111 Frontend Server running at http://127.0.0.1:8080</div>
              </div>
            </div>

            {/* Step 2: Frontend */}
            <div className="space-y-2">
              <div className="font-mono text-[14px] text-[var(--text-main)] font-bold">
                2. START NEXT.JS 15 WORKSTATION (PORT 3000):
              </div>
              <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)] font-mono text-[12px] text-[var(--text-main)]">
                <div className="text-[var(--text-muted)]"># From web application folder:</div>
                <div>cd 05_CODE/web</div>
                <div>npm install</div>
                <div>npm run dev</div>
                <div className="text-[var(--text-muted)] mt-1"># Open http://localhost:3000 in modern web browser</div>
              </div>
            </div>

            {/* Step 3: Verification Suite */}
            <div className="space-y-2">
              <div className="font-mono text-[14px] text-[var(--text-main)] font-bold">
                3. VERIFY AUTOMATED REGRESSION SUITE:
              </div>
              <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)] font-mono text-[12px] text-[var(--text-main)]">
                <div className="text-[var(--text-muted)]"># Run all 240 backend and frontend tests:</div>
                <div>cd 05_CODE</div>
                <div>.venv\Scripts\python.exe -m unittest discover -s tests</div>
                <div className="text-[var(--text-muted)] mt-1"># Expected result: Ran 240 tests ... OK (0 failures, 0 errors)</div>
              </div>
            </div>
          </div>

          {/* System Boundaries & Standards (4 cols) */}
          <div className="lg:col-span-4 border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 flex flex-col justify-between transition-colors duration-150">
            <div>
              <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase border-b border-[var(--border-dim)] pb-2 mb-4">
                [SYSTEM_BOUNDARIES]
              </div>

              <div className="space-y-3 font-mono text-[12px] text-[var(--text-muted)] leading-relaxed">
                <p>
                  <strong className="text-[var(--text-main)]">NO RF HARDWARE DIRECT ACCESS:</strong> The software analyzes
                  post-demodulated digital stream dumps. No tuner controls, LNB power, or direct RF carrier interfaces.
                </p>
                <p>
                  <strong className="text-[var(--text-main)]">NO FORMAL ETSI CERTIFICATION:</strong> Checks are inspired by ETSI
                  TR 101 290 principles for telemetry triage. No formal ETSI laboratory compliance is claimed.
                </p>
                <p>
                  <strong className="text-[var(--text-main)]">CONTENT DETECTION INDEPENDENCE:</strong> .ts file extension is
                  treated as an opaque container; format detection inspects underlying sync headers and PDU headers.
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[var(--border-dim)] font-mono text-[12px]">
              <div className="text-[var(--text-muted)]">PROJECT IDENTITY:</div>
              <div className="text-[var(--text-main)] font-bold">PRJ_111 // REVIEW-2 MILESTONE</div>
              <div className="text-[var(--text-muted)]">DOCUMENTED UNDER 07_DOCUMENTATION/</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
