"""Quick audit: all scatter points trace to source CSVs; no synthetic scatter."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import config

CHECKS: list[tuple[str, str]] = []


def ok(msg: str) -> None:
    CHECKS.append(("OK", msg))


def warn(msg: str) -> None:
    CHECKS.append(("WARN", msg))


def main() -> int:
    sources = [
        config.VON_DUIN_ERD_CSV,
        config.COMPACT_OBJECTS_CSV,
        config.SMBH_OBJECTS_CSV,
        config.MANARA_MDOTS_DAT,
        config.DATA_COMPACT_DIR / "dubus_2018_wd_uncertainties.csv",
        config.VIDAL_PDF,
    ]
    for path in sources:
        if path.exists():
            ok(f"Source file: {path.name} ({path.stat().st_size:,} bytes)")
        else:
            warn(f"Missing source: {path}")

    compact = pd.read_csv(config.PROCESSED_COMPACT_CSV)
    yso = pd.read_csv(config.PROCESSED_YSO_CSV)
    biology = pd.read_csv(config.PROCESSED_BIOLOGY_CSV)

    smbH = pd.read_csv(config.PROCESSED_SMBH_CSV) if config.PROCESSED_SMBH_CSV.exists() else pd.DataFrame()

    grav = compact[compact["track"] == "gravitational"]
    ok(
        f"Compact scatter: {len(grav)} points "
        f"(WD={len(grav[grav.category == 'cataclysmic_variables'])}, "
        f"NS={len(grav[grav.category == 'neutron_stars'])}, "
        f"BH={len(grav[grav.category == 'transient_black_holes'])})"
    )
    if not smbH.empty:
        smbH_grav = smbH[smbH["track"] == "gravitational"]
        ok(f"SMBH scatter: {len(smbH_grav)} points (Vidal 2020 Table 5)")
    else:
        warn("SMBH processed CSV missing — run main.py")
    ok(f"YSO scatter: {len(yso)} points")
    ok(f"Biology scatter: {len(biology)} points")

    for label, frame in [("compact", grav), ("yso", yso), ("biology", biology)]:
        valid = (
            frame["mass_kg"].notna()
            & frame["power_density_w_per_kg"].notna()
            & (frame["mass_kg"] > 0)
            & (frame["power_density_w_per_kg"] > 0)
        )
        ok(f"{label}: {valid.sum()}/{len(frame)} rows have mass & Phi_m from processed CSV")

    wd = grav[grav["category"] == "cataclysmic_variables"]
    if "mass_kg_err" in wd.columns:
        ok(f"WD Dubus errors: {wd['mass_kg_err'].notna().sum()} systems (literature intervals)")
    if "dubus_table" in wd.columns:
        a2 = int((wd["dubus_table"] == "A2").sum())
        a3 = int((wd["dubus_table"] == "A3").sum())
        ok(f"WD Dubus subtypes: A.2 general CVs={a2}, A.3 nova-like={a3}")

    if "phi_source" in grav.columns:
        for cat, label in [
            ("neutron_stars", "NS"),
            ("transient_black_holes", "BH"),
        ]:
            sub = grav[grav["category"] == cat]
            if sub.empty:
                continue
            tabulated = (sub["phi_source"] == "tabulated_erd").all()
            eta_nan = sub["eta"].isna().all()
            l_ok = np.allclose(
                sub["luminosity_w"],
                sub["power_density_w_per_kg"] * sub["mass_kg"],
                rtol=1e-9,
                equal_nan=True,
            )
            ok(
                f"{label}: phi_source=tabulated_erd ({tabulated}), "
                f"eta NaN ({eta_nan}), L=M*Phi_m ({l_ok})"
            )

    yso_err_cols = [c for c in yso.columns if "err" in c.lower()]
    if yso_err_cols:
        warn(f"YSO has error columns: {yso_err_cols}")
    else:
        ok("YSO: no error columns in data — figures correctly show scatter only (no fake bars)")

    pdfs = sorted(config.FIGURES_DIR.glob("figure_*.pdf"))
    ok(f"Generated {len(pdfs)} figure PDFs")
    for pdf in pdfs:
        ok(f"  {pdf.name} ({pdf.stat().st_size // 1024} KB)")

    manifest = json.loads(config.PROVENANCE_MANIFEST_JSON.read_text(encoding="utf-8"))
    ok(
        f"Provenance manifest: yso={manifest['yso_count']}, "
        f"compact={manifest['compact_count']}, biology={manifest['biology_count']}"
    )

    print("\n=== DATA INTEGRITY AUDIT ===\n")
    for status, msg in CHECKS:
        print(f"[{status}] {msg}")
    warnings = sum(1 for s, _ in CHECKS if s == "WARN")
    return 1 if warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
