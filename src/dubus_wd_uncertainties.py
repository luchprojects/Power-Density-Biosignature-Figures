"""
Dubus et al. (2018) A&A 617, A26 — WD / CV uncertainty tables (A.2 + A.3).

Statistical 68% Monte Carlo intervals on mass transfer rate; symmetric M1 errors.
Source: https://doi.org/10.1051/0004-6361/201833372
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

import config

DUBUS_2018_DOI = "10.1051/0004-6361/201833372"
DUBUS_TABLE_URLS: tuple[str, ...] = (
    "https://www.aanda.org/articles/aa/full_html/2018/09/aa33372-18/T2.html",
    "https://www.aanda.org/articles/aa/full_html/2018/09/aa33372-18/T3.html",
)
DUBUS_UNCERTAINTIES_CSV = config.DATA_COMPACT_DIR / "dubus_2018_wd_uncertainties.csv"
DUBUS_TABLE_A2 = "A2"
DUBUS_TABLE_A3 = "A3"
DUBUS_TABLE_KEYS: tuple[str, ...] = (DUBUS_TABLE_A2, DUBUS_TABLE_A3)

_MINUS_CHARS = "\u2212\u2013\u2014-"


def _normalize_unicode(text: str) -> str:
    return (
        text.strip()
        .replace("\u00b1", "+/-")
        .replace("\u00d7", "x")
        .replace("\u2212", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2299", "")
        .replace(" ", "")
    )


def _parse_mass_msun(value: object) -> tuple[float | None, float | None]:
    if pd.isna(value):
        return None, None
    text = _normalize_unicode(str(value))
    match = re.match(r"([\d.]+)\+/-([\d.]+)", text)
    if match:
        return float(match.group(1)), float(match.group(2))
    try:
        return float(text), None
    except ValueError:
        return None, None


def _parse_mdot_interval_g_s(value: object) -> tuple[float | None, float | None]:
    """Parse Dubus Ṁt column, e.g. '(0.6-1.5)x10^17' or '(0.6-1.5)x1017'."""
    if pd.isna(value):
        return None, None
    text = _normalize_unicode(str(value))
    match = re.match(
        rf"\(([\d.]+)[{_MINUS_CHARS}]([\d.]+)\)x10(?:\^)?(-?\d+)",
        text,
    )
    if not match:
        return None, None
    lo = float(match.group(1)) * (10.0 ** int(match.group(3)))
    hi = float(match.group(2)) * (10.0 ** int(match.group(3)))
    if lo > hi:
        lo, hi = hi, lo
    return lo, hi


def _fetch_dubus_tables() -> pd.DataFrame:
    records: list[dict[str, object]] = []
    table_keys = (DUBUS_TABLE_A2, DUBUS_TABLE_A3)
    for url, dubus_table in zip(DUBUS_TABLE_URLS, table_keys):
        table = pd.read_html(url)[0]
        object_col = table.columns[0]
        mass_col = ("M1", "M⊙") if ("M1", "M⊙") in table.columns else table.columns[2]
        mdot_col = ("Ṁt", "g s−1") if ("Ṁt", "g s−1") in table.columns else table.columns[-1]

        for _, row in table.iterrows():
            name = str(row[object_col]).strip()
            if not name or name.lower() == "object" or name.lower().startswith("references"):
                continue
            mass_msun, mass_msun_err = _parse_mass_msun(row[mass_col])
            mdot_lo, mdot_hi = _parse_mdot_interval_g_s(row[mdot_col])
            if mass_msun is None:
                continue
            records.append(
                {
                    "name": name,
                    "mass_msun_dubus": mass_msun,
                    "mass_msun_err": mass_msun_err,
                    "mdot_g_s_lo": mdot_lo,
                    "mdot_g_s_hi": mdot_hi,
                    "dubus_table": dubus_table,
                    "source": "Dubus+2018_AA617_A26",
                }
            )
    frame = pd.DataFrame.from_records(records)
    if frame.empty:
        raise ValueError("No Dubus 2018 WD uncertainty rows parsed.")
    return frame.drop_duplicates(subset=["name"], keep="first").reset_index(drop=True)


def build_dubus_uncertainties_csv(output_path: Path | None = None) -> Path:
    target = output_path or DUBUS_UNCERTAINTIES_CSV
    target.parent.mkdir(parents=True, exist_ok=True)
    frame = _fetch_dubus_tables()
    frame.to_csv(target, index=False)
    return target


def load_dubus_wd_uncertainties(
    path: Path | None = None,
    *,
    rebuild: bool = False,
) -> pd.DataFrame:
    """Load Dubus (2018) WD uncertainty table, fetching from A&A if needed."""
    csv_path = path or DUBUS_UNCERTAINTIES_CSV
    needs_rebuild = rebuild or not csv_path.exists()
    if csv_path.exists() and not needs_rebuild:
        header = pd.read_csv(csv_path, nrows=0).columns
        if "dubus_table" not in header:
            needs_rebuild = True
    if needs_rebuild:
        build_dubus_uncertainties_csv(csv_path)
    frame = pd.read_csv(csv_path)
    required = {"name", "mass_msun_err", "mdot_g_s_lo", "mdot_g_s_hi", "dubus_table"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Dubus uncertainty CSV missing columns: {missing}")
    return frame


if __name__ == "__main__":
    out = build_dubus_uncertainties_csv()
    loaded = load_dubus_wd_uncertainties(out)
    print(f"Wrote {len(loaded)} WD uncertainty rows -> {out}")
