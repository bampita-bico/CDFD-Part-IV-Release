#!/usr/bin/env python3
"""Final mechanical cleanup for the Part IV manuscript release."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

def _find_release_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "Part_A_Earth_Systems").is_dir() and (candidate / "Part_E_Synthesis").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CDFD Part IV release root")


RELEASE_ROOT = _find_release_root()

AUTHOR = (
    r"\author{Steve Bico Mujjabi, MD\\"
    "\n"
    r"\small Independent Researcher\\"
    "\n"
    r"\small ORCID: 0009-0001-0556-5516}"
)

PART_LETTERS = {
    "Part_A_Earth_Systems": "A",
    "Part_B_Engineered_Systems": "B",
    "Part_C_Socioeconomic_Systems": "C",
    "Part_D_Domain_Applications": "D",
    "Part_E_Synthesis": "E",
    "Part_F_Cosmic_and_Subatomic_Systems": "F",
    "Part_G_Abstract_and_Cognitive_Systems": "G",
}

DROP_TITLE_TOKENS = {"Eng", "Soc", "Dom", "Abs", "Cosmos", "Physics"}
TITLE_ACRONYMS = {
    "Afl": "AFL",
    "Ai": "AI",
    "Cdfd": "CDFD",
}

TITLE_OVERRIDES = {
    "08_Eng_Cloud": "Cloud Systems",
    "10_Eng_Autonomous": "Autonomous Systems",
    "12_Eng_Synthesis": "Engineering Synthesis",
    "01_Soc_Economics_Opportunity": "Economics and Opportunity",
    "09_Soc_Crises": "Socioeconomic Crises",
    "02_Dom_Pandemic": "Pandemic Dynamics",
    "06_Dom_Quantum_Macro": "Macroscopic Quantum Systems",
    "08_Dom_Ecology_Trophic": "Ecology and Trophic Systems",
}

OVERCLAIM_ABSTRACT = (
    "In this paper, we completely discard trial-and-error empiricism and strictly apply "
    "the formal mathematical structure of the Mujjabi Laws to universally predict systemic behavior. "
    "We mathematically mandate that systemic failure across this domain is not a stochastic accident, "
    "but an inevitable topological collapse of the adaptive constraint tensor $C$. Using the "
    "Constraint-Driven Flux Dynamics (CDFD) engine, we move beyond descriptive science to exact "
    "mathematical prognostication of network cascades and catastrophic memory locks."
)

DISCIPLINED_ABSTRACT = (
    "This paper asks whether Constraint-Driven Flux Dynamics (CDFD) and Adaptive "
    "Flux Limitation (AFL) can give the named system a sharper audit language. "
    "The working variables are driving flux $\\Phi$, constraint $C$, surface "
    "responsiveness $S$, and structural memory $M_s$. The useful question is "
    "plain: what can be measured, what would count as overload, and what result "
    "would make the mapping fail?"
)

REAL_BIB = r"""
@misc{MujjabiPartI2026,
  author = {Mujjabi, Steve Bico},
  title = {CDFD Part I: Fundamental Physics - Constraint-Driven Field Theory and Flux Dynamics},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.20250821},
  url = {https://doi.org/10.5281/zenodo.20250821}
}

@misc{MujjabiPartII2026,
  author = {Mujjabi, Steve Bico},
  title = {CDFD Part II: Origins of Life and Tri-Regime Bioenergetics - Constraint-Driven Flux Dynamics},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.20264779},
  url = {https://doi.org/10.5281/zenodo.20264779}
}

@misc{MujjabiPartIII2026,
  author = {Mujjabi, Steve Bico},
  title = {CDFD Part III: Adaptive Flux Limitation Biology and Medicine - Constraint-Driven Flux Dynamics},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.20344695},
  url = {https://doi.org/10.5281/zenodo.20344695}
}

@misc{CDFDRuntime2026,
  author = {Mujjabi, Steve Bico},
  title = {CDFD Runtime: Constraint-Driven Flux Dynamics and CDFL Execution Engine},
  year = {2026},
  publisher = {Zenodo},
  version = {1.0.1},
  doi = {10.5281/zenodo.20343160},
  url = {https://doi.org/10.5281/zenodo.20343160}
}

@article{BarabasiAlbert1999,
  author = {Barabasi, Albert-Laszlo and Albert, Reka},
  title = {Emergence of Scaling in Random Networks},
  journal = {Science},
  volume = {286},
  number = {5439},
  pages = {509--512},
  year = {1999},
  doi = {10.1126/science.286.5439.509}
}

@article{WattsStrogatz1998,
  author = {Watts, Duncan J. and Strogatz, Steven H.},
  title = {Collective Dynamics of Small-World Networks},
  journal = {Nature},
  volume = {393},
  pages = {440--442},
  year = {1998},
  doi = {10.1038/30918}
}

@article{Holling1973,
  author = {Holling, C. S.},
  title = {Resilience and Stability of Ecological Systems},
  journal = {Annual Review of Ecology and Systematics},
  volume = {4},
  pages = {1--23},
  year = {1973},
  doi = {10.1146/annurev.es.04.110173.000245}
}

@article{Turing1952,
  author = {Turing, A. M.},
  title = {The Chemical Basis of Morphogenesis},
  journal = {Philosophical Transactions of the Royal Society of London. Series B},
  volume = {237},
  number = {641},
  pages = {37--72},
  year = {1952},
  doi = {10.1098/rstb.1952.0012}
}

@article{Shannon1948,
  author = {Shannon, Claude E.},
  title = {A Mathematical Theory of Communication},
  journal = {Bell System Technical Journal},
  volume = {27},
  number = {3},
  pages = {379--423},
  year = {1948},
  doi = {10.1002/j.1538-7305.1948.tb01338.x}
}

@article{BakTangWiesenfeld1987,
  author = {Bak, Per and Tang, Chao and Wiesenfeld, Kurt},
  title = {Self-Organized Criticality: An Explanation of the 1/f Noise},
  journal = {Physical Review Letters},
  volume = {59},
  number = {4},
  pages = {381--384},
  year = {1987},
  doi = {10.1103/PhysRevLett.59.381}
}

@book{Newman2010,
  author = {Newman, Mark},
  title = {Networks: An Introduction},
  publisher = {Oxford University Press},
  year = {2010},
  isbn = {9780199206650}
}

@book{Ostrom1990,
  author = {Ostrom, Elinor},
  title = {Governing the Commons: The Evolution of Institutions for Collective Action},
  publisher = {Cambridge University Press},
  year = {1990},
  isbn = {9780521405997}
}
""".strip() + "\n"


def _load_cascade() -> dict[str, Any]:
    path = RELEASE_ROOT / "Part_E_Synthesis" / "outputs" / "universal_collapse.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _runtime_evidence_paragraph() -> str:
    cascade = _load_cascade()
    summary = cascade.get("summary", {})
    final = summary.get("final", {})
    if not final:
        return (
            r"\subsection{Current Runtime Diagnostic: Universal Network Cascade}"
            "\n"
            r"The diagnostic script \texttt{Part\_E\_Synthesis/supplementary/run\_partiv\_discovery.py} "
            r"keeps the Part IV papers tied to the current CDFD Runtime \cite{CDFDRuntime2026}. "
            r"I use it as a finite-value stress test and as a record of what the present runtime actually produces."
        )
    threshold = cascade.get("parameters", {}).get("threshold", 1.5)
    return (
        r"\subsection{Current Runtime Diagnostic: Universal Network Cascade}"
        "\n"
        r"The diagnostic script \texttt{Part\_E\_Synthesis/supplementary/run\_partiv\_discovery.py} keeps this "
        r"paper tied to the current CDFD Runtime \cite{CDFDRuntime2026}, including RK4 field updates, "
        r"surface dynamics, structural-memory diffusion, and a finite-value audit. In the May 2026 "
        f"run, the localized hub-drive stress test ended with hub $\\Psi_s={final['hub_psi_s']:.3g}$, "
        f"peak network $\\Psi_s={summary['peak_network_psi_s']:.3g}$, "
        f"{final['overloaded_nodes']} nodes above $\\Psi_s>{threshold}$, and "
        f"{summary['max_memory_locked_nodes']} maximum memory-locked nodes. "
        r"I treat those numbers as a runtime sanity check and as a target for later domain measurement, "
        r"not as a substitute for field data."
    )


def _replace_author(text: str) -> str:
    return re.sub(r"\\author\{.*?\}", lambda _match: AUTHOR, text, count=1, flags=re.S)


def _paper_label_and_title(path: Path) -> tuple[str, str] | None:
    relative = path.relative_to(RELEASE_ROOT)
    if len(relative.parts) < 3:
        return None
    part_letter = PART_LETTERS.get(relative.parts[0])
    if part_letter is None:
        return None
    stem_parts = path.stem.split("_")
    if not stem_parts or not stem_parts[0].isdigit():
        return None
    number = int(stem_parts[0])
    if path.stem in TITLE_OVERRIDES:
        return f"{part_letter}-{number:02d}", TITLE_OVERRIDES[path.stem]
    words = stem_parts[1:]
    if words and words[0] in DROP_TITLE_TOKENS:
        words = words[1:]
    title_words = [TITLE_ACRONYMS.get(word, word) for word in words]
    title = " ".join(title_words)
    return f"{part_letter}-{number:02d}", title


def _replace_title(path: Path, text: str) -> str:
    paper = _paper_label_and_title(path)
    if paper is None:
        return text
    label, title = paper
    new_title = (
        r"\title{\textbf{"
        f"Paper {label}: {title}:"
        r"\\ A Constraint-Driven Flux Dynamics (CDFD) Perspective}}"
    )
    return re.sub(
        "(?:\\\\title|\title)\\{.*?\\}\\s*(?=\\\\author)",
        lambda _match: new_title + "\n",
        text,
        count=1,
        flags=re.S,
    )


def _replace_stale_numerical_blocks(text: str, evidence: str) -> str:
    text = re.sub(
        r"\\subsection\{Current Runtime Diagnostic: Universal Network Cascade\}\s*The release-local script "
        r"\\texttt\{Part\\_E\\_Synthesis/supplementary/run\\_partiv\\_discovery\.py\} reruns this diagnostic.*?"
        r"empirical claim\.",
        lambda _match: evidence,
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\\subsection\{Numerical Verification: Universal Network Collapse\}\s*.*?(?=\n\\section\{Conclusion\}|\n\\section\*|\\bibliographystyle|\Z)",
        lambda _match: evidence + "\n\n",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\\section\{Numerical Verification\}\s*Run .*?\\textbf\{Status: Derived\}\s*",
        lambda _match: evidence + "\n\n",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\\section\{Reproducibility Note\}\s*\\begin\{itemize\}.*?\\end\{itemize\}\s*\\textbf\{Status: Derived\}\s*",
        lambda _match: (
            r"\section{Reproducibility Note}"
            "\n"
            r"Regenerate the cited discovery outputs from the release root with "
            r"\texttt{/home/bampita/Projects/CDFD/.venv/bin/python Part\_E\_Synthesis/supplementary/run\_partiv\_discovery.py}. "
            r"The command writes Part-specific domain sweeps under each Part's \texttt{outputs/} folder and release-wide synthesis artifacts under \texttt{Part\_E\_Synthesis/outputs/} and \texttt{Part\_E\_Synthesis/figures/}."
            "\n\n"
        ),
        text,
        flags=re.S,
    )
    return text


def _remove_orphan_back_matter_stubs(text: str) -> str:
    stubs = [
        r"\n\\clearpage\s*\n\\section\*\{Ontology Networks and Semantic Throughput:.*?\}\s*(?=\n\\bibliographystyle)",
        r"\n\\clearpage\s*\n\\section\*\{From Quantum Vacuum to Society:.*?\}\s*(?=\n\\bibliographystyle)",
        r"\n\\newpage\s*\n\\part\{Atmospheric Flux and Climate Regulation:.*?\}\s*\\vspace\{0\.5em\}.*?\\vspace\{0\.75em\}\s*(?=\n\\bibliographystyle)",
    ]
    for pattern in stubs:
        text = re.sub(pattern, "\n", text, flags=re.S)
    return text


NOTATION_NOTE = (
    r"\paragraph{Notation.} In Part IV, $C$ names the active constraint or "
    r"capacity burden in the system being discussed. $\Phi$ is the driving "
    r"flow, $S$ is the surface response, and $M_s$ is retained structural "
    r"memory. $\Lambda$ appears only where the Part II Life Number is being "
    r"referenced \cite{MujjabiPartII2026}. Other Greek symbols are local "
    r"coefficients whose meaning is set by the equation in which they appear."
)

OLD_NOTATION_PATTERNS = [
    (
        r"\\textbf\{Crucial Taxonomic Clarification:\}.*?subscripts restrict "
        r"coefficients to the named pathway, tissue, domain, or experiment\."
    ),
    (
        r"\\textbf\{Crucial Taxonomic Clarification:\} Across all domains of the Universal AFL Synthesis, "
        r"the constraint tensor is denoted strictly as \$C\.\$ The variable \$\\Lambda\$ is strictly reserved "
        r"for the \\textbf\{Life Number \(Emergence Number\)\}\. Greek-symbol convention: unless a manuscript "
        r"states a tighter equation-local meaning, Greek symbols are local CDFD variables or coefficients, not "
        r"universal constants\. \$\\Phi\$ is driving flux, \$\\Psi_s\$ is the adaptive operating ratio, "
        r"\$\\Lambda\$ is the Life Number where used, \$\\alpha\$ is accumulation or reinforcement, "
        r"\$\\beta\$ is relaxation or decay, \$\\gamma\$ is diffusion or coupling, and subscripts restrict "
        r"coefficients to the named pathway, tissue, domain, or experiment\."
    ),
    (
        r"\\textbf\{Crucial Taxonomic Clarification:\} Across all domains of the Universal AFL Synthesis, "
        r"the constraint tensor is denoted strictly as \$C\.\$ The variable \$\\Lambda\$ is strictly reserved "
        r"for the \\textbf\{Life Number \(Emergence Number\)\}\."
    ),
]

SERIES_CONTEXT = (
    r"\section{Series Context}"
    "\n\n"
    r"Part I sets the flow--constraint language used here \cite{MujjabiPartI2026}. "
    r"Part II develops the Life Number and the origins-of-life use of the same notation "
    r"\cite{MujjabiPartII2026}. Part III applies AFL to biology and medicine "
    r"\cite{MujjabiPartIII2026}. Part IV is the cross-domain stress test: it asks where "
    r"the notation clarifies measurement, and where it becomes only a metaphor."
    "\n\n"
)

MEASUREMENT_LAYER = (
    r"\section{Measurement Layer}"
    "\n\n"
    r"The first job in any domain is to choose proxies before drawing conclusions. "
    r"$\Phi$ may be a rate of material, energy, information, capital, or signal flow. "
    r"$C$ is the bottleneck that slows or redirects that flow. $S$ measures the system's "
    r"ability to reconfigure under stress, and $M_s$ records the past load that still "
    r"changes present behavior. A useful application gives those four terms observable "
    r"definitions, a time scale, and a failure condition. If a standard domain model "
    r"explains the same data more cleanly, the CDFD/AFL mapping should give way."
    "\n\n"
)


def _replace_notation_note(text: str) -> str:
    for pattern in OLD_NOTATION_PATTERNS:
        text = re.sub(pattern, lambda _match: NOTATION_NOTE, text, flags=re.S)
    return text


def _insert_series_context(text: str) -> str:
    if r"\section{Series Context}" in text:
        return text
    marker = r"\section{Introduction}"
    index = text.find(marker)
    if index == -1:
        return text
    return text[:index] + SERIES_CONTEXT + text[index:]


def _insert_measurement_layer(text: str) -> str:
    if r"\section{Measurement Layer}" in text:
        return text
    markers = [
        r"\section{Current Runtime Diagnostic}",
        r"\subsection{Current Runtime Diagnostic: Universal Network Cascade}",
    ]
    positions = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if not positions:
        return text
    index = min(positions)
    return text[:index] + MEASUREMENT_LAYER + text[index:]


def _clean_text(path: Path, text: str, evidence: str) -> str:
    text = _replace_title(path, text)
    text = text.replace("\texttt", r"\texttt")
    text = text.replace("–", "--").replace("’", "'").replace("→", r"$\to$").replace("è", "e")
    text = text.replace("CDFT", "CDFD")
    text = text.replace("Constraint-Driven Flux Theory", "Constraint-Driven Flux Dynamics")
    text = text.replace("AFL\\_rewrite\\_template\\_and\\_rubric.md", "CLAIM\\_STATUS.md")
    text = text.replace("notebooks/supplementary", "supplementary/supplementary")
    text = text.replace(r"$\csname Lambda\endcsname$", r"$\Lambda$")
    text = re.sub(r"\\date\{.*?\}", r"\\date{May 2026}", text, count=1, flags=re.S)
    text = _replace_author(text)
    text = text.replace(OVERCLAIM_ABSTRACT, DISCIPLINED_ABSTRACT)
    text = text.replace(
        "This paper treats the named domain as a Constraint-Driven Flux Dynamics (CDFD) and Adaptive Flux Limitation (AFL) modelling hypothesis. It maps driving flux $\\Phi$, constraint $C$, surface responsiveness $S$, and structural memory $M_s$ onto a domain-specific system, then states what would have to be measured for the mapping to become stronger than analogy. The release-local runtime outputs are internal consistency checks and candidate discovery targets, not empirical proof.",
        DISCIPLINED_ABSTRACT,
    )
    text = _replace_notation_note(text)
    text = text.replace(
        "\n\\textbf{Crucial Taxonomic Clarification:} Across all domains of the Universal AFL Synthesis, the constraint tensor is denoted strictly as $C$. The variable $\\Lambda$ is used for the \\textbf{Life Number (Emergence Number)}.\n",
        "\n",
    )
    text = _insert_series_context(text)
    text = _insert_measurement_layer(text)
    text = text.replace(
        "If $\\Lambda < 1$ systems never sustain autocatalysis and $\\Lambda > 1$ systems always do, the AFL OOL claim is validated.",
        "If $\\Lambda < 1$ systems fail to sustain autocatalysis while $\\Lambda > 1$ systems do so reproducibly, the AFL OOL claim gains support.",
    )
    text = text.replace("mathematically dictates that", "proposes that")
    text = text.replace("mandates system saturation", "can drive system saturation")
    text = text.replace("defines irreversible systemic collapse", "frames persistent systemic collapse")
    text = text.replace("This is the exact mathematical root of", "This is the proposed CDFD mechanism behind")
    text = text.replace("mathematically guarantees", "predicts")
    text = text.replace("As proven in", "As modeled in")
    text = text.replace("we prove that", "we model the hypothesis that")
    text = text.replace("guarantees topological elasticity", "may support topological elasticity")
    text = text.replace("physically inevitable", "a candidate failure mode")
    text = text.replace("entirely predictable", "represented as")
    text = text.replace("mathematically proves", "models the condition that")
    text = text.replace("mathematically prove", "model the condition that")
    text = text.replace("CDFD proves", "CDFD suggests")
    text = text.replace("exact same mathematical equations", "same candidate mathematical structure")
    text = text.replace("inevitably crash", "enter an overload regime")
    text = text.replace("mathematically mandated", "model-predicted")
    text = text.replace("mathematical prognostication", "testable model diagnostics")
    text = text.replace("not a stochastic accident, but an inevitable", "not only a stochastic accident; it may reflect")
    text = text.replace("We demonstrate that", "We model the hypothesis that")
    text = text.replace("we demonstrate that", "we model the hypothesis that")
    text = text.replace("By applying CDFD, we establish that", "By applying CDFD, we frame the hypothesis that")
    text = text.replace("Through CDFD, we establish that", "Through CDFD, we frame the hypothesis that")
    text = text.replace("we establish that", "we frame the hypothesis that")
    text = text.replace("mathematically guaranteed outcome", "model-predicted failure mode")
    text = text.replace("mathematically guarantee localized systemic collapse", "increase the risk of localized systemic collapse")
    text = text.replace("mathematically guarantees", "predicts")
    text = text.replace("mathematically verify", "model")
    text = text.replace("mathematically condemned to", "at risk of")
    text = text.replace("mathematically inevitable", "model-predicted")
    text = text.replace("mathematically collapse", "enter an overload regime")
    text = text.replace("absolute and irreversible", "a severe candidate failure mode")
    text = text.replace("strict mathematical physics", "constraint-based modelling")
    text = text.replace("exact thermodynamic cost", "candidate thermodynamic cost")
    text = text.replace("Master Law", "Master Modelling Relation")
    text = text.replace(r"\section*{CDFD/AFL Domain: ", r"\section*{")
    text = text.replace(
        "the AFL framework proves that echo chambers and viral cascades are inevitable thermodynamic consequences of engagement optimization",
        "the AFL framework frames echo chambers and viral cascades as candidate consequences of engagement optimization",
    )
    text = text.replace(
        "The release-local script \\texttt{Part\\_E\\_Synthesis/supplementary/run\\_partiv\\_discovery.py}\nproduces a domain adapter sweep, a universal cascade stress test, two figures,\nand a generated Markdown summary. The run checks finite-value behavior and\ncandidate overload/memory-locking dynamics in the current CDFD Runtime. It is\nnot empirical validation of Part IV's domain claims.",
        "The diagnostic script \\texttt{Part\\_E\\_Synthesis/supplementary/run\\_partiv\\_discovery.py}\nproduces a domain adapter sweep, a universal cascade stress test, two figures,\nand a generated Markdown summary. The run records finite-value behavior and\noverload/memory-locking dynamics in the current CDFD Runtime. It is a model\nrecord for later measurement, not a claim that the domains have already been\nvalidated.",
    )
    text = text.replace(
        "The release-local script \\texttt{Part\\_E\\_Synthesis/supplementary/run\\_partiv\\_discovery.py}\nincludes selected Earth-system adapter rows for climate and atmosphere, ocean\ntransport, hydrological flow, biodiversity, and pollution. The accompanying\nnetwork-cascade diagnostic checks finite-value behavior in a toy overload and\nmemory-locking stress test. These are model diagnostics. They do not validate\nany Earth-system claim by themselves.",
        "The diagnostic script \\texttt{Part\\_E\\_Synthesis/supplementary/run\\_partiv\\_discovery.py}\nincludes selected Earth-system adapter rows for climate and atmosphere, ocean\ntransport, hydrological flow, biodiversity, and pollution. The accompanying\nnetwork-cascade diagnostic checks finite-value behavior in an overload and\nmemory-locking stress test. I use those rows as a runtime audit, not as a\nreplacement for Earth-system data.",
    )
    text = text.replace(
        "The release-local script \\texttt{Part\\_E\\_Synthesis/supplementary/run\\_partiv\\_discovery.py}\ndoes not simulate every Part B system. It runs a current-runtime domain adapter\nsweep and a universal network-cascade stress test. The Part B rows in\n\\texttt{Part\\_B\\_Engineered\\_Systems/outputs/domain\\_adapter\\_sweep.csv} provide a small release audit for\nenergy systems, network routing, cloud capacity, and artificial intelligence.\nThese outputs check finite-value behavior and regime reporting. They do not\nvalidate any engineering claim.",
        "The diagnostic script \\texttt{Part\\_E\\_Synthesis/supplementary/run\\_partiv\\_discovery.py}\ndoes not simulate every Part B system. It runs a current-runtime domain adapter\nsweep and a universal network-cascade stress test. The Part B rows in\n\\texttt{Part\\_B\\_Engineered\\_Systems/outputs/domain\\_adapter\\_sweep.csv} provide a compact audit for\nenergy systems, network routing, cloud capacity, and artificial intelligence.\nThose rows check finite-value behavior and regime reporting; engineering claims\nstill need engineering measurements.",
    )
    text = text.replace("strictly apply", "apply")
    text = text.replace("strictly reserved", "used")
    text = text.replace("strict mathematical", "mathematical")
    text = text.replace("must be absolutely constant", "has little room to vary")
    text = text.replace("physically required", "a practical requirement")
    text = text.replace("the same physical laws as", "a comparable flow problem to")
    text = text.replace("artificially manipulate", "shape")
    text = text.replace("artificially drive", "drive")
    text = text.replace("not empirical proof", "not field evidence")
    text = text.replace("not empirical validation", "not field validation")
    text = text.replace("candidate discovery targets", "places where later measurement can focus")
    text = text.replace("toy diagnostics", "small diagnostics")
    text = text.replace("falsification targets", "tests that could break the mapping")
    text = text.replace("These are model artifacts", "These files are model outputs")
    text = text.replace(r"\textbf{Status: Derived}", r"\textbf{Status: Candidate model derivation}")
    text = text.replace(r"\textbf{Status: Inferred}", r"\textbf{Status: Hypothesis-level inference}")
    text = text.replace(
        r"\section*{Data Availability} Runtime verification models available in the \texttt{/supplementary} layer.",
        r"\section*{Data Availability} Release-local runtime diagnostics are available under each Part's \texttt{outputs/} folder, with release-wide synthesis artifacts under \texttt{Part\_E\_Synthesis/supplementary/}, \texttt{Part\_E\_Synthesis/outputs/}, and \texttt{Part\_E\_Synthesis/figures/}.",
    )
    text = text.replace(
        r"\texttt{supplementary/run\_partiv\_discovery.py}",
        r"\texttt{Part\_E\_Synthesis/supplementary/run\_partiv\_discovery.py}",
    )
    text = text.replace(
        r"\section*{Data Availability} Release-local runtime diagnostics are available under \texttt{supplementary/}, \texttt{outputs/}, and \texttt{figures/}.",
        r"\section*{Data Availability} Release-local runtime diagnostics are available under each Part's \texttt{outputs/} folder, with release-wide synthesis artifacts under \texttt{Part\_E\_Synthesis/supplementary/}, \texttt{Part\_E\_Synthesis/outputs/}, and \texttt{Part\_E\_Synthesis/figures/}.",
    )
    text = re.sub(
        r"Release-local runtime diagnostics are available under \\texttt\{supplementary/\},\s*\\texttt\{outputs/\}, and \\texttt\{figures/\}\.",
        r"Release-local runtime diagnostics are available under each Part's \texttt{outputs/} folder, with release-wide synthesis artifacts under \texttt{Part\_E\_Synthesis/supplementary/}, \texttt{Part\_E\_Synthesis/outputs/}, and \texttt{Part\_E\_Synthesis/figures/}.",
        text,
        flags=re.S,
    )
    text = text.replace(
        r"\texttt{outputs/domain\_adapter\_sweep.csv}",
        r"\texttt{Part\_B\_Engineered\_Systems/outputs/domain\_adapter\_sweep.csv}",
    )
    text = re.sub(r"\n\\tableofcontents\s*(?:\n\\newpage)?\s*", "\n", text)
    text = re.sub(r"\n?\\nocite\{[^}]*\}\s*", "\n", text, flags=re.S)
    text = text.replace(r"\bibliography{afl_references}", r"\bibliography{universal_afl_references}")
    if text.count(r"\begin{abstract}") > text.count(r"\end{abstract}"):
        text = re.sub(
            r"(\\begin\{abstract\}.*?)(\n\\section\{)",
            lambda match: match.group(1).rstrip() + "\n\\end{abstract}\n\n" + match.group(2),
            text,
            count=1,
            flags=re.S,
        )
    text = _replace_stale_numerical_blocks(text, evidence)
    text = _remove_orphan_back_matter_stubs(text)
    evidence_pattern = (
        r"\\subsection\{Current Runtime Diagnostic: Universal Network Cascade\}\n"
        r".*?they do not by themselves validate any Earth, engineered, social, cosmic, or cognitive empirical claim\.\n\n"
    )
    matches = list(re.finditer(evidence_pattern, text, flags=re.S))
    if len(matches) > 1:
        keep = matches[0]
        chunks = [text[: keep.end()]]
        cursor = keep.end()
        for duplicate in matches[1:]:
            chunks.append(text[cursor : duplicate.start()])
            cursor = duplicate.end()
        chunks.append(text[cursor:])
        text = "".join(chunks)
    text = text.replace(
        "The AFL universal principle is not a metaphor or a framework for qualitative insight. It is a mathematical claim:",
        "The AFL universal principle is a mathematical modelling claim:",
    )
    text = text.replace(
        "The AFL principle has exactly one equation:\n\n\\begin{equation}\n    \\boxed{\\Psi_s^* = \\frac{\\Phi}{C}}\n\\end{equation}\n\nwith the constraint evolution law:",
        "The Part IV operating ratio keeps the full flow-constraint-surface-memory form:\n\n\\begin{equation}\n    \\boxed{\\Psi_s^* = \\left(\\frac{\\Phi}{C}\\right) \\cdot S \\cdot M_s}\n\\end{equation}\n\nThe reduced form $\\Psi_s^*=\\Phi/C$ is used only when $S=1$ and $M_s=1$. The companion constraint evolution law is:",
    )
    if r"\bibliography{universal_afl_references}" not in text:
        text = text.rstrip() + "\n\n\\bibliographystyle{plain}\n\\bibliography{universal_afl_references}\n"
    if r"\end{document}" not in text:
        text = text.rstrip() + "\n\\end{document}\n"
    return text


def write_bibliography() -> None:
    (RELEASE_ROOT / "universal_afl_references.bib").write_text(REAL_BIB)


def main() -> int:
    evidence = _runtime_evidence_paragraph()
    changed = 0
    for path in sorted(RELEASE_ROOT.rglob("*.tex")):
        original = path.read_text(errors="replace")
        updated = _clean_text(path, original, evidence)
        if updated != original:
            path.write_text(updated)
            changed += 1
    write_bibliography()
    print(f"finalized {changed} manuscript files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
