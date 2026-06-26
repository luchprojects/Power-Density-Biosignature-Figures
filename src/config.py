"""
Physical, astronomical, and thermodynamic constants for the Power Density pipeline.

All publication figures and processed tables use SI: kg, W, W.kg-1 (Phi_m = L/M).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Project paths (canonical workspace locations)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_BIOLOGY_DIR = DATA_DIR / "biology"
DATA_COMPACT_DIR = DATA_DIR / "compact"
DATA_YSO_DIR = DATA_DIR / "yso"
REFERENCES_DIR = PROJECT_ROOT / "references"
MANUSCRIPT_DIR = PROJECT_ROOT / "manuscript"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
FIGURES_DIR = PROJECT_ROOT / "figures"
PROCESSED_DIR = PROJECT_ROOT / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"

COMPACT_OBJECTS_CSV = DATA_COMPACT_DIR / "Power density data.csv"
SMBH_OBJECTS_CSV = DATA_COMPACT_DIR / "vidal_2020_table5_smbh_seyfert1.csv"
MANARA_MDOTS_DAT = DATA_YSO_DIR / "mdots_forclement.dat"
MANARA_COMPILATION_TSV = DATA_YSO_DIR / "manara_2022_ppvii.tsv"
LEGACY_WD_TABLE = DATA_COMPACT_DIR / "Power density data  - Table 1 accreting WDs.csv"
VIDAL_PDF = REFERENCES_DIR / (
    "Vidal-2020-ERD as a technosignature - case for stellivores V1.5.pdf"
)

# ---------------------------------------------------------------------------
# Fundamental physical constants (SI)
# ---------------------------------------------------------------------------

GRAVITATIONAL_CONSTANT = 6.67430e-11  # m^3 kg^-1 s^-2
SPEED_OF_LIGHT = 2.99792458e8  # m s^-1
ERG_TO_JOULE = 1.0e-7

# ---------------------------------------------------------------------------
# Astronomical unit conversions (SI)
# ---------------------------------------------------------------------------

SOLAR_MASS = 1.98847e30  # kg
SOLAR_RADIUS = 6.957e8  # m
SOLAR_LUMINOSITY = 3.828e26  # W
SECONDS_PER_YEAR = 3.15576e7
SOLAR_MASS_PER_YEAR_TO_KG_PER_S = SOLAR_MASS / SECONDS_PER_YEAR
GRAM_TO_KG = 1.0e-3
KG_TO_GRAM = 1.0e3

# ---------------------------------------------------------------------------
# Accretion efficiencies
# ---------------------------------------------------------------------------

WHITE_DWARF_NUCLEAR_EFFICIENCY = 0.007
# WDs are plotted on the nuclear track: Phi_m = eta * Mdot * c^2 / M at eta = 0.007.
WHITE_DWARF_DISPLAY_TRACK = "nuclear"

# Thin-disc accretion onto a non-rotating (Schwarzschild) BH: binding energy at ISCO.
# Frank, King & Raine (2002) Accretion Power in Astrophysics, 3rd ed., Ch. 7 (~0.057 c^2).
SMBH_ACCRETION_EFFICIENCY = 0.057
DEFAULT_NEUTRON_STAR_RADIUS_M = 1.2e4
DEFAULT_STELLAR_MASS_BLACK_HOLE_RADIUS_SOLAR = 2.95e-5
DEFAULT_WHITE_DWARF_RADIUS_SOLAR = 0.011
WHITE_DWARF_RADIUS_MASS_EXPONENT = -1.0 / 3.0

# ---------------------------------------------------------------------------
# Literature reference overlays — one solid color per reference (all figures)
# ---------------------------------------------------------------------------

REFERENCE_LINE_STYLE = "-"
REFERENCE_LINE_WIDTH = 1.15
REFERENCE_LINE_ALPHA = 0.92

COLOR_REF_CHAISSON_SOCIETY = "#b45309"    # amber — modern society (Chaisson 2001, p. 139)
COLOR_REF_VAN_DUIN = "#4f46e5"            # indigo — dissipative ceiling (van Duin 2024)

# Chaisson (2001, Cosmic Evolution, p. 139) — modern society benchmark only
CHAISSON_2001_SOCIETY_W_PER_KG = 50.0

CHAISSON_SOCIETY_BENCHMARK_LABEL = r"Modern society (Chaisson 2001, p.~139)"

# Canonical SI display units — all publication figures use kg and W.kg-1 for Φ_m
MASS_UNIT = "kg"
POWER_DENSITY_UNIT = "W.kg-1"

# ---------------------------------------------------------------------------
# Dataset categories
# ---------------------------------------------------------------------------

CATEGORY_CATACLYSMIC_VARIABLES = "cataclysmic_variables"
CATEGORY_NEUTRON_STARS = "neutron_stars"
CATEGORY_TRANSIENT_BLACK_HOLES = "transient_black_holes"
CATEGORY_SUPERMASSIVE_BLACK_HOLES = "supermassive_black_holes"
CATEGORY_YOUNG_STELLAR_OBJECTS = "young_stellar_objects"

COMPACT_OBJECT_CATEGORIES: tuple[str, ...] = (
    CATEGORY_CATACLYSMIC_VARIABLES,
    CATEGORY_NEUTRON_STARS,
    CATEGORY_TRANSIENT_BLACK_HOLES,
)

CATEGORY_DISPLAY_NAMES: dict[str, str] = {
    CATEGORY_CATACLYSMIC_VARIABLES: "Cataclysmic Variables (White Dwarfs)",
    CATEGORY_NEUTRON_STARS: "Neutron Stars",
    CATEGORY_TRANSIENT_BLACK_HOLES: "Transient Black Holes",
    CATEGORY_SUPERMASSIVE_BLACK_HOLES: (
        r"Seyfert 1 SMBHs — Meyer-Hofmeister & Meyer (2011)"
    ),
}

# Universal empirical marker policy — solid filled circles
EMPIRICAL_MARKER_SHAPE = "o"
EMPIRICAL_MARKER_SIZE = 3.5
# Open/unfilled markers (Cataclysmic Variables on unified master): green border,
# transparent face. Edge ink is sparse, so the opacity sits higher than the dense
# solid-fill alpha used elsewhere.
EMPIRICAL_MARKER_EDGEWIDTH_UNFILLED = 0.8
EMPIRICAL_MARKER_ALPHA_UNFILLED = 0.8
# Sparse series (YSO, NS, BH, prok/euk biology) — drawn on top, stay readable
EMPIRICAL_MARKER_ALPHA = 0.85
# Dense clouds (738 multicellular, 130 WDs on unified) — translucent underlayers
EMPIRICAL_MARKER_ALPHA_DENSE = 0.22
PLOT_MARKER_SHAPE = EMPIRICAL_MARKER_SHAPE

# ---------------------------------------------------------------------------
# YSO control (Manara+2022; PI-preferred 2017 baseline references)
# ---------------------------------------------------------------------------

# Manara PPVII ref_xs tags mapping to the pristine 2017 control cohorts:
#   Alcala+14,17,19  ->  Alcalá et al. (2017) Lupus sample
#   Manara+16,17     ->  Manara et al. (2017) Upper Sco sample
YSO_PREFERRED_REFERENCE_MARKERS: tuple[str, ...] = (
    "Alcala+14,17,19",
    "Manara+16,17",
)

# Somers et al. (2020, ApJ 912, 40) SPOTS benchmark spot covering fraction.
SOMERS_SPOTS_BENCHMARK_COVERAGE = 0.17


@dataclass(frozen=True)
class YSOControlParameters:
    """Somers (2020) SPOTS mass-calibration parameters for YSO control sample."""

    spot_coverage_fraction: float = SOMERS_SPOTS_BENCHMARK_COVERAGE
    color: str = "#FBBF24"


YSO_CONTROL = YSOControlParameters()

# ---------------------------------------------------------------------------
# Master unified figure — NASA/STScI global log-log coordinates
# ---------------------------------------------------------------------------

PLOT_DPI = 300
MASTER_FIGURE_SIZE = (9.0, 6.5)
DOMAIN_FIGURE_SIZE = (7.2, 5.5)
PLOT_FONT_FAMILY = "serif"
PLOT_FONT_SERIF = ["Times New Roman", "DejaVu Serif", "serif"]
PLOT_FONT_SIZE = 11
PLOT_AXIS_LABEL_SIZE = 12
PLOT_TITLE_SIZE = 12
PLOT_LEGEND_SIZE = 9
PLOT_MARKER_SIZE = EMPIRICAL_MARKER_SIZE

# ---------------------------------------------------------------------------
# Geometric decoupling — three-layer scatter architecture (no alpha-blend masking)
# Background: filled YSO | Mid-ground: compact (open WD circles on unified, filled on compact panel)
# YSO and compact share GEOMETRIC_OBSERVATIONAL_CIRCLE_SIZE (filled dots, same s)
# ---------------------------------------------------------------------------

GEOMETRIC_DECOUPLING_ENABLED = True

GeometricLayerName = str  # "background" | "midground"

# Shared filled-circle size for YSO + compact observational cohorts
GEOMETRIC_OBSERVATIONAL_CIRCLE_SIZE = 40.0

# Unified master — YSO open rings on top; open WD circles underneath (dense CV cohort).
YSO_UNIFIED_MARKER_SIZE = 38.0
YSO_UNIFIED_RING_LINEWIDTH = 0.65
YSO_UNIFIED_RING_ALPHA = 0.9
YSO_UNIFIED_MARKER_ZORDER = 2.4

COMPACT_WD_UNIFIED_MARKER_SIZE = YSO_UNIFIED_MARKER_SIZE
BIOLOGY_SCATTER_ZORDER = 3


@dataclass(frozen=True)
class GeometricLayerSpec:
    marker: str
    size: float
    zorder: int
    alpha: float
    facecolor: str | None
    edgecolor: str | None
    linewidth: float


GEOMETRIC_LAYER_BACKGROUND = GeometricLayerSpec(
    marker="o",
    size=GEOMETRIC_OBSERVATIONAL_CIRCLE_SIZE,
    zorder=1,
    alpha=1.0,
    facecolor=None,
    edgecolor="none",
    linewidth=0.0,
)
GEOMETRIC_LAYER_MIDGROUND = GeometricLayerSpec(
    marker="o",
    size=GEOMETRIC_OBSERVATIONAL_CIRCLE_SIZE,
    zorder=2,
    alpha=0.9,
    facecolor=None,
    edgecolor="none",
    linewidth=0.0,
)

# Biology — filled circles on all figures (unified + biology panel)
GEOMETRIC_BIOLOGY_MARKER_UNIFIED = "o"
GEOMETRIC_BIOLOGY_MARKER_BIOLOGY_PANEL = "o"
GEOMETRIC_BIOLOGY_SIZE_UNIFIED = GEOMETRIC_OBSERVATIONAL_CIRCLE_SIZE
GEOMETRIC_BIOLOGY_SIZE_BIOLOGY_PANEL = GEOMETRIC_OBSERVATIONAL_CIRCLE_SIZE

GEOMETRIC_LAYERS: dict[str, GeometricLayerSpec] = {
    "background": GEOMETRIC_LAYER_BACKGROUND,
    "midground": GEOMETRIC_LAYER_MIDGROUND,
}
# Optional error-bar styling when datasets provide explicit uncertainty columns
ERRORBAR_ECOLOR = "#94a3b8"
ERRORBAR_ELINEWIDTH = 0.4
ERRORBAR_CAPSIZE = 1
ERRORBAR_ALPHA = 0.4
# Delicate error bars on zoomed observational panels only
ERRORBAR_ELINEWIDTH_ZOOM = 0.3
ERRORBAR_CAPSIZE_ZOOM = 0
ERRORBAR_ALPHA_ZOOM = 0.3
ERRORBAR_MARKERSIZE = EMPIRICAL_MARKER_SIZE
# Log-axis minor ticks — fractional decade substeps 0.2 … 0.9 (base 10)
LOG_MINOR_SUBS: tuple[float, ...] = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
VAN_DUIN_DISSIPATIVE_LIMIT_W_PER_KG = 1.0e5
VAN_DUIN_DISSIPATIVE_LIMIT_W_PER_G = VAN_DUIN_DISSIPATIVE_LIMIT_W_PER_KG / KG_TO_GRAM  # legacy gram display
VAN_DUIN_LINE_WIDTH = REFERENCE_LINE_WIDTH
VAN_DUIN_LINE_COLOR = COLOR_REF_VAN_DUIN
VAN_DUIN_LINE_ALPHA = REFERENCE_LINE_ALPHA
VAN_DUIN_LINE_STYLE = REFERENCE_LINE_STYLE
VAN_DUIN_ZORDER = 4
LEGEND_ZORDER = 5
LEGEND_FRAMEALPHA = 1.0
# Per-figure legend anchors — collision-free journal layout
LEGEND_LOC_UPPER_RIGHT = "upper right"
LEGEND_LOC_LOWER_LEFT = "lower left"
LEGEND_LOC_LOWER_RIGHT = "lower right"
LEGEND_LAYOUT: dict[str, dict[str, object]] = {
    "unified": {"loc": LEGEND_LOC_UPPER_RIGHT},
    "biology": {"loc": LEGEND_LOC_LOWER_LEFT},
    "compact": {"loc": LEGEND_LOC_UPPER_RIGHT},
    "wd_uncertainties": {"loc": LEGEND_LOC_UPPER_RIGHT},
    "smbh": {"loc": LEGEND_LOC_UPPER_RIGHT},
}
PLOT_GRID_COLOR = "#cbd5e1"
PLOT_GRID_ALPHA_MAJOR = 0.30
PLOT_GRID_ALPHA_MINOR = 0.15

MASTER_MASS_MIN_KG = 1.0e-25
MASTER_MASS_MAX_KG = 1.0e47
MASTER_RHO_MIN_WKG = 1.0e-9  # YSO accretion extends to ~2e-8 W·kg⁻¹ (Manara 2022)
MASTER_RHO_MAX_WKG = 1.0e11
# Log-axis bounds in SI (kg, W.kg-1)

FIGURE_UNIFIED_MASTER_PDF = FIGURES_DIR / "figure_unified_master.pdf"

FIGURE_BIOLOGY_PDF = FIGURES_DIR / "figure_biology.pdf"
FIGURE_COMPACT_OBJECTS_PDF = FIGURES_DIR / "figure_compact_objects.pdf"
FIGURE_COMPACT_PDF = FIGURE_COMPACT_OBJECTS_PDF  # backward-compatible alias
FIGURE_WD_DUBUS_UNCERTAINTIES_PDF = FIGURES_DIR / "figure_wd_dubus_uncertainties.pdf"
FIGURE_SMBH_PDF = FIGURES_DIR / "figure_smbh_seyfert1.pdf"
FIGURE_BIOLOGY_TRENDS_PDF = FIGURES_DIR / "figure_biology_trends.pdf"
FIGURE_COMPACT_OBJECTS_TRENDS_PDF = FIGURES_DIR / "figure_compact_objects_trends.pdf"
FIGURE_UNIFIED_MASTER_TRENDS_PDF = FIGURES_DIR / "figure_unified_master_trends.pdf"
FIGURE_REFERENCE_DOC = DOCS_DIR / "Figure_Dataset_Reference_Analysis.docx"

# Power-law trend-line styling (OLS fits in log10-log10 space; see scripts/figure_trends.py).
# Distinct from the solid literature reference lines so fits read as derived, not measured.
TREND_FIT_LINESTYLE_GROUP = "--"      # per-group (segment / category) fit
TREND_FIT_LINESTYLE_OVERALL = "-."    # global fit across all points
TREND_FIT_LINEWIDTH_GROUP = 1.3
TREND_FIT_LINEWIDTH_OVERALL = 1.8
TREND_FIT_ALPHA = 0.9
TREND_OVERALL_COLOR = "#1a1a2e"       # neutral dark — domain-agnostic global fit
TREND_FIT_SAMPLE_COUNT = 100

# Unified-master cross-domain trend lines — distinct from the empirical scatter palette
# (YSO/WD/NS/BH + biology segments) and the literature reference lines.
TREND_ALL_SYSTEMS_COLOR = "#111827"   # near-black — headline cross-domain fit (dash-dot, heavy)
TREND_ALL_BIOLOGY_COLOR = "#7e22ce"   # violet — biology overall fit (dashed)
TREND_ALL_COMPACT_COLOR = "#be123c"   # crimson — compact overall fit (dashed)

PROCESSED_COMPACT_CSV = PROCESSED_DIR / "processed_compact_results.csv"
PROCESSED_SMBH_CSV = PROCESSED_DIR / "processed_smbh_results.csv"
PROCESSED_YSO_CSV = PROCESSED_DIR / "processed_yso_results.csv"
VON_DUIN_ERD_CSV = DATA_BIOLOGY_DIR / "von_duin_2024_erd_moesm1.csv"
PROCESSED_BIOLOGY_CSV = PROCESSED_DIR / "processed_von_duin_biology.csv"
PROCESSED_SI_CSV = PROCESSED_DIR / "power_density_si.csv"
DATA_TRACKING_LEDGER_CSV = PROCESSED_DIR / "data_tracking_ledger.csv"
PROVENANCE_MANIFEST_JSON = PROCESSED_DIR / "provenance_manifest.json"

# ApJ axis labels — SI units on all publication figures (always W·kg⁻¹ for Φ_m)
AXIS_LABEL_MASS = rf"Mass $[\mathrm{{{MASS_UNIT}}}]$"
AXIS_LABEL_POWER_DENSITY = r"Power Density $\Phi_m$ ($\mathrm{W \cdot kg^{-1}}$)"
VAN_DUIN_LEGEND_LABEL = r"Stability Boundary (van Duin 2024)"

MASTER_FIGURE_PATH = FIGURE_UNIFIED_MASTER_PDF
MASTER_FIGURE_PDF = FIGURE_UNIFIED_MASTER_PDF

# Zoomed axes for standalone domain figures (global axes reserved for unified master)
DOMAIN_BIOLOGY_MASS = (1.0e-23, 1.0e33)
DOMAIN_BIOLOGY_RHO = (1.0e-12, 1.0e6)  # headroom above van Duin + mantis-shrimp burst outlier (~7e5)
DOMAIN_YSO_MASS = (1.0e27, 1.0e32)
DOMAIN_YSO_RHO = (1.0e-8, 1.0e-3)  # full Manara sample (~2e-8–7e-4 W·kg⁻¹)
DOMAIN_COMPACT_MASS = (1.0e28, 1.0e32)
DOMAIN_COMPACT_RHO = (1.0e-8, 1.0e4)  # WD Dubus error bars extend to ~3e-7 W·kg⁻¹
DOMAIN_SMBH_MASS = (1.0e34, 1.0e39)
DOMAIN_SMBH_RHO = (1.0e-2, 1.0e1)  # Phi_m from eta=0.057 thin-disc accretion (~0.02–1.5 W·kg⁻¹)

# ApJ defense-grade colorblind-safe empirical palette
# Empirical scatter — standard distinct colors (identical across all figures & reference tables)
COLOR_YSO_CONTROL = "#FBBF24"         # yellow — Young Stellar Objects (Manara 2022)
COLOR_WHITE_DWARFS = "#22C55E"        # green — general CVs (Dubus Table A.2)
COLOR_WD_NOVA_LIKE = "#D946EF"        # fuchsia — nova-like CVs (Dubus Table A.3); distinct from A.2 green
COLOR_NEUTRON_STARS = "#2563EB"       # blue — Neutron Stars
COLOR_BLACK_HOLES = "#DC2626"         # red — Transient Black Holes
COLOR_SUPERMASSIVE_BLACK_HOLES = "#9333EA"  # violet — Seyfert 1 SMBHs (Vidal Table 5)

# Biology segment scatter colors (van Duin 2024 MOESM1 — green / brown / blue earth tones)
COLOR_PROKARYOTES = "#946B3A"         # earth brown — prokaryotes (van Duin 2024)
COLOR_EUKARYOTES = "#527A96"          # slate blue — eukaryotes
COLOR_MULTICELLULAR = "#588B5C"       # forest green — multicellular (dominant cloud)

EMPIRICAL_COLOR_REGISTRY: dict[str, tuple[str, str]] = {
    "young_stellar_objects": (COLOR_YSO_CONTROL, "Young Stellar Objects (Manara et al. 2022)"),
    "cataclysmic_variables": (COLOR_WHITE_DWARFS, "Cataclysmic Variables (White Dwarfs)"),
    "neutron_stars": (COLOR_NEUTRON_STARS, "Neutron Stars"),
    "transient_black_holes": (COLOR_BLACK_HOLES, "Transient Black Holes"),
    "supermassive_black_holes": (
        COLOR_SUPERMASSIVE_BLACK_HOLES,
        "Seyfert 1 SMBHs (Meyer-Hofmeister & Meyer 2011)",
    ),
}

COMPACT_CATEGORY_COLORS: dict[str, str] = {
    CATEGORY_CATACLYSMIC_VARIABLES: COLOR_WHITE_DWARFS,
    CATEGORY_NEUTRON_STARS: COLOR_NEUTRON_STARS,
    CATEGORY_TRANSIENT_BLACK_HOLES: COLOR_BLACK_HOLES,
    CATEGORY_SUPERMASSIVE_BLACK_HOLES: COLOR_SUPERMASSIVE_BLACK_HOLES,
}

DUBUS_WD_SUBTYPE_COLORS: dict[str, str] = {
    "A2": COLOR_WHITE_DWARFS,
    "A3": COLOR_WD_NOVA_LIKE,
}

DUBUS_TABLE_KEYS: tuple[str, ...] = ("A2", "A3")

DUBUS_WD_SUBTYPE_LABELS: dict[str, str] = {
    "A2": "Cataclysmic Variables — Dubus et al. (2018) Table A.2",
    "A3": "Nova-like CVs — Dubus et al. (2018) Table A.3",
}
