# Power Density as a Universal Biosignature

This repository contains the data and script used to generate power density plots (mass vs. power density (Φ_m in W·kg⁻¹)), in the paper:
**Power Density as a Universal Biosignature: An Application to the Stellivore Hypothesis** by Clément Vidal & Luciano Kadian (to appear). 


## Quick start

```
cd "Power Density as a Biosignature"
pip install -r requirements.txt
python main.py
```

Outputs land in **`figures/`** as publication-ready vector PDFs:

| File | Description |
|------|-------------|
| `figure_unified_master.pdf` | Biology + YSO + compact objects + SMBHs |
| `figure_compact_objects.pdf` | White dwarfs (Dubus uncertainties), neutron stars, black holes |

## Layout

```
Power Density as a Biosignature/
├── main.py              ← main script to run 
├── requirements.txt     package requirements
├── src/                 pipeline code
├── data/                raw input tables (do not edit unless updating sources)
└── figures/             generated PDFs
```

## Data inputs

| Domain | File |
|--------|------|
| Biology | `data/biology/von_duin_2024_erd_moesm1.csv` |
| YSO | `data/yso/Manara_et_al_2022.dat` |
| Compact (WD / NS / BH) | `data/compact/Power density data.csv` |
| WD uncertainties | `data/compact/dubus_2018_wd_uncertainties.csv` |
| SMBH | `data/compact/meyer_hofmeister_meyer_2011.csv` (unified master only) |


