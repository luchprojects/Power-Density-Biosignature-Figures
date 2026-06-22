"""
van Duin (2024) supplementary ERD compilation — biological systems (Section I).

Loads empirical mass / ERD measurements from the MOESM1 table and assigns each
row to Prokaryotes, Eukaryotes (unicellular), or Multicellular for figure display.
"""

from __future__ import annotations

import re
from pathlib import Path
from dataclasses import dataclass

import numpy as np
import pandas as pd

import config

VON_DUIN_LABEL = "van Duin (2024)"
VON_DUIN_HEADER_ROW = 6

PROKARYOTE_SUBREALMS = frozenset({"i) bacteria", "i) archaea", "ii) bacteria"})
MULTICELLULAR_META_SUBREALMS = frozenset({"scaling", "lifetime", "evolution"})

PROKARYOTE_PATTERN = re.compile(
    r"prokary|bacter|archae|cyanobacter|escherichia|klebsiella|paracoccus|methanogen",
    re.IGNORECASE,
)
UNICELLULAR_PATTERN = re.compile(
    r"protozoa|protist|uni.?cell|micro.?alga|micro-algae|yeast|"
    r"chlamydomonas|chlorolla|selenastrum|gloeobacter|coccochloris",
    re.IGNORECASE,
)
MULTICELLULAR_PATTERN = re.compile(
    r"plant|tree|seedling|metazoa|mammal|bird|insect|fish|amphib|reptil|animal|"
    r"herb|forb|vascular|mollusc|crustace|endotherm|ectotherm|dinosaur|whale|"
    r"invertebrate|spider|tortoise|lizard|snake|turtle|penguin|rodent|shrew|"
    r"cephalopod|copepod|krill|decapod|peracarid|gelatinous|sugar cane|"
    r"whole plant|above-ground|human|brain|body|heart|liver|muscle|kidney|lung|"
    r"planarian|mesotherm|hominin|man\b|ectomycorrhizal",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BiologySegment:
    label: str
    color: str


BIOLOGY_SEGMENTS: tuple[BiologySegment, ...] = (
    BiologySegment("Prokaryotes", config.COLOR_PROKARYOTES),
    BiologySegment("Eukaryotes", config.COLOR_EUKARYOTES),
    BiologySegment("Multicellular", config.COLOR_MULTICELLULAR),
)


def _coerce_numeric(series: pd.Series) -> pd.Series:
    if series.dtype.kind in {"i", "u", "f"}:
        return pd.to_numeric(series, errors="coerce")
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False)
        .replace({"": np.nan, "nan": np.nan, "None": np.nan})
    )
    return pd.to_numeric(cleaned, errors="coerce")


def _biology_section_end(raw: pd.DataFrame) -> int:
    for index, value in enumerate(raw.iloc[:, 0].astype(str)):
        if value.strip().startswith("II)"):
            return index
    return len(raw)


def classify_segment(sub_realm: str, group: str, system: str) -> str | None:
    """Map a van Duin Section-I row to a figure segment label."""
    sub = (sub_realm or "").strip().lower()
    group_text = (group or "").strip().lower()
    system_text = (system or "").strip().lower()
    combined = f"{group_text} {system_text}"

    if sub in PROKARYOTE_SUBREALMS or PROKARYOTE_PATTERN.search(combined):
        return "Prokaryotes"

    if sub.startswith("ic)") or sub in MULTICELLULAR_META_SUBREALMS:
        return "Multicellular"

    if MULTICELLULAR_PATTERN.search(combined):
        return "Multicellular"

    if UNICELLULAR_PATTERN.search(combined):
        return "Eukaryotes"

    if sub == "ii) eukaryotes":
        if "micro-algae" in group_text or "unicellular" in group_text:
            return "Eukaryotes"
        return "Multicellular"

    if sub == "iii) eukaryotes":
        if UNICELLULAR_PATTERN.search(combined) or (
            "fungi" in group_text and "ectomycorrhizal" not in group_text
        ):
            return "Eukaryotes"
        return "Multicellular"

    return None


def load_von_duin_erd_table(path: Path | None = None) -> pd.DataFrame:
    """Parse the van Duin (2024) MOESM1 CSV and return Section-I biology rows."""
    source = path or config.VON_DUIN_ERD_CSV
    if not source.exists():
        raise FileNotFoundError(f"van Duin ERD table not found: {source}")

    raw = pd.read_csv(source, header=VON_DUIN_HEADER_ROW, low_memory=False)
    raw = raw.rename(
        columns={
            raw.columns[0]: "sub_realm",
            raw.columns[1]: "group",
            raw.columns[2]: "system",
            raw.columns[3]: "mass_kg",
            raw.columns[4]: "er_w",
            raw.columns[5]: "erd_wkg",
            raw.columns[6]: "comments",
            raw.columns[7]: "reference",
        }
    )

    section = raw.iloc[: _biology_section_end(raw)].copy()
    section["sub_realm_ff"] = section["sub_realm"].replace("", np.nan).ffill()
    section["group_ff"] = section["group"].replace("", np.nan).ffill()

    for column in ("mass_kg", "er_w", "erd_wkg"):
        section[column] = _coerce_numeric(section[column])

    valid = (
        section["mass_kg"].notna()
        & section["erd_wkg"].notna()
        & (section["mass_kg"] > 0)
        & (section["erd_wkg"] > 0)
    )
    rows = section.loc[valid].copy()
    if rows.empty:
        raise ValueError(f"No valid biology rows parsed from {source}.")

    rows["segment"] = rows.apply(
        lambda row: classify_segment(
            str(row["sub_realm_ff"]),
            str(row["group_ff"]),
            str(row["system"]),
        ),
        axis=1,
    )
    classified = rows[rows["segment"].notna()].copy()
    if classified.empty:
        raise ValueError("No biology rows matched Prokaryotes/Eukaryotes/Multicellular.")

    classified["mass_g"] = classified["mass_kg"] * config.KG_TO_GRAM
    classified["power_density_w_per_kg"] = classified["erd_wkg"]
    classified["power_density_w_per_g"] = classified["erd_wkg"] / config.KG_TO_GRAM
    classified["color"] = classified["segment"].map(
        {spec.label: spec.color for spec in BIOLOGY_SEGMENTS}
    )
    classified["data_source"] = VON_DUIN_LABEL
    return classified.reset_index(drop=True)


def combined_biology_table(path: Path | None = None) -> pd.DataFrame:
    """Processed biology table for plotting and CSV export."""
    return load_von_duin_erd_table(path)


def segment_summary(table: pd.DataFrame) -> pd.DataFrame:
    return (
        table.groupby("segment")
        .size()
        .reset_index(name="count")
        .sort_values("segment")
    )
