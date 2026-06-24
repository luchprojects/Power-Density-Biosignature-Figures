# Figure reference — data, math, and code

All figures share ApJ-style log–log axes unless noted. Power density is always **Φ_m in W·kg⁻¹**; mass is **kg**.

**Run everything:** `python main.py`  
**Plotting entry point:** `plotter.save_all_figures()` → calls `plotter.create_domain_figure(mode=...)` for each panel.

---

## 1. `figure_unified_master.pdf`

**Purpose:** Single overview of the full power-density continuum — biology, YSOs, and compact accretors.

**Data sources**

| Layer | Source file | Loader |
|-------|-------------|--------|
| Biology | `data/biology/von_duin_2024_erd_moesm1.csv` | `von_duin_biology.combined_biology_table()` |
| YSO | `data/yso/mdots_forclement.dat` (built from Manara TSV) | `data_loader.load_mdots_forclement()` |
| Compact | `data/compact/Power density data.csv` | `data_loader.load_compact_objects()` |

**Math**

- Biology / compact (when ERD tabulated): Φ_m from reported ERD (W·kg⁻¹).
- YSO: Φ_m = L_acc / M_star with L_acc from log L_acc and M_star from Somers (2020) SPOTS-inflated Baraffe+2015 mass.
- Compact (gravitational track): η_grav = GM/(Rc²), L = η Ṁ c², Φ_m = L/M; uses tabulated ERD when present.

**Literature overlays (lines only, not scatter)**

- Chaisson (2001) benchmark: modern society only (~50 W·kg⁻¹).
- van Duin (2024) stability boundary: 10⁵ W·kg⁻¹.

**Code**

- Mode: `"unified"` in `plotter.create_domain_figure()`
- Draw order: compact (mid) → YSO rings → biology circles on top. WDs: **green** = Dubus Table A.2 (general CVs), **fuchsia** = Table A.3 (nova-like); YSO: open yellow rings.
- No error bars on this panel (WD uncertainties: `figure_wd_dubus_uncertainties.pdf`).

---

## 2. `figure_biology.pdf`

**Purpose:** Zoom on biological systems — van Duin (2024) empirical ERD by segment.

**Data:** Same biology table as unified; processed CSV: `processed/processed_von_duin_biology.csv`.

**Math:** Φ_m = ERD_wkg directly from MOESM1 Section I (already W·kg⁻¹).

**Segments:** Prokaryotes (brown), Eukaryotes (slate blue), Multicellular (forest green) — filled circles.

**Overlays:** Chaisson (2001) modern society benchmark; van Duin 10⁵ W·kg⁻¹ line.

**Code:** `create_domain_figure(mode="biology")` → `_plot_von_duin_biology_scatter()`.

---

## 3. `figure_yso.pdf`

**Purpose:** Abiotic control sample — accreting young stars only.

**Data:** Manara et al. (2022) PPVII; filtered to Alcalá+2017 / Manara+2017 references; masses SPOTS-corrected.

**Math**

\[
\Phi_m = \frac{L_{\mathrm{acc}}}{M_\star}, \quad L_{\mathrm{acc}} = 10^{\log L_{\mathrm{acc}}} \times L_\odot
\]

**Code:** `create_domain_figure(mode="yso")` → `_plot_yso_scatter()`; `physics_engine.compute_yso_power_density()`.

---

## 4. `figure_compact_objects.pdf`

**Purpose:** Accreting compact objects only — WDs, neutron stars, transient BHs.

**Data:** `data/compact/Power density data.csv`

| Population | n | Primary literature (via Vidal 2020 tables) |
|------------|---|---------------------------------------------|
| Cataclysmic variables (WDs) | 130 | Dubus et al. (2018) |
| Neutron stars | 30 | Galloway et al. (2008) |
| Transient BHs | 19 | Coriat et al. (2012) |

**Math (gravitational track plotted)**

\[
\eta_{\mathrm{grav}} = \frac{GM}{Rc^2}, \quad L = \eta\,\dot M\, c^2, \quad \Phi_m = \frac{L}{M}
\]

Tabulated ERD overrides computed Φ_m when both Ṁ and ERD exist.

**Code:** `create_domain_figure(mode="compact")` → `_plot_compact_scatter()`; WDs at full opacity on this panel.

---

## 5. `figure_wd_dubus_uncertainties.pdf`

**Purpose:** WD-only panel with literature uncertainty bars (separate from main continuum).

**Data**

- Positions: same as compact WD rows.
- Uncertainties: `data/compact/dubus_2018_wd_uncertainties.csv` (Dubus et al. 2018 A&A Tables **A.2** + **A.3**; `dubus_table` column tags each system).
- **Colors:** green = Table A.2 general CVs (110); fuchsia = Table A.3 nova-like CVs (20).

**Math**

- Horizontal: M₁ ± σ from Dubus.
- Vertical: asymmetric 68% MC Ṁ interval propagated to Φ_m at fixed η (consistent with plotted point).

**Code:** `create_domain_figure(mode="wd_uncertainties")` → `_plot_wd_dubus_uncertainties()`; `physics_engine.attach_dubus_wd_uncertainties()`.

---

## 6. `figure_smbh_seyfert1.pdf`

**Purpose:** Separate test panel for Seyfert 1 supermassive black holes — **not** on the unified master.

**Data**

| Field | Source |
|-------|--------|
| 16 Seyfert 1 systems | Vidal (2020) Table 5, parsed from `references/Vidal-2020-ERD…pdf` |
| Cached CSV | `data/compact/vidal_2020_table5_smbh_seyfert1.csv` |
| Original literature | Meyer-Hofmeister & Meyer (2011) |

**Math**

- M_BH, Ṁ, and tabulated ERD (erg·s⁻¹·g⁻¹) from Vidal Table 5 (η = 0.1).
- Φ_m uses tabulated ERD when present; Schwarzschild radius for the gravitational track.

**Overlays:** Chaisson modern society benchmark only (van Duin line off-scale on this zoom).

**Code:** `load_supermassive_black_holes()` → `create_domain_figure(mode="smbh")` → `_plot_smbh_scatter()`.

---

## Processed outputs (after `main.py`)

| File | Contents |
|------|----------|
| `processed/processed_compact_results.csv` | All compact tracks + Dubus uncertainty columns; `phi_source` marks tabulated ERD vs Ṁ-derived Φ_m |
| `processed/processed_smbh_results.csv` | Seyfert 1 SMBH Φ_m (Vidal Table 5) |
| `processed/processed_yso_results.csv` | YSO Φ_m, masses, L_acc |
| `processed/processed_von_duin_biology.csv` | Biology scatter ready to plot |
| `processed/data_tracking_ledger.csv` | Figure ↔ data ↔ physics audit trail |
| `processed/provenance_manifest.json` | Run metadata and counts |

---

## Configuration

All colors, axis limits, and paths: **`config.py`**

Key constants: `POWER_DENSITY_UNIT = "W.kg-1"`, `DOMAIN_*_MASS`, `DOMAIN_*_RHO`, `DUBUS_WD_SUBTYPE_COLORS`, biology segment colors (`COLOR_PROKARYOTES`, `COLOR_EUKARYOTES`, `COLOR_MULTICELLULAR`).
