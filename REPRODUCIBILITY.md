# Reproducibility

Run commands from the release root:

```bash
cd /home/bampita/Projects/CDFD/CDFD-Part-IV-Release
```

## Python Environment

Use the workspace virtual environment when available:

```bash
/home/bampita/Projects/CDFD/.venv/bin/python -m pip install -r requirements.txt
```

or create the conda environment:

```bash
conda env create -f environment.yml
conda activate cdfd-part-iv-public
```

## Regenerate Runtime Discoveries

```bash
MPLCONFIGDIR=/tmp/cdfd_partiv_matplotlib \
/home/bampita/Projects/CDFD/.venv/bin/python Part_E_Synthesis/supplementary/run_partiv_discovery.py
```

The command writes Part-specific artifacts under each Part's `outputs/` folder
and release-wide synthesis artifacts under `Part_E_Synthesis/outputs/` and
`Part_E_Synthesis/figures/`.
It does not write into the root workspace `experiments/outputs` directory.
The manifest `Part_E_Synthesis/supplementary/active_paper_manifest.json` maps
each runtime adapter row to its active 45-paper destination. It excludes the
13 archived predecessors and makes merged associations explicit.

Expected generated files:

- `Part_E_Synthesis/outputs/runtime_info.json`
- `Part_E_Synthesis/outputs/domain_adapter_sweep.json`
- `Part_E_Synthesis/outputs/domain_adapter_sweep.csv`
- `Part_E_Synthesis/outputs/universal_collapse.json`
- `Part_E_Synthesis/outputs/partiv_discovery_summary.md`
- `Part_E_Synthesis/outputs/interactive_index.html`
- `Part_E_Synthesis/figures/universal_cascade.png`
- `Part_E_Synthesis/figures/domain_sweep_psi.png`
- `Part_A_Earth_Systems/outputs/domain_adapter_sweep.csv` through the matching Part B, C, D, F, and G output slices.

## Active Manuscript Maintenance

The pre-consolidation `finalize_partiv_manuscripts.py` and
`major_upgrade_partiv_manuscripts.py` are guarded compatibility stubs. Do not
run them: they describe the former 58-paper source layout and would recreate
material intentionally moved to the shared methods companion. Make scoped
edits to active papers, then run the redundancy audit and PDF build.

## Build Interactive Panels

```bash
/home/bampita/Projects/CDFD/.venv/bin/python Part_E_Synthesis/supplementary/make_interactive_panels.py
```

This creates `Part_E_Synthesis/outputs/interactive_index.html`.

## Compile PDFs

If `latexmk` is installed, compile from the release root with the release-local
build helper:

```bash
/home/bampita/Projects/CDFD/.venv/bin/python Part_E_Synthesis/supplementary/build_partiv_pdfs.py
```

The helper runs each manuscript in its own subdirectory under
`/tmp/cdfd_partiv_build` unless
`CDFD_PARTIV_BUILD_DIR` is set, then copies release PDFs into each Part folder's
`PDFs/` accessory directory with section-prefixed names such as
`A01_Earth_Unified_Environmental_Transport.pdf`.
The manuscripts use BibTeX. Run through `latexmk` rather than a single
`pdflatex` pass.

## Output Interpretation

The outputs are model records. They check the CDFD/AFL notation, runtime APIs,
finite-value behavior, and selected domain-adapter stress responses. They do not
stand in for Earth, engineered, social, cosmic, cognitive, or biomedical data.
