# Power Density as a Biosignature

Generate two publication figures: mass vs. power density (Φ_m in W·kg⁻¹).

## Quick start

```powershell
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
├── main.py              ← run this
├── requirements.txt
├── src/                 pipeline code
├── data/                raw input tables (do not edit unless updating sources)
└── figures/             generated PDFs
```

## Data inputs

| Domain | File |
|--------|------|
| Biology | `data/biology/von_duin_2024_erd_moesm1.csv` |
| YSO | `data/yso/mdots_forclement.dat` |
| Compact (WD / NS / BH) | `data/compact/Power density data.csv` |
| WD uncertainties | `data/compact/dubus_2018_wd_uncertainties.csv` |
| SMBH | `data/compact/vidal_2020_table5_smbh_seyfert1.csv` (unified master only) |

## Equation

Φ_m = L / M  [W·kg⁻¹], with mass in kg and luminosity in W.
