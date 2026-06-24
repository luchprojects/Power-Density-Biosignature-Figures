"""
Data ingestion and cleaning for multi-domain power-density datasets.

Canonical workspace inputs
----------------------------
- ``data/Power density data.csv`` — compact objects (WD / NS / transient BH)
- ``data/yso/mdots_forclement.dat`` — YSO accretion parameters (built from Manara PPVII TSV)
- Manara PPVII compilation (TSV / CSV) — supplemental YSO metadata
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

import config

COLUMN_ALIASES: dict[str, str] = {
    "category": "category",
    "sheet": "category",
    "object_type": "category",
    "type": "category",
    "name": "name",
    "object": "name",
    "source": "name",
    "mass (solar mass)": "mass_msun",
    "mass_msun": "mass_msun",
    "mass_solar": "mass_msun",
    "m_msun": "mass_msun",
    "accretion rate (g.s-1)": "mdot_g_s",
    "accretion_rate_g_s": "mdot_g_s",
    "mdot_g_s": "mdot_g_s",
    "mdot (solarmass/year)": "mdot_msun_yr",
    "mdot_msun_yr": "mdot_msun_yr",
    "mdot_msun_per_yr": "mdot_msun_yr",
    "mdot_kg_s": "mdot_kg_s",
    "radius_m": "radius_m",
    "radius_rsun": "radius_rsun",
    "radius (solar)": "radius_rsun",
    "radius_au": "radius_au",
    "power density (w.kg-1)": "power_density_reported_wkg",
    "power_density_w_per_kg": "power_density_reported_wkg",
    "erd (erg.s-1.g-1) assuming 2.3e-4 accretion efficiency": "erd_erg_s_g",
    "erd_erg_s_g": "erd_erg_s_g",
}

SHEET_NAME_TO_CATEGORY: dict[str, str] = {
    "cataclysmic variables": config.CATEGORY_CATACLYSMIC_VARIABLES,
    "cataclysmic_variables": config.CATEGORY_CATACLYSMIC_VARIABLES,
    "white dwarfs": config.CATEGORY_CATACLYSMIC_VARIABLES,
    "wds": config.CATEGORY_CATACLYSMIC_VARIABLES,
    "neutron stars": config.CATEGORY_NEUTRON_STARS,
    "neutron_stars": config.CATEGORY_NEUTRON_STARS,
    "transient black holes": config.CATEGORY_TRANSIENT_BLACK_HOLES,
    "transient_black_holes": config.CATEGORY_TRANSIENT_BLACK_HOLES,
    "stellar black holes": config.CATEGORY_TRANSIENT_BLACK_HOLES,
}

SKIP_NAME_PATTERNS: tuple[str, ...] = (
    r"^average$",
    r"^mean$",
    r"^total$",
    r"^summary$",
)

NUMERIC_TOKEN = re.compile(r"^[\d,\.Ee+\-]+$")

# Vidal (2020) Tables 3 (NS) and 4 (BH) tabulate ERD a factor of 1000 too high:
# the values were computed as L/M in W.kg-1 (mass in kg) but placed in the
# "erg.s-1.g-1" column without the per-gram (g->kg) step, leaving a x1000 (g/kg)
# slip. With the paper's intended efficiency eta=0.1 = GM/(c^2 R), the tabulated
# Mdot and ERD only close (eta_implied -> 0.1) after dividing ERD by 1000.
# WD Table 2 (eta=2.3e-4) is unaffected. See review note / git history.
VIDAL_NS_BH_ERD_GRAM_KILOGRAM_CORRECTION = 1.0e-3
_ERD_CORRECTED_CATEGORIES = frozenset(
    {config.CATEGORY_NEUTRON_STARS, config.CATEGORY_TRANSIENT_BLACK_HOLES}
)


def _normalize_header(header: str) -> str:
    cleaned = header.strip().lower().replace("_", " ")
    return re.sub(r"\s+", " ", cleaned)


def _map_columns(raw_columns: Iterable[str]) -> dict[str, str]:
    rename_map: dict[str, str] = {}
    for column in raw_columns:
        canonical = COLUMN_ALIASES.get(_normalize_header(column))
        if canonical is not None:
            rename_map[column] = canonical
    return rename_map


def _coerce_numeric_series(series: pd.Series) -> pd.Series:
    if series.dtype.kind in {"i", "u", "f"}:
        return pd.to_numeric(series, errors="coerce")

    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False)
        .str.replace(r"^[<>~≈]\s*", "", regex=True)
        .str.replace(r"\s+", "", regex=True)
    )
    cleaned = cleaned.replace({"": np.nan, "nan": np.nan, "None": np.nan, "--": np.nan})
    return pd.to_numeric(cleaned, errors="coerce")


def _should_skip_row(name_value: object) -> bool:
    if pd.isna(name_value):
        return True
    name_text = str(name_value).strip().lower()
    if not name_text:
        return True
    return any(re.match(pattern, name_text) for pattern in SKIP_NAME_PATTERNS)


def _normalize_category(value: object, fallback: str | None = None) -> str:
    if pd.isna(value) or str(value).strip() == "":
        if fallback is None:
            raise ValueError("Missing category and no fallback provided.")
        return fallback

    key = str(value).strip().lower()
    if key in SHEET_NAME_TO_CATEGORY:
        return SHEET_NAME_TO_CATEGORY[key]
    if key in config.COMPACT_OBJECT_CATEGORIES:
        return key
    raise ValueError(f"Unrecognized category label: {value}")


def _validate_compact_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    required = {"category", "name", "mass_msun"}
    missing = required - set(dataframe.columns)
    if missing:
        raise ValueError(f"Compact-object table missing columns: {missing}")

    mdot_columns = {"mdot_kg_s", "mdot_g_s", "mdot_msun_yr"}
    has_mdot = mdot_columns.intersection(dataframe.columns)
    has_erd = "erd_erg_s_g" in dataframe.columns
    if not has_mdot and not has_erd:
        raise ValueError("Each row needs mdot or ERD for power-density derivation.")

    valid_mdot = pd.Series(False, index=dataframe.index)
    for column in has_mdot:
        valid_mdot = valid_mdot | dataframe[column].notna()

    valid = (
        dataframe["mass_msun"].notna()
        & (dataframe["mass_msun"] > 0)
        & (~dataframe["name"].apply(_should_skip_row))
        & (valid_mdot | dataframe.get("erd_erg_s_g", pd.Series(np.nan, index=dataframe.index)).notna())
    )
    cleaned = dataframe.loc[valid].copy()
    if cleaned.empty:
        raise ValueError("No valid compact-object rows after cleaning.")
    return cleaned.reset_index(drop=True)


def normalize_dataframe(
    dataframe: pd.DataFrame,
    default_category: str | None = None,
) -> pd.DataFrame:
    renamed = dataframe.rename(columns=_map_columns(dataframe.columns))

    if "category" not in renamed.columns and default_category is not None:
        renamed["category"] = default_category
    if "name" not in renamed.columns:
        renamed["name"] = renamed.index.astype(str)

    for column in [
        "mass_msun",
        "mdot_kg_s",
        "mdot_g_s",
        "mdot_msun_yr",
        "radius_m",
        "radius_rsun",
        "radius_au",
        "power_density_reported_wkg",
        "erd_erg_s_g",
    ]:
        if column in renamed.columns:
            renamed[column] = _coerce_numeric_series(renamed[column])

    renamed["category"] = renamed["category"].apply(
        lambda value: _normalize_category(value, fallback=default_category)
    )
    return _validate_compact_dataframe(renamed)


def _is_numeric_token(value: str) -> bool:
    return bool(NUMERIC_TOKEN.match(value.strip()))


def _parse_vidal_pdf_table(section_title: str, category: str, next_title: str) -> pd.DataFrame:
    """
    Extract tabular rows from the Vidal (2020) PDF text layer.

    The PDF stores each column on separate lines (name, mass, mdot, ERD).
    """
    import fitz

    document = fitz.open(config.VIDAL_PDF)
    text = "".join(page.get_text() for page in document)

    start = text.find(section_title)
    if start < 0:
        return pd.DataFrame()

    end = text.find(next_title, start + len(section_title))
    chunk = text[start:end if end > 0 else None]
    lines = [line.strip() for line in chunk.splitlines() if line.strip()]

    # Skip prose/header until the first object name row appears.
    records: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        name = lines[index]
        if (
            index + 3 >= len(lines)
            or _is_numeric_token(name)
            or name.upper() in {"NAME", "AVERAGE"}
            or "Table" in name
            or "Mass" in name
            or "Accretion" in name
            or "ERD" in name
            or "erg" in name
        ):
            index += 1
            continue

        mass_token = lines[index + 1]
        mdot_token = lines[index + 2]
        erd_token = lines[index + 3]

        if not (
            _is_numeric_token(mass_token)
            and _is_numeric_token(mdot_token)
            and _is_numeric_token(erd_token)
        ):
            index += 1
            continue

        if name.upper() == "AVERAGE":
            break

        erd_value = float(erd_token.replace(",", "."))
        if category in _ERD_CORRECTED_CATEGORIES:
            erd_value *= VIDAL_NS_BH_ERD_GRAM_KILOGRAM_CORRECTION

        records.append(
            {
                "name": name,
                "mass_msun": float(mass_token.replace(",", ".")),
                "mdot_msun_yr": float(mdot_token.replace(",", ".")),
                "erd_erg_s_g": erd_value,
                "category": category,
            }
        )
        index += 4

    return pd.DataFrame.from_records(records)


def _load_white_dwarf_table() -> pd.DataFrame:
    source = config.LEGACY_WD_TABLE
    if not source.exists():
        raise FileNotFoundError(f"WD table not found: {source}")
    return load_csv_file(source, default_category=config.CATEGORY_CATACLYSMIC_VARIABLES)


def _load_neutron_star_table() -> pd.DataFrame:
    return _parse_vidal_pdf_table(
        section_title="Table 2 - Energy rate density of 130 white dwarfs",
        category=config.CATEGORY_NEUTRON_STARS,
        next_title="Table 3 - Energy rate density of 30 neutron stars",
    )


def _load_transient_black_hole_table() -> pd.DataFrame:
    return _parse_vidal_pdf_table(
        section_title="Table 3 - Energy rate density of 30 neutron stars",
        category=config.CATEGORY_TRANSIENT_BLACK_HOLES,
        next_title="Table 4 - Energy rate density of 19 transient black holes",
    )


def assemble_compact_objects_csv(output_path: Path | None = None) -> Path:
    """
    Build ``data/Power density data.csv`` from verified workspace sources.

    WDs: Table 1 accreting WDs CSV
    NSs: Vidal (2020) PDF Table 2 text layer (30 systems)
    BHs: Vidal (2020) PDF Table 3 text layer (19 systems)
    """
    target = output_path or config.COMPACT_OBJECTS_CSV
    target.parent.mkdir(parents=True, exist_ok=True)

    frames = [
        _load_white_dwarf_table(),
        _load_neutron_star_table(),
        _load_transient_black_hole_table(),
    ]
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(target, index=False)
    return target


def load_compact_objects(path: Path | None = None, rebuild: bool = True) -> pd.DataFrame:
    """Load compact-object populations from the canonical CSV path."""
    csv_path = path or config.COMPACT_OBJECTS_CSV
    if rebuild or not csv_path.exists():
        assemble_compact_objects_csv(csv_path)
    return normalize_dataframe(pd.read_csv(csv_path))


def load_power_density_data(path: Path | None = None) -> pd.DataFrame:
    """Primary compact-object loader (alias for pipeline compatibility)."""
    return load_compact_objects(path)


def summarize_dataset(dataframe: pd.DataFrame) -> pd.DataFrame:
    return (
        dataframe.groupby("category")
        .size()
        .reset_index(name="count")
        .sort_values("category")
    )


def load_csv_file(path: Path, default_category: str | None = None) -> pd.DataFrame:
    raw = pd.read_csv(path, comment="#")
    return normalize_dataframe(raw, default_category=default_category)


def _resolve_manara_compilation_path() -> Path:
    if config.MANARA_COMPILATION_TSV.exists():
        return config.MANARA_COMPILATION_TSV
    raise FileNotFoundError(
        f"Manara 2022 compilation not found: {config.MANARA_COMPILATION_TSV}"
    )


def _build_mdots_forclement_from_compilation(output_path: Path) -> Path:
    """
    Derive ``mdots_forclement.dat`` from the Manara PPVII compilation.

    Pristine control cohort: Alcalá et al. (2017) + Manara et al. (2017) only
    (ref_xs tags Alcala+14,17,19 and Manara+16,17).

    Stellar masses use the Somers (2020) SPOTS framework: Baraffe+2015 spotless
    masses (Mstar_B15_xs_DR3) inflated by the configured spot covering fraction.

    Columns: source  mass_msun  log_macc  log_lacc  teff_k  lstar_lsun
             mass_spotless_msun  radius_au  dist_pc  reference
    """
    compilation_path = _resolve_manara_compilation_path()
    if compilation_path.suffix.lower() == ".tsv":
        catalog = pd.read_csv(compilation_path, sep="\t", low_memory=False)
    else:
        catalog = pd.read_csv(compilation_path, low_memory=False)

    if "ref_xs" in catalog.columns:
        catalog = catalog[catalog["ref_xs"].isin(config.YSO_PREFERRED_REFERENCE_MARKERS)].copy()

    working = catalog.rename(columns={"Source": "source"}).copy()
    working["teff_k"] = _coerce_numeric_series(working["Teff_xs"])
    working["lstar_lsun"] = _coerce_numeric_series(
        working.get("Lstar_xs_DR3", working.get("Lstar_xs"))
    )
    working["mass_spotless_msun"] = _coerce_numeric_series(
        working.get("Mstar_B15_xs_DR3", working.get("Mstar_B15_xs"))
    )
    working["log_macc"] = _coerce_numeric_series(working["logMacc_PPVII"])
    working["log_lacc"] = _coerce_numeric_series(working["logLacc_xs"])
    working["dist_pc"] = _coerce_numeric_series(
        working.get("dist_PPVII", working.get("EDR3_Dist_PPVII"))
    )
    working["radius_au"] = _coerce_numeric_series(working.get("H20_R68_au_DR3"))

    import physics_engine

    working["mass_msun"] = working.apply(
        lambda row: physics_engine.compute_somers_spots_mass_msun(
            float(row["mass_spotless_msun"]),
            teff_k=float(row["teff_k"]) if pd.notna(row["teff_k"]) else None,
        )
        if pd.notna(row["mass_spotless_msun"]) and float(row["mass_spotless_msun"]) > 0
        else float("nan"),
        axis=1,
    )

    valid = (
        working["source"].notna()
        & working["mass_msun"].notna()
        & working["log_lacc"].notna()
        & (working["mass_msun"] > 0.01)
        & (working["mass_msun"] < 10.0)
        & (working["log_lacc"] > -12.0)
        & (working["log_lacc"] < 2.0)
    )
    export = working.loc[
        valid,
        [
            "source",
            "mass_msun",
            "mass_spotless_msun",
            "teff_k",
            "lstar_lsun",
            "log_macc",
            "log_lacc",
            "radius_au",
            "dist_pc",
            "ref_xs",
        ],
    ]
    export = export.rename(columns={"ref_xs": "reference"})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    export.to_csv(output_path, sep=" ", index=False, header=True)
    return output_path


def load_mdots_forclement(path: Path | None = None, rebuild: bool = True) -> pd.DataFrame:
    """
    Load YSO accretion parameters with Somers (2020) SPOTS-corrected masses.

    Rebuilds ``mdots_forclement.dat`` from the Manara compilation by default so
    mass calibration tracks the latest SPOTS configuration.
    """
    dat_path = path or config.MANARA_MDOTS_DAT
    if rebuild or not dat_path.exists():
        _build_mdots_forclement_from_compilation(dat_path)

    raw = pd.read_csv(dat_path, sep=r"\s+", engine="python")
    raw = raw.rename(columns={col: col.lower() for col in raw.columns})

    column_map = {
        "source": "name",
        "mass_msun": "mass_msun_somers",
        "mass_spotless_msun": "mass_spotless_msun",
        "teff_k": "teff_k",
        "lstar_lsun": "lstar_lsun",
        "log_macc": "log_macc",
        "log_lacc": "log_lacc",
        "radius_au": "radius_au",
        "dist_pc": "dist_pc",
        "reference": "reference",
    }
    renamed = raw.rename(columns=column_map)

    for column in [
        "mass_msun_somers",
        "mass_spotless_msun",
        "teff_k",
        "lstar_lsun",
        "log_macc",
        "log_lacc",
        "radius_au",
        "dist_pc",
    ]:
        if column in renamed.columns:
            renamed[column] = _coerce_numeric_series(renamed[column])

    renamed["category"] = config.CATEGORY_YOUNG_STELLAR_OBJECTS
    renamed["mass_calibration"] = "somers_2020_spots"
    renamed["spot_coverage_fraction"] = config.YSO_CONTROL.spot_coverage_fraction
    renamed["mass_msun"] = renamed["mass_msun_somers"]

    valid = (
        renamed["name"].notna()
        & renamed["mass_msun"].notna()
        & renamed["log_lacc"].notna()
        & (renamed["mass_msun"] > 0)
    )
    cleaned = renamed.loc[valid].copy()
    if cleaned.empty:
        raise ValueError(f"No valid YSO rows parsed from {dat_path}.")
    return cleaned.reset_index(drop=True)


def load_yso_control_group() -> pd.DataFrame:
    """Load YSO control data from mdots_forclement.dat (built from Manara if needed)."""
    return load_mdots_forclement()
