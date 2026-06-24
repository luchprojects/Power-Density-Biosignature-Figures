"""
Power-law trend-line figures for the power-density continuum (exploratory stats pass).

Generates two figures that augment the canonical scatter panels with OLS power-law
fits in log10-log10 mass vs. power-density space (Phi = 10**a * M**b):

  * figure_biology_trends.pdf          — van Duin (2024) biology panel + per-segment
                                         and overall power-law trends.
  * figure_compact_objects_trends.pdf  — compact-objects panel with Dubus (2018) WD
                                         mass + asymmetric Phi error bars, plus
                                         per-category and overall power-law trends.

A power law is the scientifically meaningful trend here: a straight line in log-log
space. For biology the overall slope recovers the allometric decline of mass-specific
metabolic rate with body mass (b ~ -0.25). The identical OLS method is applied to the
compact accretors.

The canonical pipeline (main.py / plotter.py) and its geometry audit are left untouched;
these trend figures are an intentional exploratory companion that draws fit lines the
audit would otherwise forbid.

Run from the project root:  python scripts/figure_trends.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Pipeline modules live in src/ (mirror main.py bootstrap).
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

import config
import plotter
import von_duin_biology


# ---------------------------------------------------------------------------
# Power-law fit (the shared "trend method")
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PowerLawFit:
    """OLS power-law fit in log10-log10 space: Phi = 10**intercept * M**slope."""

    slope: float        # b — power-law exponent
    intercept: float    # a — log10(Phi) at log10(M) = 0
    r_squared: float
    n: int
    x_min: float        # min fitted mass [kg]
    x_max: float        # max fitted mass [kg]


def fit_power_law(
    mass_kg: np.ndarray | pd.Series,
    rho_wkg: np.ndarray | pd.Series,
) -> PowerLawFit | None:
    """OLS fit of log10(Phi) on log10(M); needs >=3 finite, strictly-positive pairs."""
    mass = np.asarray(mass_kg, dtype=float)
    rho = np.asarray(rho_wkg, dtype=float)
    valid = np.isfinite(mass) & np.isfinite(rho) & (mass > 0) & (rho > 0)
    mass = mass[valid]
    rho = rho[valid]
    if mass.size < 3:
        return None

    log_m = np.log10(mass)
    log_r = np.log10(rho)
    # A power-law-vs-mass fit needs spread in mass. Some cohorts (e.g. neutron stars,
    # all tabulated at 1.4 Msun) have effectively zero mass variance, which makes the
    # slope undefined; report no trend rather than a spurious one.
    if float(np.std(log_m)) < 1.0e-6:
        return None
    # Center the regressor before fitting: log10(M) spans ~30 decades for compact
    # objects, which makes a raw polyfit ill-conditioned. Centering is numerically
    # stable and leaves the slope unchanged; recover the M=0 intercept afterwards.
    log_m_mean = float(np.mean(log_m))
    slope, intercept_centered = np.polyfit(log_m - log_m_mean, log_r, 1)
    intercept = intercept_centered - slope * log_m_mean

    predicted = slope * log_m + intercept
    ss_res = float(np.sum((log_r - predicted) ** 2))
    ss_tot = float(np.sum((log_r - np.mean(log_r)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    return PowerLawFit(
        slope=float(slope),
        intercept=float(intercept),
        r_squared=float(r_squared),
        n=int(mass.size),
        x_min=float(mass.min()),
        x_max=float(mass.max()),
    )


def _trend_label(name: str, fit: PowerLawFit) -> str:
    return rf"{name} fit: $b={fit.slope:.2f}$, $R^2={fit.r_squared:.2f}$ ($n={fit.n}$)"


def _plot_trend_line(
    axis,
    fit: PowerLawFit,
    *,
    color: str,
    label: str,
    linestyle: str,
    linewidth: float,
    zorder: int,
) -> None:
    """Draw Phi = 10**(a + b*log10(M)) across the group's fitted mass range."""
    x = np.logspace(
        np.log10(fit.x_min),
        np.log10(fit.x_max),
        config.TREND_FIT_SAMPLE_COUNT,
    )
    y = 10.0 ** (fit.intercept + fit.slope * np.log10(x))
    axis.plot(
        x,
        y,
        color=color,
        linestyle=linestyle,
        linewidth=linewidth,
        alpha=config.TREND_FIT_ALPHA,
        label=label,
        zorder=zorder,
    )


# ---------------------------------------------------------------------------
# Figure builders
# ---------------------------------------------------------------------------


def _save(figure, pdf_path: Path) -> Path:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(pdf_path, bbox_inches="tight", pad_inches=0.05)
    plt.close(figure)
    return pdf_path


def build_biology_trends_figure(
    biology_samples: pd.DataFrame,
) -> tuple[plt.Figure, list[tuple[str, PowerLawFit]]]:
    """Biology panel + per-segment and overall power-law trends."""
    plotter._apply_apj_style()
    mass_limits, rho_limits = plotter._axis_limits_for_mode("biology")
    figure, axis = plt.subplots(figsize=config.DOMAIN_FIGURE_SIZE)
    plotter._configure_axes(axis, mass_limits, rho_limits)
    plotter._add_chaisson_reference_overlays(axis, mass_limits, rho_limits)
    plotter._add_van_duin_bound(axis, rho_limits)

    plotter._plot_von_duin_biology_scatter(axis, biology_samples, mode="biology")

    fits: list[tuple[str, PowerLawFit]] = []
    trend_zorder = 4.5  # above all scatter (max z=3), below legend (z=5)
    for spec in von_duin_biology.BIOLOGY_SEGMENTS:
        rows = biology_samples[biology_samples["segment"] == spec.label]
        fit = fit_power_law(
            plotter._mass_kg_from_frame(rows),
            plotter._rho_w_per_kg_from_frame(rows),
        )
        if fit is None:
            continue
        fits.append((spec.label, fit))
        _plot_trend_line(
            axis,
            fit,
            color=spec.color,
            label=_trend_label(spec.label, fit),
            linestyle=config.TREND_FIT_LINESTYLE_GROUP,
            linewidth=config.TREND_FIT_LINEWIDTH_GROUP,
            zorder=trend_zorder,
        )

    overall_fit = fit_power_law(
        plotter._mass_kg_from_frame(biology_samples),
        plotter._rho_w_per_kg_from_frame(biology_samples),
    )
    if overall_fit is not None:
        fits.append(("All biology", overall_fit))
        _plot_trend_line(
            axis,
            overall_fit,
            color=config.TREND_OVERALL_COLOR,
            label=_trend_label("All biology", overall_fit),
            linestyle=config.TREND_FIT_LINESTYLE_OVERALL,
            linewidth=config.TREND_FIT_LINEWIDTH_OVERALL,
            zorder=trend_zorder + 0.2,
        )

    plotter._apply_apj_legend(axis, "biology")
    figure.tight_layout(pad=0.8)
    plotter._enforce_viewport(axis, mass_limits, rho_limits)
    plotter._finalize_log_axes(axis)
    return figure, fits


def build_compact_trends_figure(
    compact_results: pd.DataFrame,
) -> tuple[plt.Figure, list[tuple[str, PowerLawFit]]]:
    """Compact panel with Dubus WD error bars + per-category and overall trends."""
    plotter._apply_apj_style()
    mass_limits, rho_limits = plotter._axis_limits_for_mode("compact")
    figure, axis = plt.subplots(figsize=config.DOMAIN_FIGURE_SIZE)
    plotter._configure_axes(axis, mass_limits, rho_limits)
    plotter._add_van_duin_bound(axis, rho_limits)

    gravitational = compact_results[compact_results["track"] == "gravitational"].copy()

    # WD markers WITH Dubus (2018) mass + asymmetric Phi error bars.
    plotter._plot_wd_dubus_uncertainties(axis, compact_results)
    # NS + BH markers (exclude WD so the cataclysmic-variable cohort is not drawn twice).
    non_wd = gravitational[
        gravitational["category"] != config.CATEGORY_CATACLYSMIC_VARIABLES
    ]
    plotter._plot_compact_scatter(axis, non_wd, show_errors=False, mode="compact")

    fits: list[tuple[str, PowerLawFit]] = []
    trend_zorder = 4.5  # above all scatter (max z=3), below legend (z=5)
    for category in config.COMPACT_OBJECT_CATEGORIES:
        rows = gravitational[gravitational["category"] == category]
        fit = fit_power_law(
            plotter._mass_kg_from_frame(rows),
            plotter._rho_w_per_kg_from_frame(rows),
        )
        if fit is None:
            continue
        name = config.CATEGORY_DISPLAY_NAMES[category]
        fits.append((name, fit))
        _plot_trend_line(
            axis,
            fit,
            color=config.COMPACT_CATEGORY_COLORS[category],
            label=_trend_label(name, fit),
            linestyle=config.TREND_FIT_LINESTYLE_GROUP,
            linewidth=config.TREND_FIT_LINEWIDTH_GROUP,
            zorder=trend_zorder,
        )

    overall_fit = fit_power_law(
        plotter._mass_kg_from_frame(gravitational),
        plotter._rho_w_per_kg_from_frame(gravitational),
    )
    if overall_fit is not None:
        fits.append(("All compact objects", overall_fit))
        _plot_trend_line(
            axis,
            overall_fit,
            color=config.TREND_OVERALL_COLOR,
            label=_trend_label("All compact", overall_fit),
            linestyle=config.TREND_FIT_LINESTYLE_OVERALL,
            linewidth=config.TREND_FIT_LINEWIDTH_OVERALL,
            zorder=trend_zorder + 0.2,
        )

    plotter._apply_apj_legend(axis, "compact")
    figure.tight_layout(pad=0.8)
    plotter._enforce_viewport(axis, mass_limits, rho_limits)
    plotter._finalize_log_axes(axis)
    return figure, fits


def _mass_rho(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Plot-axis (mass [kg], Phi [W/kg]) arrays from a processed table."""
    return (
        plotter._mass_kg_from_frame(frame),
        plotter._rho_w_per_kg_from_frame(frame),
    )


def build_unified_master_trends_figure(
    compact_results: pd.DataFrame,
    yso_results: pd.DataFrame,
    biology_samples: pd.DataFrame,
) -> tuple[plt.Figure, list[tuple[str, PowerLawFit]]]:
    """Unified master scatter + the 'all biology', 'all compact', and 'all systems' fits."""
    plotter._apply_apj_style()
    mass_limits, rho_limits = plotter._axis_limits_for_mode("unified")
    figure, axis = plt.subplots(figsize=config.MASTER_FIGURE_SIZE)
    plotter._configure_axes(axis, mass_limits, rho_limits)
    plotter._add_chaisson_reference_overlays(axis, mass_limits, rho_limits)
    plotter._add_van_duin_bound(axis, rho_limits)

    # Unified draw order (matches plotter.create_domain_figure): solid compact
    # (WD green) -> YSO rings -> biology.
    plotter._plot_compact_scatter(axis, compact_results, show_errors=False, mode="unified")
    plotter._plot_yso_scatter(
        axis,
        yso_results,
        show_errors=False,
        marker_size=config.YSO_UNIFIED_MARKER_SIZE,
        marker_zorder=config.YSO_UNIFIED_MARKER_ZORDER,
        use_rings=True,
    )
    plotter._plot_von_duin_biology_scatter(axis, biology_samples, mode="unified")

    gravitational = compact_results[compact_results["track"] == "gravitational"].copy()
    bio_mass, bio_rho = _mass_rho(biology_samples)
    cmp_mass, cmp_rho = _mass_rho(gravitational)
    # Cross-domain fit excludes the YSO population (single-mass cluster that would
    # otherwise anchor the slope without adding mass leverage).
    all_mass = np.concatenate([bio_mass, cmp_mass])
    all_rho = np.concatenate([bio_rho, cmp_rho])

    trend_zorder = 4.5  # above all scatter (max z=3), below legend (z=5)
    fits: list[tuple[str, PowerLawFit]] = []

    line_specs = (
        ("All biology", bio_mass, bio_rho, config.TREND_ALL_BIOLOGY_COLOR,
         config.TREND_FIT_LINESTYLE_GROUP, config.TREND_FIT_LINEWIDTH_GROUP, 0),
        ("All compact", cmp_mass, cmp_rho, config.TREND_ALL_COMPACT_COLOR,
         config.TREND_FIT_LINESTYLE_GROUP, config.TREND_FIT_LINEWIDTH_GROUP, 1),
        ("All systems except YSOs", all_mass, all_rho, config.TREND_ALL_SYSTEMS_COLOR,
         config.TREND_FIT_LINESTYLE_OVERALL, config.TREND_FIT_LINEWIDTH_OVERALL, 2),
    )
    for name, mass, rho, color, linestyle, linewidth, offset in line_specs:
        fit = fit_power_law(mass, rho)
        if fit is None:
            continue
        fits.append((name, fit))
        _plot_trend_line(
            axis,
            fit,
            color=color,
            label=_trend_label(name, fit),
            linestyle=linestyle,
            linewidth=linewidth,
            zorder=trend_zorder + offset,
        )

    plotter._apply_apj_legend(axis, "unified")
    figure.tight_layout(pad=0.8)
    plotter._enforce_viewport(axis, mass_limits, rho_limits, lock_autoscale=True)
    plotter._finalize_log_axes(axis)
    return figure, fits


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _print_fit_table(title: str, fits: list[tuple[str, PowerLawFit]]) -> None:
    print(f"\n{title}")
    print(f"  {'group':<28}{'n':>6}{'slope b':>12}{'R^2':>10}")
    print("  " + "-" * 56)
    for name, fit in fits:
        print(f"  {name:<28}{fit.n:>6}{fit.slope:>12.3f}{fit.r_squared:>10.3f}")


def main() -> int:
    compact_results = pd.read_csv(config.PROCESSED_COMPACT_CSV)
    yso_results = pd.read_csv(config.PROCESSED_YSO_CSV)
    biology_samples = plotter.generate_biological_scatter_samples()

    bio_fig, bio_fits = build_biology_trends_figure(biology_samples)
    bio_path = _save(bio_fig, config.FIGURE_BIOLOGY_TRENDS_PDF)

    cmp_fig, cmp_fits = build_compact_trends_figure(compact_results)
    cmp_path = _save(cmp_fig, config.FIGURE_COMPACT_OBJECTS_TRENDS_PDF)

    uni_fig, uni_fits = build_unified_master_trends_figure(
        compact_results, yso_results, biology_samples
    )
    uni_path = _save(uni_fig, config.FIGURE_UNIFIED_MASTER_TRENDS_PDF)

    print("Power-law trend fits (OLS in log10-log10 space; Phi = 10^a * M^b)")
    _print_fit_table("Biology — figure_biology_trends.pdf", bio_fits)
    _print_fit_table("Compact objects — figure_compact_objects_trends.pdf", cmp_fits)
    _print_fit_table("Unified master — figure_unified_master_trends.pdf", uni_fits)
    print(f"\nSaved: {bio_path}")
    print(f"Saved: {cmp_path}")
    print(f"Saved: {uni_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
