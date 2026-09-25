"use client";

import React from "react";

export const DocumentationSection: React.FC = () => {
  return (
    <section id="documentation" className="w-full border-b border-[#262626] bg-[#0A0A0A] py-12">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="border-b border-[#262626] pb-4 mb-8">
          <div className="font-mono text-[12px] text-[#737373] uppercase mb-1">
            SECTION [07] // SPECIFICATIONS &amp; ENGINEERING REPRODUCIBILITY
          </div>
          <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[#E8E8E8]">
            SYSTEM DOCUMENTATION &amp; TECH STACK
          </h2>
          <p className="text-[14px] text-[#737373] max-w-[800px] mt-2">
            Complete technical specification, verified software requirements, and installation protocol
            for the PRJ_111 DVB-S2 multi-format receiver output analyzer.
          </p>
        </div>

        {/* Technologies Used Table */}
        <div className="mb-10">
          <div className="font-mono text-[12px] text-[#737373] uppercase mb-3 flex items-center justify-between">
            <span>[TECHNOLOGIES_USED_MATRIX]</span>
            <span className="text-[#FF6B35]">VERIFIED ACTIVE STACK</span>
          </div>

          <div className="border border-[#262626] bg-[#141414] overflow-x-auto">
            <table className="w-full border-collapse font-mono text-[12px] text-left">
              <thead>
                <tr className="border-b border-[#262626] bg-[#0A0A0A] text-[#737373]">
                  <th className="p-3 border-r border-[#262626]">LAYER</th>
                  <th className="p-3 border-r border-[#262626]">TECHNOLOGY / RUNTIME</th>
                  <th className="p-3 border-r border-[#262626]">VERSION</th>
                  <th className="p-3">OPERATIONAL PURPOSE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1A1A1A] text-[#E8E8E8]">
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="p-3 border-r border-[#262626] font-bold">Frontend Framework</td>
                  <td className="p-3 border-r border-[#262626] text-white">Next.js (App Router)</td>
                  <td className="p-3 border-r border-[#262626] text-[#FF6B35]">15.2+ (15.5.26)</td>
                  <td className="p-3 text-[#737373]">High-performance engineering workstation &amp; hybrid showcase</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="p-3 border-r border-[#262626] font-bold">UI Component Core</td>
                  <td className="p-3 border-r border-[#262626] text-white">React</td>
                  <td className="p-3 border-r border-[#262626] text-[#FF6B35]">19.0+ (19.3.0)</td>
                  <td className="p-3 text-[#737373]">Server &amp; Client components with zero 3rd-party component libraries</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="p-3 border-r border-[#262626] font-bold">Type System</td>
                  <td className="p-3 border-r border-[#262626] text-white">TypeScript</td>
                  <td className="p-3 border-r border-[#262626] text-[#FF6B35]">5.7+ (5.9.3)</td>
                  <td className="p-3 text-[#737373]">Strict compile-time schema safety for all F1-F7 API responses</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="p-3 border-r border-[#262626] font-bold">Styling &amp; Design Tokens</td>
                  <td className="p-3 border-r border-[#262626] text-white">Tailwind CSS</td>
                  <td className="p-3 border-r border-[#262626] text-[#FF6B35]">v4.0+ (4.3.3)</td>
                  <td className="p-3 text-[#737373]">Swiss typography scale, industrial 0px radius, zero box-shadows</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="p-3 border-r border-[#262626] font-bold">Analysis Backend</td>
                  <td className="p-3 border-r border-[#262626] text-white">Python</td>
                  <td className="p-3 border-r border-[#262626] text-[#FF6B35]">3.12+ (3.12.3)</td>
                  <td className="p-3 text-[#737373]">Binary parsers (TS, GSE, BBFrame), feature extraction, health check</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="p-3 border-r border-[#262626] font-bold">HTTP / REST API</td>
                  <td className="p-3 border-r border-[#262626] text-white">ThreadingHTTPServer</td>
                  <td className="p-3 border-r border-[#262626] text-[#737373]">Standard Library</td>
                  <td className="p-3 text-[#737373]">Multi-threaded REST endpoints on localhost:8080 (zero external web framework overhead)</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="p-3 border-r border-[#262626] font-bold">AI / Anomaly Detection</td>
                  <td className="p-3 border-r border-[#262626] text-white">scikit-learn (Isolation Forest)</td>
                  <td className="p-3 border-r border-[#262626] text-[#FF6B35]">1.5+</td>
                  <td className="p-3 text-[#737373]">Feature F2 unsupervised framing anomaly detection</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="p-3 border-r border-[#262626] font-bold">Numerical Computation</td>
                  <td className="p-3 border-r border-[#262626] text-white">NumPy</td>
                  <td className="p-3 border-r border-[#262626] text-[#FF6B35]">1.26+</td>
                  <td className="p-3 text-[#737373]">Window aggregation, rolling feature matrices, bounded Z-score computation</td>
                </tr>
                <tr className="hover:bg-[#1a1a1a]">
                  <td className="p-3 border-r border-[#262626] font-bold">Automated Test Suite</td>
                  <td className="p-3 border-r border-[#262626] text-white">Python unittest</td>
                  <td className="p-3 border-r border-[#262626] text-[#E8E8E8]">240 Tests</td>
                  <td className="p-3 text-[#737373]">207 Backend + 33 Frontend integration tests (100% pass invariant)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Installation & Reproduction Protocol (Asymmetric 8/4 Split) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Reproduction Commands (8 cols) */}
          <div className="lg:col-span-8 border border-[#262626] bg-[#141414] p-6 space-y-6">
            <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#262626] pb-2">
              [INSTALLATION_AND_STARTUP_PROTOCOL]
            </div>

            {/* Step 1: Backend */}
            <div className="space-y-2">
              <div className="font-mono text-[14px] text-[#E8E8E8] font-bold">
                1. START PYTHON ANALYSIS BACKEND (PORT 8080):
              </div>
              <div className="p-3 bg-[#0A0A0A] border border-[#262626] font-mono text-[12px] text-[#E8E8E8]">
                <div className="text-[#737373]"># From repository root:</div>
                <div>cd 05_CODE</div>
                <div>.venv\Scripts\python.exe run_frontend.py</div>
                <div className="text-[#737373] mt-1"># Verified output: PRJ_111 Frontend Server running at http://127.0.0.1:8080</div>
              </div>
            </div>

            {/* Step 2: Frontend */}
            <div className="space-y-2">
              <div className="font-mono text-[14px] text-[#E8E8E8] font-bold">
                2. START NEXT.JS 15 WORKSTATION (PORT 3000):
              </div>
              <div className="p-3 bg-[#0A0A0A] border border-[#262626] font-mono text-[12px] text-[#E8E8E8]">
                <div className="text-[#737373]"># From web application folder:</div>
                <div>cd 05_CODE/web</div>
                <div>npm install</div>
                <div>npm run dev</div>
                <div className="text-[#737373] mt-1"># Open http://localhost:3000 in modern web browser</div>
              </div>
            </div>

            {/* Step 3: Verification Suite */}
            <div className="space-y-2">
              <div className="font-mono text-[14px] text-[#E8E8E8] font-bold">
                3. VERIFY AUTOMATED REGRESSION SUITE:
              </div>
              <div className="p-3 bg-[#0A0A0A] border border-[#262626] font-mono text-[12px] text-[#E8E8E8]">
                <div className="text-[#737373]"># Run all 240 backend and frontend tests:</div>
                <div>cd 05_CODE</div>
                <div>.venv\Scripts\python.exe -m unittest discover -s tests</div>
                <div className="text-[#737373] mt-1"># Expected result: Ran 240 tests ... OK (0 failures, 0 errors)</div>
              </div>
            </div>
          </div>

          {/* System Boundaries & Standards (4 cols) */}
          <div className="lg:col-span-4 border border-[#262626] bg-[#141414] p-6 flex flex-col justify-between">
            <div>
              <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#262626] pb-2 mb-4">
                [SYSTEM_BOUNDARIES]
              </div>

              <div className="space-y-3 font-mono text-[12px] text-[#737373]">
                <p>
                  <strong className="text-[#E8E8E8]">NO RF HARDWARE DIRECT ACCESS:</strong> The software analyzes
                  post-demodulated digital stream dumps. No tuner controls, LNB power, or direct RF carrier interfaces.
                </p>
                <p>
                  <strong className="text-[#E8E8E8]">NO FORMAL ETSI CERTIFICATION:</strong> Checks are inspired by ETSI
                  TR 101 290 principles for telemetry triage. No formal ETSI laboratory compliance is claimed.
                </p>
                <p>
                  <strong className="text-[#E8E8E8]">CONTENT DETECTION INDEPENDENCE:</strong> .ts file extension is
                  treated as an opaque container; format detection inspects underlying sync headers and PDU headers.
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[#1A1A1A] font-mono text-[12px]">
              <div className="text-[#737373]">PROJECT IDENTITY:</div>
              <div className="text-[#E8E8E8] font-bold">PRJ_111 // REVIEW-2 MILESTONE</div>
              <div className="text-[#737373]">DOCUMENTED UNDER 07_DOCUMENTATION/</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
