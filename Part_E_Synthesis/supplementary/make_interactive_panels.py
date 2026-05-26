#!/usr/bin/env python3
"""Build a small release-local HTML index for Part IV generated artifacts."""
from __future__ import annotations

import html
import json
from pathlib import Path

def _find_release_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "Part_A_Earth_Systems").is_dir() and (candidate / "Part_E_Synthesis").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CDFD Part IV release root")


ROOT = _find_release_root()
OUTPUTS = ROOT / "Part_E_Synthesis" / "outputs"
FIGURES = ROOT / "Part_E_Synthesis" / "figures"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def main() -> int:
    OUTPUTS.mkdir(exist_ok=True)
    cascade = _load_json(OUTPUTS / "universal_collapse.json")
    sweep = _load_json(OUTPUTS / "domain_adapter_sweep.json")
    final = cascade.get("summary", {}).get("final", {})
    rows = sweep.get("rows", [])
    top_rows = sorted(
        [row for row in rows if row.get("status") == "ok" and row.get("final_mean_psi") is not None],
        key=lambda row: float(row["final_mean_psi"]),
        reverse=True,
    )[:12]

    table = "\n".join(
        "<tr>"
        f"<td>{html.escape(row['part'])}</td>"
        f"<td>{html.escape(row['domain'])}</td>"
        f"<td>{html.escape(str(row['regime']))}</td>"
        f"<td>{float(row['final_mean_psi']):.6g}</td>"
        "</tr>"
        for row in top_rows
    )
    figure_html = []
    for fig in ["universal_cascade.png", "domain_sweep_psi.png"]:
        if (FIGURES / fig).exists():
            figure_html.append(f'<figure><img src="../figures/{fig}" alt="{fig}"><figcaption>{fig}</figcaption></figure>')

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CDFD Part IV Runtime Panels</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 32px; color: #17202a; }}
    h1, h2 {{ color: #17324d; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }}
    img {{ max-width: 100%; border: 1px solid #d8dee9; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ padding: 8px 10px; border-bottom: 1px solid #d8dee9; text-align: left; }}
    th {{ background: #eef3f8; }}
    code {{ background: #eef3f8; padding: 2px 4px; }}
  </style>
</head>
<body>
  <h1>CDFD Part IV Runtime Panels</h1>
  <p>These files are model outputs from the release diagnostics. They document runtime behavior and point to measurements that can test the mapping.</p>
  <h2>Universal Network Cascade</h2>
  <p>Final hub <code>Psi_s</code>: {final.get('hub_psi_s', 'not generated')} |
     overloaded nodes: {final.get('overloaded_nodes', 'not generated')} |
     memory-locked nodes: {final.get('memory_locked_nodes', 'not generated')}</p>
  <div class="grid">
    {''.join(figure_html)}
  </div>
  <h2>Top Domain Adapter Stress Responses</h2>
  <table>
    <thead><tr><th>Part</th><th>Domain</th><th>Regime</th><th>Final mean Psi_s</th></tr></thead>
    <tbody>{table}</tbody>
  </table>
  <h2>Files</h2>
  <ul>
    <li><a href="partiv_discovery_summary.md">partiv_discovery_summary.md</a></li>
    <li><a href="universal_collapse.json">universal_collapse.json</a></li>
    <li><a href="domain_adapter_sweep.csv">domain_adapter_sweep.csv</a></li>
    <li><a href="runtime_info.json">runtime_info.json</a></li>
  </ul>
</body>
</html>
"""
    (OUTPUTS / "interactive_index.html").write_text(html_text)
    print(f"wrote {OUTPUTS / 'interactive_index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
