# Power Density as a Biosignature

Publication pipeline for **mass vs. power density** (Φ_m in W·kg⁻¹). One command rebuilds all figures from source data.

## Quick start (for Clem)

```powershell
cd "Power Density as a Biosignature"
pip install -r requirements.txt
python main.py
```

**What you get**

| Folder | Contents |
|--------|----------|
| `figures/` | Five PDF figures (main deliverables) |
| `processed/` | Computed CSVs (SI units), provenance manifest, audit ledger |
| `docs/` | PI Word guide + technical figure reference (Markdown) |
| `data/` | Raw source tables only (do not edit unless updating sources) |

PI-readable Word summary: `docs/Figure_Dataset_Reference_Analysis.docx`

Verify data integrity: `python scripts/verify_data_integrity.py`

---

## Folder layout

```
Power Density as a Biosignature/
├── main.py              ← run this
├── requirements.txt
├── README.md
│
├── src/                 Python pipeline (you rarely need to open this)
│   ├── config.py        paths, units, colors
│   ├── data_loader.py   ingest CSV / Manara / Vidal tables
│   ├── physics_engine.py
│   ├── plotter.py       all figure rendering
│   ├── von_duin_biology.py
│   ├── dubus_wd_uncertainties.py
│   └── provenance.py
│
├── data/                ★ raw inputs
│   ├── biology/         van Duin (2024) MOESM1 ERD table
│   ├── compact/         WDs, NSs, BHs + Dubus uncertainty cache + SMBH Table 5 cache
│   └── yso/             Manara (2022) PPVII compilation
│
├── figures/             ★ generated PDFs
├── processed/           ★ generated tables + manifest
├── docs/                ★ Word guide + FIGURES.md
├── scripts/             doc builder + integrity check
├── references/          Vidal (2020) source PDF
└── manuscript/          paper draft (not used by pipeline)
```

---

## Active figures (5)

| PDF | Description |
|-----|-------------|
| `figure_unified_master.pdf` | Full continuum: biology + YSO + compact + SMBH |
| `figure_biology.pdf` | Biology zoom (van Duin ERD) |
| `figure_compact_objects.pdf` | WDs (with Dubus uncertainties), NSs, BHs |
| `figure_wd_dubus_uncertainties.pdf` | WDs with Dubus (2018) error bars |
| `figure_smbh_seyfert1.pdf` | Seyfert 1 SMBHs zoom (same cohort as unified master) |

See **`docs/FIGURES.md`** for equations, file paths, and code entry points.

---

## Core equation

\[
\Phi_m = \frac{L}{M} \quad [\mathrm{W\,kg^{-1}}]
\]

Mass in **kg**; axis labels on all figures use SI W·kg⁻¹. All `processed/*.csv` tables use SI only (kg, W, W·kg⁻¹). The unified master export is `processed/power_density_si.csv`.

---

## Data sources (raw)

| Domain | File |
|--------|------|
| Biology | `data/biology/von_duin_2024_erd_moesm1.csv` |
| YSO | `data/yso/manara_2022_ppvii.tsv` → builds `data/yso/mdots_forclement.dat` |
| Compact | `data/compact/Power density data.csv` |
| WD uncertainties | `data/compact/dubus_2018_wd_uncertainties.csv` |
| SMBH (Table 5) | `data/compact/vidal_2020_table5_smbh_seyfert1.csv` |

Every scatter point comes from these tables or the van Duin stability reference line — nothing is hand-placed.

**Default:** `python main.py` reads committed CSVs. To rebuild compact/YSO/SMBH inputs from the Vidal PDF or Manara TSV, use `python main.py --rebuild-data`.

NS/BH Φ_m uses **tabulated ERD** from Vidal (2020) with Clem's g/kg correction (÷1000 on Tables 3–4). WDs use **η = 0.007** nuclear fusion efficiency computed from Ṁ. SMBHs use **η = 0.057** thin-disc ISCO efficiency computed from Ṁ (Frank et al. 2002). Processed CSV includes `phi_source` marking tabulated vs computed values.
