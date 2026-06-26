"""
Export a unified power-density table in canonical SI units (kg, W, W·kg⁻¹).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import config
from physics_engine import select_plot_compact_results
from si_columns import UNIFIED_SI_EXPORT_COLUMNS, select_si_columns
from von_duin_biology import VON_DUIN_LABEL

SI_EXPORT_COLUMNS = UNIFIED_SI_EXPORT_COLUMNS


def _empty_si_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=list(SI_EXPORT_COLUMNS))


def _biology_si_rows(biology: pd.DataFrame) -> pd.DataFrame:
    if biology.empty:
        return _empty_si_frame()

    rows = pd.DataFrame(
        {
            "name": biology["system"].astype(str),
            "domain": "biology",
            "segment": biology["segment"],
            "mass_kg": biology["mass_kg"],
            "power_density_w_per_kg": biology["power_density_w_per_kg"],
            "luminosity_w": biology.get("er_w", pd.Series([pd.NA] * len(biology))),
            "mdot_kg_s": pd.NA,
            "mass_msun": pd.NA,
            "radius_m": pd.NA,
            "eta": pd.NA,
            "track": pd.NA,
            "phi_source": "tabulated_erd",
            "mass_kg_err": pd.NA,
            "power_density_w_per_kg_lo": pd.NA,
            "power_density_w_per_kg_hi": pd.NA,
            "reference": biology.get("reference", pd.Series([pd.NA] * len(biology))),
            "data_source": biology.get("data_source", VON_DUIN_LABEL),
        }
    )
    return rows


def _yso_si_rows(yso: pd.DataFrame) -> pd.DataFrame:
    if yso.empty:
        return _empty_si_frame()

    name_col = "name" if "name" in yso.columns else yso.columns[0]
    rows = pd.DataFrame(
        {
            "name": yso[name_col].astype(str),
            "domain": config.CATEGORY_YOUNG_STELLAR_OBJECTS,
            "segment": pd.NA,
            "mass_kg": yso["mass_kg"],
            "power_density_w_per_kg": yso["power_density_w_per_kg"],
            "luminosity_w": yso["lacc_w"],
            "mdot_kg_s": pd.NA,
            "mass_msun": yso.get("mass_msun", pd.NA),
            "radius_m": pd.NA,
            "eta": pd.NA,
            "track": pd.NA,
            "phi_source": "computed_from_lacc",
            "mass_kg_err": pd.NA,
            "power_density_w_per_kg_lo": pd.NA,
            "power_density_w_per_kg_hi": pd.NA,
            "reference": yso.get("reference", pd.Series([pd.NA] * len(yso))),
            "data_source": "Manara et al. (2022) PPVII",
        }
    )
    return rows


def _compact_si_rows(compact: pd.DataFrame) -> pd.DataFrame:
    plotted = select_plot_compact_results(compact)
    if plotted.empty:
        return _empty_si_frame()

    rows = pd.DataFrame(
        {
            "name": plotted["name"].astype(str),
            "domain": plotted["category"],
            "segment": pd.NA,
            "mass_kg": plotted["mass_kg"],
            "power_density_w_per_kg": plotted["power_density_w_per_kg"],
            "luminosity_w": plotted.get("luminosity_w", pd.NA),
            "mdot_kg_s": plotted.get("mdot_kg_s", pd.NA),
            "mass_msun": plotted.get("mass_msun", pd.NA),
            "radius_m": plotted.get("radius_m", pd.NA),
            "eta": plotted.get("eta", pd.NA),
            "track": plotted.get("track", pd.NA),
            "phi_source": plotted.get("phi_source", pd.NA),
            "mass_kg_err": plotted.get("mass_kg_err", pd.NA),
            "power_density_w_per_kg_lo": plotted.get(
                "power_density_w_per_kg_lo", pd.NA
            ),
            "power_density_w_per_kg_hi": plotted.get(
                "power_density_w_per_kg_hi", pd.NA
            ),
            "reference": pd.NA,
            "data_source": "Vidal (2020) compact-object tables",
        }
    )
    return rows


def _smbh_si_rows(smbh: pd.DataFrame) -> pd.DataFrame:
    if smbh.empty:
        return _empty_si_frame()

    plotted = smbh[smbh["track"] == "gravitational"].copy()
    rows = pd.DataFrame(
        {
            "name": plotted["name"].astype(str),
            "domain": plotted["category"],
            "segment": pd.NA,
            "mass_kg": plotted["mass_kg"],
            "power_density_w_per_kg": plotted["power_density_w_per_kg"],
            "luminosity_w": plotted.get("luminosity_w", pd.NA),
            "mdot_kg_s": plotted.get("mdot_kg_s", pd.NA),
            "mass_msun": plotted.get("mass_msun", pd.NA),
            "radius_m": plotted.get("radius_m", pd.NA),
            "eta": plotted.get("eta", pd.NA),
            "track": plotted.get("track", pd.NA),
            "phi_source": plotted.get("phi_source", pd.NA),
            "mass_kg_err": pd.NA,
            "power_density_w_per_kg_lo": pd.NA,
            "power_density_w_per_kg_hi": pd.NA,
            "reference": pd.NA,
            "data_source": "Vidal (2020) Table 5",
        }
    )
    return rows


def build_power_density_si_table(
    *,
    compact_results: pd.DataFrame,
    yso_results: pd.DataFrame,
    biology_results: pd.DataFrame,
    smbH_results: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Assemble the unified SI export table (same cohorts as the unified master)."""
    parts = [
        _biology_si_rows(biology_results),
        _yso_si_rows(yso_results),
        _compact_si_rows(compact_results),
    ]
    if smbH_results is not None and not smbH_results.empty:
        parts.append(_smbh_si_rows(smbH_results))

    combined = pd.concat(parts, ignore_index=True)
    return combined[list(SI_EXPORT_COLUMNS)]


def export_power_density_si_csv(
    *,
    compact_results: pd.DataFrame,
    yso_results: pd.DataFrame,
    biology_results: pd.DataFrame,
    smbH_results: pd.DataFrame | None = None,
    output_path: Path | None = None,
) -> tuple[Path, int]:
    """Write the unified SI table to processed/power_density_si.csv."""
    target = output_path or config.PROCESSED_SI_CSV
    target.parent.mkdir(parents=True, exist_ok=True)
    frame = build_power_density_si_table(
        compact_results=compact_results,
        yso_results=yso_results,
        biology_results=biology_results,
        smbH_results=smbH_results,
    )
    frame.to_csv(target, index=False)
    return target, len(frame)
