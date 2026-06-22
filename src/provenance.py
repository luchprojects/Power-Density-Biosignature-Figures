"""
Data-provenance ledger and reproducibility manifest for figure production.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import config


FIGURE_TRACKING_ROWS: tuple[dict[str, str], ...] = (
    {
        "figure_asset": "figure_biology.pdf",
        "data_source": "van Duin (2024) MOESM1 ERD supplementary table (Section I)",
        "physics_validation": (
            f"Empirical ERD ({config.POWER_DENSITY_UNIT}) vs. mass ({config.MASS_UNIT}) "
            "from compiled literature measurements; rows classified into prokaryote, "
            "unicellular eukaryote, and multicellular segments"
        ),
        "plot_rule": (
            "Empirical scatter only; Chaisson (2003/2011) living envelope "
            f"({config.CHAISSON_LIVING_ENVELOPE_MIN_W_PER_KG:g}–"
            f"{config.CHAISSON_LIVING_ENVELOPE_MAX_W_PER_KG:g} {config.POWER_DENSITY_UNIT}); "
            "Chaisson (2001) benchmarks; van Duin stability boundary"
        ),
        "task_owner": "LK",
        "status": "automated",
    },
    {
        "figure_asset": "figure_yso.pdf",
        "data_source": "Manara et al. (2022) PPVII compilation",
        "physics_validation": (
            "Somers (2020) SPOTS mass inflation of Baraffe+2015 spotless masses; "
            "Alcalá+2017 and Manara+2017 reference filter"
        ),
        "plot_rule": "Empirical scatter only; linestyle=none enforced",
        "task_owner": "LK",
        "status": "automated",
    },
    {
        "figure_asset": "figure_compact_objects.pdf",
        "data_source": "Tables 1--4 (WDs, NSs, transient BHs)",
        "physics_validation": (
            "Gravitational eta = GM/(Rc^2); WD nuclear track eta=0.007; "
            "reported ERD where available"
        ),
        "plot_rule": "Gravitational track displayed; scatter markers only",
        "task_owner": "CV",
        "status": "automated",
    },
    {
        "figure_asset": "figure_wd_dubus_uncertainties.pdf",
        "data_source": (
            "Dubus, Otulakowska-Hypka & Lasota (2018) A&A 617, A26 — "
            "Tables A.2--A.3 (130 CVs)"
        ),
        "physics_validation": (
            "68% MC intervals on M1 and mass transfer rate; "
            "Phi_m uncertainty propagated from Ṁ and M1 (gravitational track)"
        ),
        "plot_rule": (
            "WD-only zoom panel with asymmetric error bars; "
            "no literature reference overlays"
        ),
        "task_owner": "CV",
        "status": "automated",
    },
    {
        "figure_asset": "figure_unified_master.pdf",
        "data_source": "Integrated multi-scale continuum",
        "physics_validation": (
            f"van Duin (2024) stability boundary at 10^5 {config.POWER_DENSITY_UNIT}; "
            "Chaisson living envelope and 2001 benchmarks as literature overlays"
        ),
        "plot_rule": (
            "Geometric decoupling scatter: YSO filled circles (z=1), compact filled circles "
            "per category (z=2), biology per segment (z=3) — diamonds on unified, circles on "
            "biology panel; Chaisson envelope/benchmarks; van Duin solid upper reference"
        ),
        "task_owner": "CV & LK",
        "status": "automated",
    },
)


def write_tracking_ledger(output_path: Path | None = None) -> Path:
    """Export the figure-to-data tracking matrix as CSV."""
    target = output_path or config.DATA_TRACKING_LEDGER_CSV
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(FIGURE_TRACKING_ROWS).to_csv(target, index=False)
    return target


def write_provenance_manifest(
    *,
    compact_results: pd.DataFrame,
    yso_results: pd.DataFrame,
    biology_results: pd.DataFrame | None = None,
    saved_figures: dict[str, Path],
    output_path: Path | None = None,
) -> Path:
    """Write a JSON manifest summarising inputs, counts, and outputs."""
    target = output_path or config.PROVENANCE_MANIFEST_JSON
    target.parent.mkdir(parents=True, exist_ok=True)

    yso_refs = (
        yso_results["reference"].value_counts().to_dict()
        if "reference" in yso_results.columns
        else {}
    )
    compact_by_category = (
        compact_results.groupby("category").size().to_dict()
        if not compact_results.empty
        else {}
    )

    biology_by_segment = (
        biology_results.groupby("segment").size().to_dict()
        if biology_results is not None and not biology_results.empty
        else {}
    )

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "mass_unit": "kg (SI display)",
        "power_density_unit": config.POWER_DENSITY_UNIT,
        "mass_unit": config.MASS_UNIT,
        "van_duin_limit_w_per_kg": config.VAN_DUIN_DISSIPATIVE_LIMIT_W_PER_KG,
        "chaisson_living_envelope_w_per_kg": [
            config.CHAISSON_LIVING_ENVELOPE_MIN_W_PER_KG,
            config.CHAISSON_LIVING_ENVELOPE_MAX_W_PER_KG,
        ],
        "chaisson_2001_benchmarks_w_per_kg": {
            "sun": config.CHAISSON_SUN_POWER_DENSITY_W_PER_KG,
            "human": config.CHAISSON_2001_HUMAN_W_PER_KG,
            "society": config.CHAISSON_2001_SOCIETY_W_PER_KG,
        },
        "yso_mass_calibration": "somers_2020_spots",
        "yso_spot_coverage_fraction": config.YSO_CONTROL.spot_coverage_fraction,
        "yso_reference_filter": list(config.YSO_PREFERRED_REFERENCE_MARKERS),
        "yso_count": int(len(yso_results)),
        "yso_reference_counts": yso_refs,
        "compact_count": int(len(compact_results)),
        "compact_by_category": compact_by_category,
        "biology_count": int(len(biology_results)) if biology_results is not None else 0,
        "biology_by_segment": biology_by_segment,
        "biology_source": "van Duin (2024) MOESM1 ERD Table Section I",
        "figures": {key: str(path) for key, path in saved_figures.items()},
        "empirical_colors": {
            key: {"hex": hex_code, "label": label}
            for key, (hex_code, label) in config.EMPIRICAL_COLOR_REGISTRY.items()
        },
        "plot_protocol": {
            "empirical_geometry": "geometric_decoupling_scatter",
            "scatter_layers": {
                "background": "YSO open rings (yellow edge, s=15, z=1)",
                "midground": "Compact filled circles per category (s=40, z=2)",
                "foreground": "Biology per segment — diamonds (unified), circles (biology panel)",
            },
            "marker_shape": config.PLOT_MARKER_SHAPE,
            "allowed_continuous_lines": [
                "chaisson_living_envelope",
                "chaisson_2001_benchmarks",
                "van_duin_stability_boundary",
            ],
            "axis_labels": {
                "mass": config.AXIS_LABEL_MASS,
                "power_density": config.AXIS_LABEL_POWER_DENSITY,
            },
        },
    }
    target.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return target
