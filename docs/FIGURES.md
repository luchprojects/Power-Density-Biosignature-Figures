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

- Chaisson (2003/2011) living envelope: 0.1–10 W·kg⁻¹ band.
- Chaisson (2001) benchmarks: Sun, human, society.
- van Duin (2024) stability boundary: 10⁵ W·kg⁻¹.

**Code**

- Mode: `"unified"` in `plotter.create_domain_figure()`
- Draw order: YSO (background) → compact (mid) → biology diamonds (foreground)
- No error bars on this panel.

---

## 2. `figure_biology.pdf`

**Purpose:** Zoom on biological systems — van Duin (2024) empirical ERD by segment.

**Data:** Same biology table as unified; processed CSV: `processed/processed_von_duin_biology.csv`.

**Math:** Φ_m = ERD_wkg directly from MOESM1 Section I (already W·kg⁻¹).

**Segments:** Prokaryotes, Eukaryotes, Multicellular — filled circles (no marker outline).

**Overlays:** Chaisson envelope + benchmarks; van Duin 10⁵ W·kg⁻¹ line.

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
- Uncertainties: `data/compact/dubus_2018_wd_uncertainties.csv` (parsed from Dubus et al. 2018 A&A Tables A.2–A.3).

**Math**

- Horizontal: M₁ ± σ from Dubus.
- Vertical: asymmetric 68% MC Ṁ interval propagated to Φ_m at fixed η (consistent with plotted point).

**Code:** `create_domain_figure(mode="wd_uncertainties")` → `_plot_wd_dubus_uncertainties()`; `physics_engine.attach_dubus_wd_uncertainties()`.

---

## Processed outputs (after `main.py`)

| File | Contents |
|------|----------|
| `processed/processed_compact_results.csv` | All compact tracks + Dubus uncertainty columns |
| `processed/processed_yso_results.csv` | YSO Φ_m, masses, L_acc |
| `processed/processed_von_duin_biology.csv` | Biology scatter ready to plot |
| `processed/data_tracking_ledger.csv` | Figure ↔ data ↔ physics audit trail |
| `processed/provenance_manifest.json` | Run metadata and counts |

---

## Configuration

All colors, axis limits, and paths: **`config.py`**

Key constants: `POWER_DENSITY_UNIT = "W.kg-1"`, `DOMAIN_*_MASS`, `DOMAIN_*_RHO`, `COMPACT_CATEGORY_COLORS`.
