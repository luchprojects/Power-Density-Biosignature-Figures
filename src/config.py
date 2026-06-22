"""
Physical, astronomical, and thermodynamic constants for the Power Density pipeline.

All publication figures display power density in SI as W.kg-1 (Φ_m = L/M in kg).
Internal processed tables may retain legacy W g^-1 columns for reproducibility;
plotting always converts to and labels W.kg-1.
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
MANARA_MDOTS_DAT = DATA_YSO_DIR / "mdots_forclement.dat"
MANARA_COMPILATION_TSV = DATA_YSO_DIR / "manara_2022_ppvii.tsv"
LEGACY_WD_TABLE = DATA_COMPACT_DIR / "Power density data  - Table 1 accreting WDs.csv"
VIDAL_PDF = REFERENCES_DIR / (
    "Vidal-2020-ERD as a technosignature - case for stellivores V1.5.pdf"
)

MASTER_FIGURE_PATH = FIGURES_DIR / "master_power_density.pdf"
MASTER_FIGURE_PDF = FIGURES_DIR / "master_power_density.pdf"

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
DEFAULT_NEUTRON_STAR_RADIUS_M = 1.2e4
DEFAULT_STELLAR_MASS_BLACK_HOLE_RADIUS_SOLAR = 2.95e-5
DEFAULT_WHITE_DWARF_RADIUS_SOLAR = 0.011
WHITE_DWARF_RADIUS_MASS_EXPONENT = -1.0 / 3.0

# ---------------------------------------------------------------------------
# Literature reference overlays — one solid color per reference (all figures)
# Distinct from empirical scatter (YSO/WD/NS/BH) and Kempes scaling tracks.
# ---------------------------------------------------------------------------

REFERENCE_LINE_STYLE = "-"
REFERENCE_LINE_WIDTH = 1.15
REFERENCE_LINE_ALPHA = 0.92

COLOR_REF_CHAISSON_ENVELOPE = "#0f766e"   # teal — plants & animals band (Chaisson 2003; 2011)
COLOR_REF_CHAISSON_SUN = "#78716c"        # stone — Sun benchmark (Chaisson 2001, p. 139)
COLOR_REF_CHAISSON_HUMAN = "#db2777"      # pink — human benchmark (Chaisson 2001, p. 139)
COLOR_REF_CHAISSON_SOCIETY = "#b45309"    # amber — modern society (Chaisson 2001, p. 139)
COLOR_REF_VAN_DUIN = "#4f46e5"            # indigo — dissipative ceiling (van Duin 2024)

CHAISSON_LIVING_ENVELOPE_MIN_W_PER_KG = 0.1
CHAISSON_LIVING_ENVELOPE_MAX_W_PER_KG = 10.0

# Benchmark ladder — Chaisson (2001, Cosmic Evolution, p. 139; cited in Vidal preprint)
CHAISSON_SUN_MASS_KG = SOLAR_MASS
CHAISSON_SUN_POWER_DENSITY_W_PER_KG = SOLAR_LUMINOSITY / SOLAR_MASS  # ~1.93e-4; Chaisson quotes ~2e-4
CHAISSON_HUMAN_MASS_KG = 70.0
CHAISSON_2001_HUMAN_W_PER_KG = 2.0
CHAISSON_2001_SOCIETY_W_PER_KG = 50.0

CHAISSON_ENVELOPE_FILL_ALPHA = 0.10
CHAISSON_BENCHMARK_MARKER_SIZE = 5.0

CHAISSON_ENVELOPE_LEGEND_LABEL = r"Living envelope — plants \& animals (Chaisson 2003; 2011)"
CHAISSON_SUN_BENCHMARK_LABEL = r"Sun benchmark (Chaisson 2001, p.~139)"
CHAISSON_HUMAN_BENCHMARK_LABEL = r"Human benchmark (Chaisson 2001, p.~139)"
CHAISSON_SOCIETY_BENCHMARK_LABEL = r"Modern society (Chaisson 2001, p.~139)"

# Canonical SI display units — all publication figures use kg and W.kg-1 for Φ_m
MASS_UNIT = "kg"
POWER_DENSITY_UNIT = "W.kg-1"

REFERENCE_OVERLAY_REGISTRY: tuple[tuple[str, str, str], ...] = (
    (
        "Chaisson living envelope",
        COLOR_REF_CHAISSON_ENVELOPE,
        f"{CHAISSON_LIVING_ENVELOPE_MIN_W_PER_KG:g}–{CHAISSON_LIVING_ENVELOPE_MAX_W_PER_KG:g} {POWER_DENSITY_UNIT}",
    ),
    ("Chaisson Sun benchmark", COLOR_REF_CHAISSON_SUN, "Chaisson 2001, p. 139"),
    ("Chaisson Human benchmark", COLOR_REF_CHAISSON_HUMAN, "Chaisson 2001, p. 139"),
    ("Chaisson Modern society", COLOR_REF_CHAISSON_SOCIETY, "Chaisson 2001, p. 139"),
    ("van Duin stability limit", COLOR_REF_VAN_DUIN, f"10⁵ {POWER_DENSITY_UNIT}"),
)

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
}

# Universal empirical marker policy — solid filled circles
EMPIRICAL_MARKER_SHAPE = "o"
EMPIRICAL_MARKER_SIZE = 3.5
# Sparse series (YSO, NS, BH, prok/euk biology) — drawn on top, stay readable
EMPIRICAL_MARKER_ALPHA = 0.85
# Dense clouds (738 multicellular, 130 WDs on unified) — translucent underlayers
EMPIRICAL_MARKER_ALPHA_DENSE = 0.22
PLOT_MARKER_SHAPE = EMPIRICAL_MARKER_SHAPE

COMPACT_CATEGORY_MARKERS: dict[str, str] = {
    CATEGORY_CATACLYSMIC_VARIABLES: PLOT_MARKER_SHAPE,
    CATEGORY_NEUTRON_STARS: PLOT_MARKER_SHAPE,
    CATEGORY_TRANSIENT_BLACK_HOLES: PLOT_MARKER_SHAPE,
}

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
PLOT_MARKER_SIZE_BIOLOGY = EMPIRICAL_MARKER_SIZE
PLOT_MARKER_SIZE_YSO = EMPIRICAL_MARKER_SIZE
PLOT_MARKER_SIZE_COMPACT = EMPIRICAL_MARKER_SIZE
PLOT_MARKER_ALPHA_BIOLOGY = EMPIRICAL_MARKER_ALPHA
PLOT_MARKER_ALPHA_YSO = EMPIRICAL_MARKER_ALPHA
PLOT_MARKER_ALPHA_COMPACT = EMPIRICAL_MARKER_ALPHA
PLOT_MARKER_ALPHA_BIOLOGY_MULTICELLULAR = 0.45
PLOT_MARKER_ALPHA_WHITE_DWARFS_UNIFIED = EMPIRICAL_MARKER_ALPHA_DENSE
PLOT_MARKER_ALPHA_WHITE_DWARFS = 0.12  # n=130 CV/WD cohort — dense overlay

# ---------------------------------------------------------------------------
# Geometric decoupling — three-layer scatter architecture (no alpha-blend masking)
# Background: filled YSO circles | Mid-ground: filled compact circles | Foreground: biology diamonds
# YSO and compact share GEOMETRIC_OBSERVATIONAL_CIRCLE_SIZE (filled dots, same s)
# ---------------------------------------------------------------------------

GEOMETRIC_DECOUPLING_ENABLED = True

GeometricLayerName = str  # "background" | "midground" | "foreground"

# Shared filled-circle size for YSO + compact observational cohorts
GEOMETRIC_OBSERVATIONAL_CIRCLE_SIZE = 40.0


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
GEOMETRIC_LAYER_FOREGROUND = GeometricLayerSpec(
    marker="D",
    size=50.0,
    zorder=3,
    alpha=1.0,
    facecolor=None,
    edgecolor="#666666",
    linewidth=0.5,
)

# Biology marker by figure mode — diamonds on unified (cross-domain), circles on biology panel
GEOMETRIC_BIOLOGY_MARKER_UNIFIED = "D"
GEOMETRIC_BIOLOGY_MARKER_BIOLOGY_PANEL = "o"
GEOMETRIC_BIOLOGY_SIZE_UNIFIED = GEOMETRIC_LAYER_FOREGROUND.size
GEOMETRIC_BIOLOGY_SIZE_BIOLOGY_PANEL = GEOMETRIC_OBSERVATIONAL_CIRCLE_SIZE

GEOMETRIC_LAYERS: dict[str, GeometricLayerSpec] = {
    "background": GEOMETRIC_LAYER_BACKGROUND,
    "midground": GEOMETRIC_LAYER_MIDGROUND,
    "foreground": GEOMETRIC_LAYER_FOREGROUND,
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
    "yso": {"loc": LEGEND_LOC_UPPER_RIGHT},
    "compact": {"loc": LEGEND_LOC_UPPER_RIGHT},
    "wd_uncertainties": {"loc": LEGEND_LOC_UPPER_RIGHT},
}
PLOT_GRID_COLOR = "#cbd5e1"
PLOT_GRID_ALPHA_MAJOR = 0.30
PLOT_GRID_ALPHA_MINOR = 0.15

MASTER_MASS_MIN_KG = 1.0e-25
MASTER_MASS_MAX_KG = 1.0e47
MASTER_RHO_MIN_WKG = 1.0e-5
MASTER_RHO_MAX_WKG = 1.0e11
# Legacy gram-axis aliases (processed tables still store mass_g / W g^-1)
MASTER_MASS_MIN_G = MASTER_MASS_MIN_KG * KG_TO_GRAM
MASTER_MASS_MAX_G = MASTER_MASS_MAX_KG * KG_TO_GRAM
MASTER_RHO_MIN_WG = MASTER_RHO_MIN_WKG / KG_TO_GRAM
MASTER_RHO_MAX_WG = MASTER_RHO_MAX_WKG / KG_TO_GRAM

FIGURE_UNIFIED_MASTER_PDF = FIGURES_DIR / "figure_unified_master.pdf"

FIGURE_BIOLOGY_PDF = FIGURES_DIR / "figure_biology.pdf"
FIGURE_YSO_PDF = FIGURES_DIR / "figure_yso.pdf"
FIGURE_COMPACT_OBJECTS_PDF = FIGURES_DIR / "figure_compact_objects.pdf"
FIGURE_COMPACT_PDF = FIGURE_COMPACT_OBJECTS_PDF  # backward-compatible alias
FIGURE_WD_DUBUS_UNCERTAINTIES_PDF = FIGURES_DIR / "figure_wd_dubus_uncertainties.pdf"
FIGURE_REFERENCE_DOC = DOCS_DIR / "Figure_Dataset_Reference_Analysis.docx"

PROCESSED_COMPACT_CSV = PROCESSED_DIR / "processed_compact_results.csv"
PROCESSED_YSO_CSV = PROCESSED_DIR / "processed_yso_results.csv"
VON_DUIN_ERD_CSV = DATA_BIOLOGY_DIR / "von_duin_2024_erd_moesm1.csv"
PROCESSED_BIOLOGY_CSV = PROCESSED_DIR / "processed_von_duin_biology.csv"
DATA_TRACKING_LEDGER_CSV = PROCESSED_DIR / "data_tracking_ledger.csv"
PROVENANCE_MANIFEST_JSON = PROCESSED_DIR / "provenance_manifest.json"

# ApJ axis labels — SI units on all publication figures (always W·kg⁻¹ for Φ_m)
AXIS_LABEL_MASS = rf"Mass $[\mathrm{{{MASS_UNIT}}}]$"
AXIS_LABEL_POWER_DENSITY = r"Power Density $\Phi_m$ ($\mathrm{W \cdot kg^{-1}}$)"
VAN_DUIN_LEGEND_LABEL = r"Stability Boundary (van Duin 2024)"

# Kempes (2017) analytical scaling-law line styling
BIOLOGY_ANALYTICAL_LINEWIDTH = 1.5
BIOLOGY_ANALYTICAL_SAMPLE_COUNT = 500

MASTER_FIGURE_PATH = FIGURE_UNIFIED_MASTER_PDF
MASTER_FIGURE_PDF = FIGURE_UNIFIED_MASTER_PDF

# Zoomed axes for standalone domain figures (global axes reserved for unified master)
DOMAIN_BIOLOGY_MASS = (1.0e-23, 1.0e33)
DOMAIN_BIOLOGY_RHO = (1.0e-12, 3.0e5)  # headroom above van Duin at 10^5 W.kg-1
DOMAIN_YSO_MASS = (1.0e27, 1.0e32)
DOMAIN_YSO_RHO = (1.0e-5, 1.0e-1)
DOMAIN_COMPACT_MASS = (1.0e28, 1.0e32)
DOMAIN_COMPACT_RHO = (1.0e-6, 1.0e11)

# ApJ defense-grade colorblind-safe empirical palette
# Empirical scatter — standard distinct colors (identical across all figures & reference tables)
COLOR_YSO_CONTROL = "#FBBF24"         # yellow — Young Stellar Objects (Manara 2022)
COLOR_WHITE_DWARFS = "#22C55E"        # green — Cataclysmic Variables (accreting WDs)
COLOR_NEUTRON_STARS = "#2563EB"       # blue — Neutron Stars
COLOR_BLACK_HOLES = "#DC2626"         # red — Transient Black Holes

# Kempes (2017) analytical scaling-law line colors (continuous tracks, not scatter)
COLOR_PROKARYOTES = "#A855F7"         # purple
COLOR_EUKARYOTES = "#EA580C"          # orange
COLOR_MULTICELLULAR = "#0891B2"       # cyan

EMPIRICAL_COLOR_REGISTRY: dict[str, tuple[str, str]] = {
    "young_stellar_objects": (COLOR_YSO_CONTROL, "Young Stellar Objects (Manara et al. 2022)"),
    "cataclysmic_variables": (COLOR_WHITE_DWARFS, "Cataclysmic Variables (White Dwarfs)"),
    "neutron_stars": (COLOR_NEUTRON_STARS, "Neutron Stars"),
    "transient_black_holes": (COLOR_BLACK_HOLES, "Transient Black Holes"),
}

COMPACT_CATEGORY_COLORS: dict[str, str] = {
    CATEGORY_CATACLYSMIC_VARIABLES: COLOR_WHITE_DWARFS,
    CATEGORY_NEUTRON_STARS: COLOR_NEUTRON_STARS,
    CATEGORY_TRANSIENT_BLACK_HOLES: COLOR_BLACK_HOLES,
}
COMPACT_CATEGORY_ALPHA: dict[str, float] = {
    CATEGORY_CATACLYSMIC_VARIABLES: PLOT_MARKER_ALPHA_WHITE_DWARFS,
}
