"""Canonical SI column schemas for processed pipeline tables."""

from __future__ import annotations

import pandas as pd

PROCESSED_COMPACT_SI_COLUMNS: tuple[str, ...] = (
    "name",
    "category",
    "track",
    "mass_kg",
    "mass_msun",
    "mdot_kg_s",
    "radius_m",
    "eta",
    "luminosity_w",
    "power_density_w_per_kg",
    "phi_source",
    "mass_kg_err",
    "power_density_w_per_kg_lo",
    "power_density_w_per_kg_hi",
    "dubus_table",
)

PROCESSED_YSO_SI_COLUMNS: tuple[str, ...] = (
    "name",
    "mass_msun_somers",
    "mass_spotless_msun",
    "teff_k",
    "lstar_lsun",
    "log_macc",
    "log_lacc",
    "radius_au",
    "dist_pc",
    "reference",
    "category",
    "mass_calibration",
    "spot_coverage_fraction",
    "mass_msun",
    "mass_kg",
    "lacc_w",
    "power_density_w_per_kg",
)

PROCESSED_BIOLOGY_SI_COLUMNS: tuple[str, ...] = (
    "sub_realm",
    "group",
    "system",
    "mass_kg",
    "er_w",
    "power_density_w_per_kg",
    "comments",
    "reference",
    "segment",
    "color",
    "data_source",
)

UNIFIED_SI_EXPORT_COLUMNS: tuple[str, ...] = (
    "name",
    "domain",
    "segment",
    "mass_kg",
    "power_density_w_per_kg",
    "luminosity_w",
    "mdot_kg_s",
    "mass_msun",
    "radius_m",
    "eta",
    "track",
    "phi_source",
    "mass_kg_err",
    "power_density_w_per_kg_lo",
    "power_density_w_per_kg_hi",
    "reference",
    "data_source",
)


def select_si_columns(frame: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    """Return only SI columns that exist in frame."""
    present = [column for column in columns if column in frame.columns]
    return frame[present].copy()
