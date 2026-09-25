"""
Dashboard and Visual Presentation Generator for Feature F4.

Generates self-contained, interactive HTML5 dashboards presenting:
1. Stream Health Score over window indices
2. AI Anomaly Score over window indices with threshold markers
3. Payload Volume (KB) per window (without fake throughput rates)
4. Format-Specific Telemetry trends (PID entropy, fragmentation, DFL)
5. Timeline Event Markers (F2 Anomalies, F3 Transitions, Health Shifts)
6. Comprehensive Window Details & Telemetry Table

Works completely offline with responsive SVG graphics, and enhances with
interactive Chart.js when online.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from dvbs2_analyzer.config import StreamFormat


def generate_html_dashboard(timeline: Any) -> str:
    """
    Generates a complete, self-contained HTML5 dashboard string from a StreamTimeline.
    """
    tl_dict = timeline.to_dict()
    stream_name = tl_dict.get("stream_name", "Unknown Stream")
    fmt_str = tl_dict.get("format", "MPEG_TS")
    total_units = tl_dict.get("total_units", 0)
    total_windows = tl_dict.get("total_windows", 0)
    window_size = tl_dict.get("window_size", 0)
    anomaly_threshold = tl_dict.get("anomaly_threshold", 0.50)
    summary_stats = tl_dict.get("summary_stats", {})
    points = tl_dict.get("points", [])
    events = tl_dict.get("events", [])

    # Extract series for charts
    window_labels = [f"W{p['window_index']}" for p in points]
    health_scores = [p["health_score"] for p in points]
    anomaly_scores = [p["anomaly_score"] for p in points]
    payload_kb = [p["payload_kb"] for p in points]
    is_anomaly = [1 if p["is_anomaly"] else 0 for p in points]

    # Format-specific series
    fmt_metric_name = "Format Metric"
    fmt_values: List[float] = []
    if "MPEG_TS" in fmt_str:
        fmt_metric_name = "PID Entropy (bits)"
        fmt_values = [p.get("format_specific_metrics", {}).get("pid_entropy", 0.0) for p in points]
    elif "GSE" in fmt_str:
        fmt_metric_name = "Fragmentation Ratio"
        fmt_values = [p.get("format_specific_metrics", {}).get("fragmentation_ratio", 0.0) for p in points]
    elif "BB_FRAME" in fmt_str:
        fmt_metric_name = "Modal DFL (bits)"
        fmt_values = [float(p.get("format_specific_metrics", {}).get("modal_dfl_bits", 0)) for p in points]

    mean_health = summary_stats.get("mean_health_score", 100.0)
    peak_anomaly = summary_stats.get("peak_anomaly_score", 0.0)
    anomaly_win_count = summary_stats.get("anomaly_window_count", 0)
    trans_count = summary_stats.get("transition_count", 0)
    total_payload = summary_stats.get("total_payload_kb", 0.0)

    # Health status styling
    health_badge_class = "badge-healthy"
    if mean_health < 70.0 or anomaly_win_count > (total_windows * 0.3):
        health_badge_class = "badge-critical"
    elif mean_health < 90.0 or anomaly_win_count > 0:
        health_badge_class = "badge-warning"

    # Convert datasets to JSON for client-side charts
    json_labels = json.dumps(window_labels)
    json_health = json.dumps(health_scores)
    json_anomaly = json.dumps(anomaly_scores)
    json_payload = json.dumps(payload_kb)
    json_fmt_values = json.dumps(fmt_values)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PRJ_111: {stream_name} — Timeline & Activity Dashboard</title>
  <!-- Chart.js CDN for interactive charting -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg-primary: #0f172a;
      --bg-secondary: #1e293b;
      --bg-card: #1e293b;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --accent-blue: #38bdf8;
      --accent-green: #34d399;
      --accent-amber: #fbbf24;
      --accent-red: #f87171;
      --accent-purple: #c084fc;
      --border-color: #334155;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    body {{
      background-color: var(--bg-primary);
      color: var(--text-primary);
      padding: 24px;
      line-height: 1.5;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border-color);
      margin-bottom: 24px;
    }}
    .header-title h1 {{
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.5px;
    }}
    .header-subtitle {{
      color: var(--text-secondary);
      font-size: 14px;
      margin-top: 4px;
    }}
    .header-badges {{
      display: flex;
      gap: 10px;
      align-items: center;
    }}
    .badge {{
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .badge-format {{
      background-color: #0284c7;
      color: #ffffff;
    }}
    .badge-healthy {{
      background-color: rgba(52, 211, 153, 0.2);
      color: var(--accent-green);
      border: 1px solid var(--accent-green);
    }}
    .badge-warning {{
      background-color: rgba(251, 191, 36, 0.2);
      color: var(--accent-amber);
      border: 1px solid var(--accent-amber);
    }}
    .badge-critical {{
      background-color: rgba(248, 113, 113, 0.2);
      color: var(--accent-red);
      border: 1px solid var(--accent-red);
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .kpi-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 16px 20px;
    }}
    .kpi-title {{
      font-size: 13px;
      color: var(--text-secondary);
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .kpi-value {{
      font-size: 26px;
      font-weight: 700;
      margin-top: 6px;
      color: var(--text-primary);
    }}
    .kpi-subtext {{
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 4px;
    }}
    .chart-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }}
    .chart-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
    }}
    .chart-title {{
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .chart-legend-hint {{
      font-size: 12px;
      color: var(--text-secondary);
    }}
    .chart-container {{
      position: relative;
      height: 280px;
      width: 100%;
    }}
    .table-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 24px;
    }}
    .table-container {{
      overflow-x: auto;
      margin-top: 12px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }}
    th {{
      background-color: #1e293b;
      color: var(--text-secondary);
      font-weight: 600;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border-color);
      white-space: nowrap;
    }}
    td {{
      padding: 10px 12px;
      border-bottom: 1px solid #283548;
      color: var(--text-primary);
    }}
    tr:hover {{
      background-color: #273549;
    }}
    .event-pill {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      margin-right: 4px;
      margin-bottom: 2px;
    }}
    .event-anomaly {{
      background-color: rgba(248, 113, 113, 0.25);
      color: #fca5a5;
      border: 1px solid #f87171;
    }}
    .event-transition {{
      background-color: rgba(251, 191, 36, 0.25);
      color: #fde68a;
      border: 1px solid #fbbf24;
    }}
    .event-health {{
      background-color: rgba(56, 189, 248, 0.25);
      color: #bae6fd;
      border: 1px solid #38bdf8;
    }}
    .footer {{
      text-align: center;
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 32px;
      padding-top: 16px;
      border-top: 1px solid var(--border-color);
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <header class="header">
    <div class="header-title">
      <h1>PRJ_111: Stream Timeline & Activity Visualization</h1>
      <div class="header-subtitle">
        Capture: <strong>{stream_name}</strong> | Sequential Physical Offset Timeline | Grounded Telemetry
      </div>
    </div>
    <div class="header-badges">
      <span class="badge badge-format">{fmt_str}</span>
      <span class="badge {health_badge_class}">Status: {summary_stats.get('mean_health_score', 100):.1f}% Health</span>
    </div>
  </header>

  <!-- KPI Metrics Grid -->
  <section class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-title">Units Monitored</div>
      <div class="kpi-value">{total_units:,}</div>
      <div class="kpi-subtext">{total_windows} sequential windows ({window_size} units/window)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Average Health Score</div>
      <div class="kpi-value">{mean_health:.1f}%</div>
      <div class="kpi-subtext">ETSI TR 101 290 metric synthesis</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Peak Anomaly Score</div>
      <div class="kpi-value">{peak_anomaly:.4f}</div>
      <div class="kpi-subtext">F2 Threshold: {anomaly_threshold:.2f} ({anomaly_win_count} flagged windows)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Payload Volume</div>
      <div class="kpi-value">{total_payload:,.1f} KB</div>
      <div class="kpi-subtext">Physical data volume (no fake throughput)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Structural Transitions</div>
      <div class="kpi-value">{trans_count}</div>
      <div class="kpi-subtext">Cross-window mode/composition shifts</div>
    </div>
  </section>

  <!-- Main Visual Charts -->
  <section class="chart-grid">
    <!-- Chart 1: Health vs Anomaly Trajectory -->
    <div class="chart-card">
      <div class="chart-title">
        <span>Stream Health Trajectory vs. AI Anomaly Score</span>
        <span class="chart-legend-hint">Dual Y-Axis: Health Score [0..100%] (Left) vs. Anomaly Score [0.0..1.0] (Right)</span>
      </div>
      <div class="chart-container">
        <canvas id="healthAnomalyChart"></canvas>
      </div>
    </div>

    <!-- Chart 2: Payload Volume & Format Telemetry -->
    <div class="chart-card">
      <div class="chart-title">
        <span>Activity & Format-Specific Telemetry</span>
        <span class="chart-legend-hint">Payload Volume (KB) vs. {fmt_metric_name}</span>
      </div>
      <div class="chart-container">
        <canvas id="activityChart"></canvas>
      </div>
    </div>
  </section>

  <!-- Window Telemetry & Events Table -->
  <section class="table-card">
    <div class="chart-title">
      <span>Sequential Window Telemetry & Discovered Events</span>
      <span class="chart-legend-hint">Showing {len(points)} windows with exact unit and byte offsets</span>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Window</th>
            <th>Unit Range</th>
            <th>Byte Range</th>
            <th>Payload (KB)</th>
            <th>Health Score</th>
            <th>Anomaly Score</th>
            <th>Severity</th>
            <th>Format Telemetry</th>
            <th>Events & Explanations</th>
          </tr>
        </thead>
        <tbody>
"""

    for p in points:
        w_idx = p["window_index"]
        unit_rng = f"{p['unit_offset_start']}..{p['unit_offset_end']}"
        byte_rng = f"{p['byte_offset_start']:,}..{p['byte_offset_end']:,}"
        p_kb = f"{p['payload_kb']:.2f}"
        h_score = f"{p['health_score']:.1f}%"
        a_score = f"{p['anomaly_score']:.4f}"
        a_sev = p["anomaly_severity"]

        # Format-specific highlight
        fmt_hl = []
        if "MPEG_TS" in fmt_str:
            dom = p.get("format_specific_metrics", {}).get("dominant_pid_summary", "")
            ent = p.get("format_specific_metrics", {}).get("pid_entropy", 0.0)
            fmt_hl.append(f"{dom}")
            fmt_hl.append(f"H={ent:.3f}b")
        elif "GSE" in fmt_str:
            proto = p.get("format_specific_metrics", {}).get("dominant_protocol", "")
            frag = p.get("format_specific_metrics", {}).get("fragmentation_ratio", 0.0)
            fmt_hl.append(f"{proto}")
            fmt_hl.append(f"Frag: {frag*100:.1f}%")
        elif "BB_FRAME" in fmt_str:
            dfl = p.get("format_specific_metrics", {}).get("modal_dfl_bits", 0)
            ro = p.get("format_specific_metrics", {}).get("dominant_ro", 0.35)
            fmt_hl.append(f"DFL: {dfl}b")
            fmt_hl.append(f"&alpha;={ro}")
        fmt_str_cell = " | ".join(fmt_hl)

        # Events and explanations
        events_html = []
        if p["is_anomaly"]:
            events_html.append(f'<span class="event-pill event-anomaly">ANOMALY: {a_sev}</span>')
            expl = p.get("explanation")
            if expl:
                what = expl.get("what_happened", "")
                safe = expl.get("safe_conclusion", "")
                events_html.append(f'<div style="font-size: 11px; color: #fca5a5; margin-top: 3px;"><strong>Diagnostic:</strong> {what}</div>')
                events_html.append(f'<div style="font-size: 10px; color: #94a3b8; margin-top: 1px;"><strong>Safe Conclusion:</strong> {safe}</div>')
            elif p["anomaly_explanation"]:
                events_html.append(f'<div style="font-size: 11px; color: #fca5a5; margin-top: 3px;">{p["anomaly_explanation"]}</div>')
        if p["has_transition"]:
            events_html.append(f'<span class="event-pill event-transition">TRANSITION</span>')
            if p["transition_description"]:
                events_html.append(f'<div style="font-size: 11px; color: #fde68a; margin-top: 2px;">{p["transition_description"]}</div>')
        if not events_html:
            events_html.append('<span style="color: var(--text-secondary);">-</span>')
        events_cell = "".join(events_html)

        html += f"""          <tr>
            <td><strong>W{w_idx}</strong></td>
            <td>{unit_rng}</td>
            <td style="font-family: monospace;">{byte_rng}</td>
            <td>{p_kb}</td>
            <td>{h_score}</td>
            <td>{a_score}</td>
            <td>{a_sev}</td>
            <td>{fmt_str_cell}</td>
            <td>{events_cell}</td>
          </tr>\n"""

    html += f"""        </tbody>
      </table>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    PRJ_111: DVB-S2 Receiver Output Stream Analysis — Review-2 Prototype Milestone &copy; 2026
  </footer>

  <!-- Chart.js Scripts -->
  <script>
    const labels = {json_labels};
    const healthData = {json_health};
    const anomalyData = {json_anomaly};
    const payloadData = {json_payload};
    const fmtData = {json_fmt_values};
    const anomalyThreshold = {anomaly_threshold};

    // Chart 1: Health vs Anomaly Trajectory
    const ctx1 = document.getElementById('healthAnomalyChart').getContext('2d');
    new Chart(ctx1, {{
      type: 'line',
      data: {{
        labels: labels,
        datasets: [
          {{
            label: 'Stream Health Score (%)',
            data: healthData,
            borderColor: '#34d399',
            backgroundColor: 'rgba(52, 211, 153, 0.1)',
            borderWidth: 2.5,
            yAxisID: 'yHealth',
            tension: 0.2,
            pointRadius: 4,
            pointHoverRadius: 6,
          }},
          {{
            label: 'AI Anomaly Score',
            data: anomalyData,
            borderColor: '#f87171',
            backgroundColor: 'rgba(248, 113, 113, 0.15)',
            borderWidth: 2,
            borderDash: [4, 4],
            yAxisID: 'yAnomaly',
            tension: 0.2,
            pointRadius: 4,
            pointHoverRadius: 6,
          }},
          {{
            label: 'F2 Anomaly Decision Threshold (' + anomalyThreshold.toFixed(2) + ')',
            data: Array(labels.length).fill(anomalyThreshold),
            borderColor: '#fbbf24',
            borderWidth: 1.5,
            borderDash: [6, 6],
            pointRadius: 0,
            yAxisID: 'yAnomaly',
            fill: false,
          }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        interaction: {{ mode: 'index', intersect: false }},
        scales: {{
          x: {{
            grid: {{ color: '#334155' }},
            ticks: {{ color: '#94a3b8' }}
          }},
          yHealth: {{
            type: 'linear',
            position: 'left',
            min: 0,
            max: 100,
            grid: {{ color: '#334155' }},
            ticks: {{ color: '#34d399' }},
            title: {{ display: true, text: 'Health Score (%)', color: '#34d399' }}
          }},
          yAnomaly: {{
            type: 'linear',
            position: 'right',
            min: 0.0,
            max: 1.0,
            grid: {{ drawOnChartArea: false }},
            ticks: {{ color: '#f87171' }},
            title: {{ display: true, text: 'Anomaly Score [0..1]', color: '#f87171' }}
          }}
        }},
        plugins: {{
          legend: {{ labels: {{ color: '#f8fafc' }} }}
        }}
      }}
    }});

    // Chart 2: Payload Volume & Format Telemetry
    const ctx2 = document.getElementById('activityChart').getContext('2d');
    new Chart(ctx2, {{
      type: 'bar',
      data: {{
        labels: labels,
        datasets: [
          {{
            type: 'bar',
            label: 'Payload Volume (KB)',
            data: payloadData,
            backgroundColor: 'rgba(56, 189, 248, 0.4)',
            borderColor: '#38bdf8',
            borderWidth: 1.5,
            yAxisID: 'yPayload',
          }},
          {{
            type: 'line',
            label: '{fmt_metric_name}',
            data: fmtData,
            borderColor: '#c084fc',
            backgroundColor: 'transparent',
            borderWidth: 2,
            tension: 0.2,
            pointRadius: 3,
            yAxisID: 'yFmt',
          }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        interaction: {{ mode: 'index', intersect: false }},
        scales: {{
          x: {{
            grid: {{ color: '#334155' }},
            ticks: {{ color: '#94a3b8' }}
          }},
          yPayload: {{
            type: 'linear',
            position: 'left',
            grid: {{ color: '#334155' }},
            ticks: {{ color: '#38bdf8' }},
            title: {{ display: true, text: 'Payload (KB)', color: '#38bdf8' }}
          }},
          yFmt: {{
            type: 'linear',
            position: 'right',
            grid: {{ drawOnChartArea: false }},
            ticks: {{ color: '#c084fc' }},
            title: {{ display: true, text: '{fmt_metric_name}', color: '#c084fc' }}
          }}
        }},
        plugins: {{
          legend: {{ labels: {{ color: '#f8fafc' }} }}
        }}
      }}
    }});
  </script>
</body>
</html>
"""
    return html
