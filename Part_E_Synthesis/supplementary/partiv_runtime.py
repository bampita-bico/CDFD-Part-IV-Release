#!/usr/bin/env python3
"""Release-local diagnostics for CDFD Part IV.

The Part IV archive is a manuscript release, not the runtime package itself.
This module imports the adjacent current CDFD Runtime and writes all generated
artifacts back into this release tree.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

def _find_release_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "Part_A_Earth_Systems").is_dir() and (candidate / "Part_E_Synthesis").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CDFD Part IV release root")


RELEASE_ROOT = _find_release_root()
WORKSPACE_ROOT = RELEASE_ROOT.parent
RUNTIME_ROOT = WORKSPACE_ROOT / "cdfd_runtime"

PART_DIRS = {
    "Part A": "Part_A_Earth_Systems",
    "Part B": "Part_B_Engineered_Systems",
    "Part C": "Part_C_Socioeconomic_Systems",
    "Part D": "Part_D_Domain_Applications",
    "Part E": "Part_E_Synthesis",
    "Part F": "Part_F_Cosmic_and_Subatomic_Systems",
    "Part G": "Part_G_Abstract_and_Cognitive_Systems",
}

OUTPUTS_DIR = RELEASE_ROOT / "Part_E_Synthesis" / "outputs"
FIGURES_DIR = RELEASE_ROOT / "Part_E_Synthesis" / "figures"

if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from engine.physics import step as physics_step  # noqa: E402
from engine.state import State  # noqa: E402
from runtime.diagnostics import clean_json, finite_audit, runtime_provenance  # noqa: E402
from runtime.runner import list_domains, run_domain, runtime_info  # noqa: E402


DOMAIN_SWEEP: list[tuple[str, str, str]] = [
    ("Part A", "climate and atmosphere", "climate"),
    ("Part A", "ocean transport", "oceanography"),
    ("Part A", "hydrological flow", "hydrology"),
    ("Part A", "biodiversity network", "biodiversity"),
    ("Part A", "pollution constraint", "pollution"),
    ("Part B", "energy systems", "energy_systems"),
    ("Part B", "network routing", "networks"),
    ("Part B", "cloud capacity", "cloud_computing"),
    ("Part B", "artificial intelligence", "artificial_intelligence"),
    ("Part C", "macroeconomic flow", "economics"),
    ("Part C", "trade corridors", "trade_routes"),
    ("Part C", "migration pressure", "migration"),
    ("Part C", "education throughput", "education"),
    ("Part C", "governance pressure", "politics"),
    ("Part D", "consciousness", "consciousness"),
    ("Part D", "epidemiology", "epidemiology"),
    ("Part D", "geology", "geology"),
    ("Part D", "quantum mechanics", "quantum_mechanics"),
    ("Part D", "ecology", "ecology"),
    ("Part D", "information flow", "information_theory"),
    ("Part D", "immune response", "immunology"),
    ("Part D", "population genetics", "genetics"),
    ("Part F", "astrophysics", "astrophysics"),
    ("Part F", "nuclear dynamics", "nuclear_physics"),
    ("Part F", "plasma dynamics", "plasma_physics"),
    ("Part G", "language evolution", "linguistics"),
    ("Part G", "science paradigms", "epistemology"),
]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True, allow_nan=False) + "\n")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(clean_json(rows))


def _part_outputs(part: str) -> Path:
    return RELEASE_ROOT / PART_DIRS[part] / "outputs"


def _write_output_readmes() -> None:
    for part, folder in PART_DIRS.items():
        out = RELEASE_ROOT / folder / "outputs"
        out.mkdir(parents=True, exist_ok=True)
        if part == "Part E":
            text = (
                "# Part E Synthesis Outputs\n\n"
                "This folder keeps the release-wide Part IV runtime record: current-runtime provenance, "
                "the universal network-cascade stress test, the full domain adapter sweep, the HTML panel "
                "index, and generated summaries. Figures live in `../figures/`.\n\n"
                "Read these files as model output and bookkeeping for later measurement, not as field evidence.\n"
            )
        else:
            text = (
                f"# {part} Runtime Outputs\n\n"
                "This folder keeps the Part-specific slice of the current-runtime domain adapter sweep. "
                "The release-wide cascade, full sweep, figures, and HTML panel index live under "
                "`Part_E_Synthesis/outputs/` and `Part_E_Synthesis/figures/` from the release root.\n\n"
                "Read these files as model output and bookkeeping for later measurement, not as field evidence.\n"
            )
        (out / "README.md").write_text(text)


def _write_part_sweeps(sweep: dict[str, Any]) -> None:
    for part in PART_DIRS:
        if part == "Part E":
            continue
        rows = [row for row in sweep["rows"] if row.get("part") == part]
        payload = {
            "provenance": sweep.get("provenance"),
            "parameters": sweep.get("parameters"),
            "part": part,
            "rows": rows,
            "finite_audit": finite_audit(rows),
        }
        out = _part_outputs(part)
        _write_json(out / "domain_adapter_sweep.json", payload)
        _write_csv(out / "domain_adapter_sweep.csv", rows)


def run_current_runtime_summary() -> dict[str, Any]:
    info = runtime_info()
    domains = list_domains()
    return {
        "runtime_info": info,
        "domain_list": domains,
        "domain_count": info["payload"].get("domain_count"),
        "language": info["payload"].get("language"),
        "finite_audit": finite_audit({"info": info, "domains": domains}),
    }


def run_domain_adapter_sweep(nx: int = 8, ny: int = 8, steps: int = 8) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for part, label, domain in DOMAIN_SWEEP:
        result = run_domain(domain, {}, nx=nx, ny=ny, steps=steps)
        payload = result.get("payload", {})
        final = payload.get("final", {})
        initial = payload.get("initial", {})
        rows.append(
            {
                "part": part,
                "label": label,
                "domain": domain,
                "status": result.get("status"),
                "regime": payload.get("regime"),
                "initial_mean_psi": initial.get("mean_psi"),
                "final_mean_psi": final.get("mean_psi"),
                "final_mean_phi": final.get("mean_phi"),
                "final_mean_C": final.get("mean_C"),
                "errors": "; ".join(result.get("errors", [])),
            }
        )
    return {
        "provenance": runtime_provenance("partiv domain adapter sweep"),
        "parameters": {"nx": nx, "ny": ny, "steps": steps},
        "rows": rows,
        "finite_audit": finite_audit(rows),
    }


def run_universal_network_cascade(
    nx: int = 32,
    ny: int = 32,
    steps: int = 400,
    dt: float = 0.02,
    hub_drive: float = 4.0,
    beta: float = 0.015,
    threshold: float = 1.5,
) -> dict[str, Any]:
    """Run the current-engine cascade diagnostic used by the Part IV papers."""
    state = State(nx, ny)
    state.phi[:] = 0.8
    state.C[:] = 1.0
    state.S[:] = 1.0
    state.Ms[:] = 1.0
    state.alpha[:] = 0.08
    state.beta[:] = beta
    state.gamma[:] = 0.02
    hub = (nx // 2, ny // 2)
    locked = np.zeros((nx, ny), dtype=bool)

    series: dict[str, list[Any]] = {
        "time": [],
        "phi_hub": [],
        "C_hub": [],
        "S_hub": [],
        "M_s_hub": [],
        "psi_hub": [],
        "psi_system_mean": [],
        "psi_system_max": [],
        "overloaded_nodes": [],
        "memory_locked_nodes": [],
    }

    for index in range(steps):
        t = index * dt
        source = np.zeros((nx, ny), dtype=float)
        source[hub] = hub_drive * (1.0 + 0.08 * t)
        source[hub[0] - 1 : hub[0] + 2, hub[1] - 1 : hub[1] + 2] += hub_drive * 0.08
        physics_step(state, dt=dt, J_in=source)
        psi = state.update_psi()
        overloaded = psi > threshold
        locked |= (state.Ms > 1.05) | overloaded

        if index % 10 == 0 or index == steps - 1:
            series["time"].append(float(t))
            series["phi_hub"].append(float(state.phi[hub]))
            series["C_hub"].append(float(state.C[hub]))
            series["S_hub"].append(float(state.S[hub]))
            series["M_s_hub"].append(float(state.Ms[hub]))
            series["psi_hub"].append(float(psi[hub]))
            series["psi_system_mean"].append(float(np.mean(psi)))
            series["psi_system_max"].append(float(np.max(psi)))
            series["overloaded_nodes"].append(int(np.sum(overloaded)))
            series["memory_locked_nodes"].append(int(np.sum(locked)))

    final = {
        "hub_phi": float(state.phi[hub]),
        "hub_C": float(state.C[hub]),
        "hub_S": float(state.S[hub]),
        "hub_M_s": float(state.Ms[hub]),
        "hub_psi_s": float(state.psi_s[hub]),
        "mean_psi_s": float(np.mean(state.psi_s)),
        "max_psi_s": float(np.max(state.psi_s)),
        "overloaded_nodes": int(np.sum(state.psi_s > threshold)),
        "memory_locked_nodes": int(np.sum(locked)),
        "regime": state.regime(),
    }
    summary = {
        "peak_hub_psi_s": max(series["psi_hub"]),
        "peak_network_psi_s": max(series["psi_system_max"]),
        "max_overloaded_nodes": max(series["overloaded_nodes"]),
        "max_memory_locked_nodes": max(series["memory_locked_nodes"]),
        "final": final,
    }
    payload = {
        "provenance": runtime_provenance("partiv universal network cascade"),
        "status": "candidate_simulation_result",
        "interpretation": (
            "A localized high-drive hub creates an overload and memory-locking "
            "stress test in the current CDFD Runtime. This is an internal model "
            "diagnostic, not empirical validation."
        ),
        "parameters": {
            "nx": nx,
            "ny": ny,
            "steps": steps,
            "dt": dt,
            "hub_drive": hub_drive,
            "beta": beta,
            "threshold": threshold,
            "engine_update": "engine.physics.step RK4 with S and M_s dynamics",
        },
        "series": series,
        "summary": summary,
    }
    payload["finite_audit"] = finite_audit(payload)
    return payload


def plot_outputs(cascade: dict[str, Any], sweep: dict[str, Any]) -> list[str]:
    written: list[str] = []
    try:
        os.environ.setdefault("MPLCONFIGDIR", "/tmp/cdfd_partiv_matplotlib")
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - optional plotting path
        return [f"plotting unavailable: {exc}"]

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    series = cascade["series"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("white")
    axes[0].plot(series["time"], series["phi_hub"], lw=2.5, color="#8B1E3F")
    axes[0].set_title("A | Hub drive")
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("Phi")
    axes[0].grid(alpha=0.3)

    axes[1].plot(series["time"], series["psi_hub"], lw=2.5, color="#1F5E8C")
    axes[1].axhline(cascade["parameters"]["threshold"], ls="--", color="#B00020", lw=1.8)
    axes[1].set_title("B | Hub operating ratio")
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("Psi_s")
    axes[1].grid(alpha=0.3)

    axes[2].plot(series["time"], series["overloaded_nodes"], lw=2.5, color="#2E7D32", label="overload")
    axes[2].plot(series["time"], series["memory_locked_nodes"], lw=2.5, color="#6A4C93", label="memory lock")
    axes[2].set_title("C | Network cascade")
    axes[2].set_xlabel("time")
    axes[2].set_ylabel("node count")
    axes[2].legend()
    axes[2].grid(alpha=0.3)

    fig.suptitle("Part IV current-runtime cascade diagnostic", fontsize=14, fontweight="bold")
    fig.tight_layout()
    cascade_path = FIGURES_DIR / "universal_cascade.png"
    fig.savefig(cascade_path, dpi=220)
    plt.close(fig)
    written.append(str(cascade_path.relative_to(RELEASE_ROOT)))

    rows = [row for row in sweep["rows"] if row["status"] == "ok" and row["final_mean_psi"] is not None]
    rows = sorted(rows, key=lambda item: float(item["final_mean_psi"]), reverse=True)
    fig, ax = plt.subplots(figsize=(12, 7))
    labels = [row["domain"] for row in rows]
    values = [float(row["final_mean_psi"]) for row in rows]
    colors = ["#8B1E3F" if value > 1.2 else "#2E7D32" if value >= 0.8 else "#4A6FA5" for value in values]
    ax.barh(labels, values, color=colors)
    ax.axvspan(0.8, 1.2, color="#EEEEEE", alpha=0.8, label="balanced band")
    ax.set_xlabel("final mean Psi_s")
    ax.set_title("Current-runtime domain adapter sweep")
    ax.invert_yaxis()
    ax.legend()
    fig.tight_layout()
    sweep_path = FIGURES_DIR / "domain_sweep_psi.png"
    fig.savefig(sweep_path, dpi=220)
    plt.close(fig)
    written.append(str(sweep_path.relative_to(RELEASE_ROOT)))
    return written


def write_summary_markdown(runtime: dict[str, Any], cascade: dict[str, Any], sweep: dict[str, Any], figures: list[str]) -> None:
    rows = [row for row in sweep["rows"] if row["status"] == "ok" and row["final_mean_psi"] is not None]
    overload = [row for row in rows if float(row["final_mean_psi"]) > 1.2]
    balanced = [row for row in rows if 0.8 <= float(row["final_mean_psi"]) <= 1.2]
    constrained = [row for row in rows if float(row["final_mean_psi"]) < 0.8]
    top = sorted(overload, key=lambda row: float(row["final_mean_psi"]), reverse=True)[:8]
    final = cascade["summary"]["final"]

    lines = [
        "# Part IV Runtime Discovery Summary",
        "",
        "This file is generated by `Part_E_Synthesis/supplementary/run_partiv_discovery.py`.",
        "The numbers below are runtime output and a record of the May 2026 model pass.",
        "",
        "## Runtime Surface",
        "",
        f"- Runtime: {runtime['runtime_info']['payload'].get('name')}",
        f"- Language: {runtime.get('language')}",
        f"- Registered domains: {runtime.get('domain_count')}",
        "- Runtime boundary: application/VOS layer kept outside the numerical engine.",
        "",
        "## Universal Network Cascade",
        "",
        f"- Final hub `Psi_s`: {final['hub_psi_s']:.6g}",
        f"- Peak network `Psi_s`: {cascade['summary']['peak_network_psi_s']:.6g}",
        f"- Final overloaded nodes (`Psi_s > {cascade['parameters']['threshold']}`): {final['overloaded_nodes']}",
        f"- Maximum memory-locked nodes: {cascade['summary']['max_memory_locked_nodes']}",
        f"- Finite-value audit: {cascade['finite_audit']['all_finite']}",
        "",
        "Interpretation: with these parameters, the current runtime produces an overload-and-memory-locking stress test when a localized hub drive is coupled to slow constraint relaxation.",
        "",
        "## Domain Adapter Sweep",
        "",
        f"- Domains run: {len(rows)}",
        f"- Overload regime: {len(overload)}",
        f"- Balanced regime: {len(balanced)}",
        f"- Constrained regime: {len(constrained)}",
        "",
        "| Domain | Part | Regime | Final mean Psi_s |",
        "|---|---|---:|---:|",
    ]
    for row in top:
        lines.append(f"| `{row['domain']}` | {row['part']} | {row['regime']} | {float(row['final_mean_psi']):.6g} |")
    lines.extend(
        [
            "",
            "## Figures",
            "",
        ]
    )
    lines.extend([f"- `{item}`" for item in figures if not item.startswith("plotting unavailable")])
    if any(item.startswith("plotting unavailable") for item in figures):
        lines.append(f"- Plot warning: {figures[-1]}")
    lines.append("")
    (OUTPUTS_DIR / "partiv_discovery_summary.md").write_text("\n".join(lines))


def run_release_diagnostics() -> dict[str, Any]:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    _write_output_readmes()
    runtime = run_current_runtime_summary()
    sweep = run_domain_adapter_sweep()
    cascade = run_universal_network_cascade()
    figures = plot_outputs(cascade, sweep)

    _write_json(OUTPUTS_DIR / "runtime_info.json", runtime)
    _write_json(OUTPUTS_DIR / "domain_adapter_sweep.json", sweep)
    _write_csv(OUTPUTS_DIR / "domain_adapter_sweep.csv", sweep["rows"])
    _write_json(OUTPUTS_DIR / "universal_collapse.json", cascade)
    _write_part_sweeps(sweep)
    write_summary_markdown(runtime, cascade, sweep, figures)
    return {
        "runtime": runtime,
        "domain_sweep": sweep,
        "cascade": cascade,
        "figures": figures,
    }


if __name__ == "__main__":
    result = run_release_diagnostics()
    print(
        json.dumps(
            {
                "status": "ok",
                "domain_count": result["runtime"].get("domain_count"),
                "cascade_final_hub_psi_s": result["cascade"]["summary"]["final"]["hub_psi_s"],
                "figures": result["figures"],
            },
            indent=2,
            sort_keys=True,
        )
    )
