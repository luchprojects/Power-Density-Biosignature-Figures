"""
Unified master figure for the power-density evolutionary continuum.

ApJ-compliant log-log charts: geometric decoupling scatter layers (filled YSO background,
filled compact mid-ground with per-category colors, biology foreground with per-segment colors —
diamonds on unified master, circles on biology panel); Chaisson and van Duin literature
references as solid colored lines.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import LogFormatterMathtext

import config
import von_duin_biology

FigureMode = Literal[
    "unified",
    "biology",
    "yso",
    "compact",
    "wd_uncertainties",
]

# Unified master — hard log viewport in SI (kg, W kg^-1)
UNIFIED_XLIM = (config.MASTER_MASS_MIN_KG, config.MASTER_MASS_MAX_KG)
UNIFIED_YLIM = (config.MASTER_RHO_MIN_WKG, config.MASTER_RHO_MAX_WKG)

# ---------------------------------------------------------------------------
# van Duin (2024) — empirical ERD compilation (Section I biological systems)
# ---------------------------------------------------------------------------

VON_DUIN_LABEL_MARKER = von_duin_biology.VON_DUIN_LABEL
BIOLOGICAL_SEGMENTS = von_duin_biology.BIOLOGY_SEGMENTS


def _mass_kg_from_frame(frame: pd.DataFrame) -> np.ndarray:
    """Plot-axis mass in kg (SI) from processed tables."""
    if "mass_kg" in frame.columns:
        return np.asarray(frame["mass_kg"], dtype=float)
    return np.asarray(frame["mass_g"], dtype=float) / config.KG_TO_GRAM


def _rho_w_per_kg_from_frame(frame: pd.DataFrame) -> np.ndarray:
    """Plot-axis power density in W kg^-1 (SI) from processed tables."""
    if "power_density_w_per_kg" in frame.columns:
        return np.asarray(frame["power_density_w_per_kg"], dtype=float)
    return np.asarray(frame["power_density_w_per_g"], dtype=float) * config.KG_TO_GRAM


def _grams_to_kg(values: np.ndarray | pd.Series) -> np.ndarray:
    return np.asarray(values, dtype=float) / config.KG_TO_GRAM


def _w_per_g_to_w_per_kg(values: np.ndarray | pd.Series) -> np.ndarray:
    return np.asarray(values, dtype=float) * config.KG_TO_GRAM


def generate_biological_scatter_samples() -> pd.DataFrame:
    """van Duin (2024) biology table for plotting."""
    return von_duin_biology.combined_biology_table()


def generate_biological_baseline() -> dict[str, pd.DataFrame | dict[str, float]]:
    """Backward-compatible wrapper returning processed biology tables."""
    combined = generate_biological_scatter_samples()
    segments = {
        label: combined[combined["segment"] == label].copy()
        for label in combined["segment"].unique()
    }
    return {"segments": segments, "combined": combined, "normalizations": {}}


def _apply_apj_style() -> None:
    """ApJ / MNRAS publication rcParams."""
    plt.rcParams.update(
        {
            "font.family": config.PLOT_FONT_FAMILY,
            "font.serif": config.PLOT_FONT_SERIF,
            "font.size": config.PLOT_FONT_SIZE,
            "mathtext.fontset": "stix",
            "figure.dpi": config.PLOT_DPI,
            "savefig.dpi": config.PLOT_DPI,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "axes.edgecolor": "#1a1a2e",
            "axes.linewidth": 0.9,
            "axes.grid": True,
            "grid.color": config.PLOT_GRID_COLOR,
            "grid.linestyle": ":",
            "grid.linewidth": 0.5,
            "grid.alpha": config.PLOT_GRID_ALPHA_MAJOR,
            "axes.labelsize": config.PLOT_AXIS_LABEL_SIZE,
            "axes.titlesize": config.PLOT_TITLE_SIZE,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "xtick.major.size": 6,
            "ytick.major.size": 6,
            "xtick.minor.size": 3,
            "ytick.minor.size": 3,
            "xtick.major.width": 0.9,
            "ytick.major.width": 0.9,
            "xtick.labelsize": config.PLOT_FONT_SIZE,
            "ytick.labelsize": config.PLOT_FONT_SIZE,
            "legend.frameon": True,
            "legend.framealpha": config.LEGEND_FRAMEALPHA,
            "legend.edgecolor": "#e2e8f0",
            "legend.facecolor": "#ffffff",
            "legend.fontsize": config.PLOT_LEGEND_SIZE,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _resolve_systematic_errors(
    x: np.ndarray | pd.Series,
    y: np.ndarray | pd.Series,
    xerr_col: np.ndarray | pd.Series | None = None,
    yerr_col: np.ndarray | pd.Series | None = None,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Use dataset error columns only; no synthetic placeholders."""
    xerr: np.ndarray | None = None
    yerr: np.ndarray | None = None
    if xerr_col is not None and np.any(pd.notna(xerr_col)):
        xerr = np.asarray(xerr_col, dtype=float)
    if yerr_col is not None and np.any(pd.notna(yerr_col)):
        yerr = np.asarray(yerr_col, dtype=float)
    return xerr, yerr


def _resolve_interval_errors(
    values: np.ndarray,
    *,
    lo: np.ndarray | pd.Series | None = None,
    hi: np.ndarray | pd.Series | None = None,
    symmetric_err: np.ndarray | pd.Series | None = None,
) -> np.ndarray | None:
    """Build matplotlib asymmetric (2, N) error arrays from lo/hi or symmetric σ."""
    if lo is not None and hi is not None and np.any(pd.notna(lo)) and np.any(pd.notna(hi)):
        lo_arr = np.asarray(lo, dtype=float)
        hi_arr = np.asarray(hi, dtype=float)
        lower = values - lo_arr
        upper = hi_arr - values
        lower = np.where(np.isfinite(lower) & (lower >= 0), lower, np.nan)
        upper = np.where(np.isfinite(upper) & (upper >= 0), upper, np.nan)
        if np.any(np.isfinite(lower)) or np.any(np.isfinite(upper)):
            return np.array([lower, upper])
    if symmetric_err is not None and np.any(pd.notna(symmetric_err)):
        err = np.asarray(symmetric_err, dtype=float)
        return err
    return None


GeometricLayer = Literal["background", "midground", "foreground"]


def _geometric_layer_spec(layer: GeometricLayer) -> config.GeometricLayerSpec:
    return config.GEOMETRIC_LAYERS[layer]


def _scatter_geometric_layer(
    axis: Axes,
    x: np.ndarray | pd.Series,
    y: np.ndarray | pd.Series,
    *,
    layer: GeometricLayer,
    label: str,
    color: str | None = None,
    alpha: float | None = None,
    marker: str | None = None,
    size: float | None = None,
) -> None:
    """Strict geometric-decoupling scatter — marker geometry replaces alpha-blend masking."""
    spec = _geometric_layer_spec(layer)
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    scatter_kwargs: dict[str, object] = {
        "s": spec.size if size is None else size,
        "marker": spec.marker if marker is None else marker,
        "alpha": spec.alpha if alpha is None else alpha,
        "zorder": spec.zorder,
        "label": label,
    }
    if layer in {"background", "midground"}:
        fill = color or spec.facecolor
        scatter_kwargs["c"] = fill
        scatter_kwargs["edgecolors"] = "none"
    else:
        fill = color or spec.facecolor
        scatter_kwargs["c"] = fill
        scatter_kwargs["edgecolors"] = spec.edgecolor
        scatter_kwargs["linewidths"] = spec.linewidth
    axis.scatter(x_arr, y_arr, **scatter_kwargs)


def _errorbar_geometric_layer(
    axis: Axes,
    x: np.ndarray | pd.Series,
    y: np.ndarray | pd.Series,
    *,
    layer: GeometricLayer,
    label: str,
    color: str | None = None,
    alpha: float | None = None,
    xerr_col: np.ndarray | pd.Series | None = None,
    yerr_col: np.ndarray | pd.Series | None = None,
    x_lo_col: np.ndarray | pd.Series | None = None,
    x_hi_col: np.ndarray | pd.Series | None = None,
    y_lo_col: np.ndarray | pd.Series | None = None,
    y_hi_col: np.ndarray | pd.Series | None = None,
    delicate: bool = False,
) -> None:
    """Delicate error bars on zoom panels, with geometric-decoupling marker overlay."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    xerr = _resolve_interval_errors(
        x_arr,
        lo=x_lo_col,
        hi=x_hi_col,
        symmetric_err=xerr_col,
    )
    yerr = _resolve_interval_errors(
        y_arr,
        lo=y_lo_col,
        hi=y_hi_col,
        symmetric_err=yerr_col,
    )
    spec = _geometric_layer_spec(layer)
    bar_alpha = config.ERRORBAR_ALPHA_ZOOM if delicate else config.ERRORBAR_ALPHA
    bar_lw = config.ERRORBAR_ELINEWIDTH_ZOOM if delicate else config.ERRORBAR_ELINEWIDTH
    bar_cap = config.ERRORBAR_CAPSIZE_ZOOM if delicate else config.ERRORBAR_CAPSIZE
    if color:
        ecolor = color
    elif layer == "background":
        ecolor = color or config.COLOR_YSO_CONTROL
    else:
        ecolor = config.ERRORBAR_ECOLOR
    if xerr is not None or yerr is not None:
        axis.errorbar(
            x_arr,
            y_arr,
            xerr=xerr,
            yerr=yerr,
            fmt="none",
            linestyle="none",
            elinewidth=bar_lw,
            capsize=bar_cap,
            capthick=bar_lw,
            ecolor=mcolors.to_rgba(ecolor, bar_alpha),
            zorder=max(spec.zorder - 1, 0),
        )
    _scatter_geometric_layer(
        axis, x_arr, y_arr, layer=layer, label=label, color=color, alpha=alpha
    )


def _empirical_marker_kwargs(color: str, *, alpha: float | None = None) -> dict[str, object]:
    """Solid filled-circle empirical markers — one color per object class."""
    return {
        "linestyle": "none",
        "marker": config.EMPIRICAL_MARKER_SHAPE,
        "color": color,
        "markerfacecolor": color,
        "markeredgecolor": color,
        "markeredgewidth": 0.0,
        "markersize": config.EMPIRICAL_MARKER_SIZE,
        "alpha": config.EMPIRICAL_MARKER_ALPHA if alpha is None else alpha,
    }


def _scatter_series(
    axis: Axes,
    x: np.ndarray | pd.Series,
    y: np.ndarray | pd.Series,
    *,
    color: str,
    label: str,
    zorder: int,
    alpha: float | None = None,
) -> None:
    """Solid filled-circle empirical markers (unified master / domain scatter)."""
    axis.plot(
        np.asarray(x, dtype=float),
        np.asarray(y, dtype=float),
        label=label,
        zorder=zorder,
        **_empirical_marker_kwargs(color, alpha=alpha),
    )


def _errorbar_series(
    axis: Axes,
    x: np.ndarray | pd.Series,
    y: np.ndarray | pd.Series,
    *,
    color: str,
    label: str,
    zorder: int,
    xerr_col: np.ndarray | pd.Series | None = None,
    yerr_col: np.ndarray | pd.Series | None = None,
    delicate: bool = False,
) -> None:
    """Empirical markers with delicate error bars on zoom panels only."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    xerr, yerr = _resolve_systematic_errors(x_arr, y_arr, xerr_col, yerr_col)
    bar_alpha = config.ERRORBAR_ALPHA_ZOOM if delicate else config.ERRORBAR_ALPHA
    bar_lw = config.ERRORBAR_ELINEWIDTH_ZOOM if delicate else config.ERRORBAR_ELINEWIDTH
    bar_cap = config.ERRORBAR_CAPSIZE_ZOOM if delicate else config.ERRORBAR_CAPSIZE
    if xerr is not None or yerr is not None:
        ecolor_rgba = mcolors.to_rgba(config.ERRORBAR_ECOLOR, bar_alpha)
        axis.errorbar(
            x_arr,
            y_arr,
            xerr=xerr,
            yerr=yerr,
            fmt="none",
            linestyle="none",
            elinewidth=bar_lw,
            capsize=bar_cap,
            capthick=bar_lw,
            ecolor=ecolor_rgba,
            zorder=zorder - 1,
        )
    axis.plot(
        x_arr,
        y_arr,
        label=label,
        zorder=zorder,
        **_empirical_marker_kwargs(color),
    )


def _apply_scale_tick_formatting(axis: Axes) -> None:
    """Log axes: mathtext major labels + automatic minor subdivisions; linear axes: default."""
    log_formatter = LogFormatterMathtext(base=10.0, labelOnlyBase=True)
    if axis.get_xscale() == "log":
        axis.xaxis.set_major_formatter(log_formatter)
    if axis.get_yscale() == "log":
        axis.yaxis.set_major_formatter(log_formatter)
    if axis.get_xscale() == "log" or axis.get_yscale() == "log":
        axis.minorticks_on()


def _finalize_axes(axis: Axes) -> None:
    """Mirrored inward ticks; native log minor ticks on log-scaled dimensions only."""
    axis.tick_params(direction="in", top=True, right=True, which="both")
    axis.tick_params(which="major", length=6, width=0.9)
    axis.tick_params(which="minor", length=3, width=0.7)
    _apply_scale_tick_formatting(axis)
    axis.grid(
        True,
        which="major",
        linestyle=":",
        linewidth=0.5,
        color=config.PLOT_GRID_COLOR,
        alpha=config.PLOT_GRID_ALPHA_MAJOR,
        zorder=0,
    )
    axis.grid(
        True,
        which="minor",
        linestyle=":",
        linewidth=0.3,
        color=config.PLOT_GRID_COLOR,
        alpha=config.PLOT_GRID_ALPHA_MINOR,
        zorder=0,
    )


def _configure_axes(
    axis: Axes,
    mass_limits: tuple[float, float],
    rho_limits: tuple[float, float],
) -> None:
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlim(mass_limits[0], mass_limits[1])
    axis.set_ylim(rho_limits[0], rho_limits[1])
    axis.set_xlabel(config.AXIS_LABEL_MASS)
    axis.set_ylabel(config.AXIS_LABEL_POWER_DENSITY)
    _finalize_axes(axis)


def _enforce_viewport(
    axis: Axes,
    mass_limits: tuple[float, float],
    rho_limits: tuple[float, float],
    *,
    lock_autoscale: bool = False,
) -> None:
    """Re-bind hard log limits after artists are drawn (prevents padding drift)."""
    axis.set_xlim(mass_limits[0], mass_limits[1])
    axis.set_ylim(rho_limits[0], rho_limits[1])
    if lock_autoscale:
        axis.set_autoscale_on(False)
        axis.use_sticky_edges = False


def _finalize_log_axes(axis: Axes) -> None:
    """Re-apply tick styling after artists are drawn."""
    _finalize_axes(axis)


def _axis_limits_for_mode(mode: FigureMode) -> tuple[tuple[float, float], tuple[float, float]]:
    if mode == "unified":
        return (UNIFIED_XLIM, UNIFIED_YLIM)
    if mode == "biology":
        return (config.DOMAIN_BIOLOGY_MASS, config.DOMAIN_BIOLOGY_RHO)
    if mode == "yso":
        return (config.DOMAIN_YSO_MASS, config.DOMAIN_YSO_RHO)
    if mode == "compact":
        return (config.DOMAIN_COMPACT_MASS, config.DOMAIN_COMPACT_RHO)
    if mode == "wd_uncertainties":
        return (config.DOMAIN_COMPACT_MASS, config.DOMAIN_COMPACT_RHO)
    raise ValueError(f"Unknown figure mode: {mode!r}")


def _reference_hline(
    axis: Axes,
    rho: float,
    *,
    color: str,
    label: str,
    zorder: int = 2,
) -> None:
    """Solid literature reference line — shared styling across all figures."""
    axis.axhline(
        rho,
        color=color,
        linestyle=config.REFERENCE_LINE_STYLE,
        linewidth=config.REFERENCE_LINE_WIDTH,
        alpha=config.REFERENCE_LINE_ALPHA,
        zorder=zorder,
        label=label,
    )


def _add_van_duin_bound(axis: Axes, rho_limits: tuple[float, float]) -> None:
    if rho_limits[0] <= config.VAN_DUIN_DISSIPATIVE_LIMIT_W_PER_KG <= rho_limits[1]:
        _reference_hline(
            axis,
            config.VAN_DUIN_DISSIPATIVE_LIMIT_W_PER_KG,
            color=config.COLOR_REF_VAN_DUIN,
            label=config.VAN_DUIN_LEGEND_LABEL,
            zorder=config.VAN_DUIN_ZORDER,
        )


def _add_chaisson_living_references(
    axis: Axes,
    mass_limits: tuple[float, float],
    rho_limits: tuple[float, float],
) -> None:
    """
    Chaisson literature overlays — analytical reference geometry, not CSV scatter.

    Each reference uses one distinct solid color (see config.REFERENCE_OVERLAY_REGISTRY).
    """
    env_lo = config.CHAISSON_LIVING_ENVELOPE_MIN_W_PER_KG
    env_hi = config.CHAISSON_LIVING_ENVELOPE_MAX_W_PER_KG
    if rho_limits[0] < env_hi and rho_limits[1] > env_lo:
        span_lo = max(env_lo, rho_limits[0])
        span_hi = min(env_hi, rho_limits[1])
        axis.axhspan(
            span_lo,
            span_hi,
            xmin=0.0,
            xmax=1.0,
            facecolor=config.COLOR_REF_CHAISSON_ENVELOPE,
            edgecolor="none",
            alpha=config.CHAISSON_ENVELOPE_FILL_ALPHA,
            zorder=1,
        )
        _reference_hline(
            axis,
            span_lo,
            color=config.COLOR_REF_CHAISSON_ENVELOPE,
            label=config.CHAISSON_ENVELOPE_LEGEND_LABEL,
            zorder=2,
        )
        _reference_hline(
            axis,
            span_hi,
            color=config.COLOR_REF_CHAISSON_ENVELOPE,
            label="_nolegend_",
            zorder=2,
        )

    benchmark_specs: tuple[tuple[float, str, str], ...] = (
        (
            config.CHAISSON_SUN_POWER_DENSITY_W_PER_KG,
            config.CHAISSON_SUN_BENCHMARK_LABEL,
            config.COLOR_REF_CHAISSON_SUN,
        ),
        (
            config.CHAISSON_2001_HUMAN_W_PER_KG,
            config.CHAISSON_HUMAN_BENCHMARK_LABEL,
            config.COLOR_REF_CHAISSON_HUMAN,
        ),
        (
            config.CHAISSON_2001_SOCIETY_W_PER_KG,
            config.CHAISSON_SOCIETY_BENCHMARK_LABEL,
            config.COLOR_REF_CHAISSON_SOCIETY,
        ),
    )
    for rho, label, color in benchmark_specs:
        if rho_limits[0] <= rho <= rho_limits[1]:
            _reference_hline(axis, rho, color=color, label=label, zorder=2)


def _apply_apj_legend(axis: Axes, mode: FigureMode | str) -> None:
    """Opaque white legend card — per-figure anchor avoids collisions."""
    layout = config.LEGEND_LAYOUT.get(mode, {"loc": config.LEGEND_LOC_UPPER_RIGHT})
    legend = axis.legend(
        fontsize=config.PLOT_LEGEND_SIZE,
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#e2e8f0",
        framealpha=config.LEGEND_FRAMEALPHA,
        markerscale=1.0,
        handletextpad=0.4,
        borderaxespad=0.5,
        handlelength=2.0,
        labelspacing=0.4,
        **layout,
    )
    legend.set_zorder(config.LEGEND_ZORDER)
    # Legend swatches use canonical full-opacity registry colors (plot may use lower α for dense cohorts).
    for handle in legend.legend_handles:
        if hasattr(handle, "set_alpha"):
            handle.set_alpha(1.0)


def _is_permitted_analytical_line(label: str, linestyle: str) -> bool:
    if label == config.VAN_DUIN_LEGEND_LABEL and linestyle in ("-", "solid"):
        return True
    if "Chaisson" in label and linestyle in ("-", "solid"):
        return True
    if label in ("_nolegend_",):
        return True
    if "Human Metabolism" in label and linestyle in ("-", "solid"):
        return True
    if "Star" in label and "protostar" in label and linestyle in ("-", "solid"):
        return True
    if "Baseline" in label and linestyle == "--":
        return True
    return False


def audit_figure_geometry(figure: Figure) -> None:
    """
    Verify ApJ plot geometry: empirical scatter only; Chaisson overlays and
    van Duin stability boundary are the sole permitted connected lines.
    """
    from matplotlib.lines import Line2D

    for axis in figure.axes:
        for artist in axis.get_children():
            if not isinstance(artist, Line2D):
                continue
            label = artist.get_label() or ""
            if label.startswith("_"):
                continue
            linestyle = artist.get_linestyle()
            if linestyle in ("none", " ", "", "None"):
                continue
            if linestyle in (":", "-."):
                continue
            if artist.get_color() in (config.ERRORBAR_ECOLOR, "#94a3b8"):
                continue
            if _is_permitted_analytical_line(label, linestyle):
                continue
            raise RuntimeError(
                "ApJ geometry audit failed: impermissible connected line. "
                f"label={label!r}, linestyle={linestyle!r}"
            )


def _biology_zorder(segment: str, mode: FigureMode) -> int:
    _ = (segment, mode)
    return config.GEOMETRIC_LAYER_FOREGROUND.zorder


def _biology_marker_style(mode: FigureMode) -> tuple[str, float]:
    """Unified master: diamonds; biology panel: filled circles (same segment colors)."""
    if mode == "biology":
        return (
            config.GEOMETRIC_BIOLOGY_MARKER_BIOLOGY_PANEL,
            config.GEOMETRIC_BIOLOGY_SIZE_BIOLOGY_PANEL,
        )
    return (
        config.GEOMETRIC_BIOLOGY_MARKER_UNIFIED,
        config.GEOMETRIC_BIOLOGY_SIZE_UNIFIED,
    )


def _plot_von_duin_biology_scatter(
    axis: Axes,
    biology_samples: pd.DataFrame,
    *,
    mode: FigureMode,
) -> None:
    """van Duin (2024) Section-I ERD — diamonds on unified, circles on biology panel."""
    if biology_samples.empty:
        return

    biology_marker, biology_size = _biology_marker_style(mode)
    segment_order = ("Multicellular", "Prokaryotes", "Eukaryotes")
    segments_by_label = {spec.label: spec for spec in BIOLOGICAL_SEGMENTS}

    for label in segment_order:
        spec = segments_by_label.get(label)
        if spec is None:
            continue
        rows = biology_samples[biology_samples["segment"] == spec.label]
        if rows.empty:
            continue
        x_arr = _mass_kg_from_frame(rows)
        y_arr = _rho_w_per_kg_from_frame(rows)
        legend_label = rf"{spec.label} — {VON_DUIN_LABEL_MARKER} ($n={len(rows)}$)"
        if config.GEOMETRIC_DECOUPLING_ENABLED:
            # Biology panel: filled circles without marker edge outline.
            biology_layer: GeometricLayer = "midground" if mode == "biology" else "foreground"
            biology_alpha = 1.0 if mode == "biology" else None
            _scatter_geometric_layer(
                axis,
                x_arr,
                y_arr,
                layer=biology_layer,
                label=legend_label,
                color=spec.color,
                marker=biology_marker,
                size=biology_size,
                alpha=biology_alpha,
            )
        else:
            _scatter_series(
                axis,
                x_arr,
                y_arr,
                color=spec.color,
                label=legend_label,
                zorder=_biology_zorder(spec.label, mode),
            )


def _plot_yso_scatter(axis: Axes, yso_results: pd.DataFrame, *, show_errors: bool) -> None:
    """Empirical YSO markers — background diffuse circle layer."""
    if yso_results.empty:
        return
    label = rf"YSO Population — Manara et al. (2022) ($n={len(yso_results)}$)"
    x_arr = _mass_kg_from_frame(yso_results)
    y_arr = _rho_w_per_kg_from_frame(yso_results)
    if config.GEOMETRIC_DECOUPLING_ENABLED:
        if show_errors:
            xerr_col = yso_results["mass_kg_err"] if "mass_kg_err" in yso_results.columns else None
            if xerr_col is None and "mass_g_err" in yso_results.columns:
                xerr_col = yso_results["mass_g_err"] / config.KG_TO_GRAM
            yerr_col = (
                yso_results["power_density_w_per_kg_err"]
                if "power_density_w_per_kg_err" in yso_results.columns
                else None
            )
            if yerr_col is None and "power_density_w_per_g_err" in yso_results.columns:
                yerr_col = yso_results["power_density_w_per_g_err"] * config.KG_TO_GRAM
            _errorbar_geometric_layer(
                axis,
                x_arr,
                y_arr,
                layer="background",
                label=label,
                color=config.COLOR_YSO_CONTROL,
                xerr_col=xerr_col,
                yerr_col=yerr_col,
                delicate=True,
            )
        else:
            _scatter_geometric_layer(
                axis,
                x_arr,
                y_arr,
                layer="background",
                label=label,
                color=config.COLOR_YSO_CONTROL,
            )
        return

    color = config.COLOR_YSO_CONTROL
    label = rf"YSO Population — Manara et al. (2022) ($n={len(yso_results)}$)"
    x_arr = _mass_kg_from_frame(yso_results)
    y_arr = _rho_w_per_kg_from_frame(yso_results)
    if show_errors:
        xerr_col = yso_results["mass_kg_err"] if "mass_kg_err" in yso_results.columns else None
        if xerr_col is None and "mass_g_err" in yso_results.columns:
            xerr_col = yso_results["mass_g_err"] / config.KG_TO_GRAM
        yerr_col = (
            yso_results["power_density_w_per_kg_err"]
            if "power_density_w_per_kg_err" in yso_results.columns
            else None
        )
        if yerr_col is None and "power_density_w_per_g_err" in yso_results.columns:
            yerr_col = yso_results["power_density_w_per_g_err"] * config.KG_TO_GRAM
        xerr, yerr = _resolve_systematic_errors(x_arr, y_arr, xerr_col, yerr_col)
        if xerr is not None or yerr is not None:
            ecolor_rgba = mcolors.to_rgba(config.ERRORBAR_ECOLOR, config.ERRORBAR_ALPHA_ZOOM)
            axis.errorbar(
                x_arr,
                y_arr,
                xerr=xerr,
                yerr=yerr,
                fmt="none",
                linestyle="none",
                elinewidth=config.ERRORBAR_ELINEWIDTH_ZOOM,
                capsize=config.ERRORBAR_CAPSIZE_ZOOM,
                capthick=config.ERRORBAR_ELINEWIDTH_ZOOM,
                ecolor=ecolor_rgba,
                zorder=3,
            )
    axis.plot(
        x_arr,
        y_arr,
        label=label,
        zorder=4,
        **_empirical_marker_kwargs(color),
    )


def _compact_category_alpha(category: str, mode: FigureMode) -> float | None:
    """
    WD marker opacity — match unified master on multi-cohort overlays.

    unified master: translucent WDs (dense underlayer).
    compact-only panel: full opacity (no overlap with other domains).
    """
    if mode == "compact":
        return None
    return config.COMPACT_CATEGORY_ALPHA.get(category)


def _plot_compact_scatter(
    axis: Axes,
    compact_results: pd.DataFrame,
    *,
    show_errors: bool,
    mode: FigureMode,
) -> None:
    if compact_results.empty:
        return

    display = compact_results[compact_results["track"] == "gravitational"].copy()
    if display.empty:
        display = compact_results.copy()

    for category in config.COMPACT_OBJECT_CATEGORIES:
        rows = display[display["category"] == category]
        if rows.empty:
            continue

        x_mass = _mass_kg_from_frame(rows)
        y_rho = _rho_w_per_kg_from_frame(rows)
        legend_label = config.CATEGORY_DISPLAY_NAMES[category]

        if config.GEOMETRIC_DECOUPLING_ENABLED:
            category_color = config.COMPACT_CATEGORY_COLORS[category]
            category_alpha = _compact_category_alpha(category, mode)
            if show_errors:
                xerr_col = rows["mass_kg_err"] if "mass_kg_err" in rows.columns else None
                if xerr_col is None and "mass_g_err" in rows.columns:
                    xerr_col = rows["mass_g_err"] / config.KG_TO_GRAM
                yerr_col = (
                    rows["power_density_w_per_kg_err"]
                    if "power_density_w_per_kg_err" in rows.columns
                    else None
                )
                if yerr_col is None and "power_density_w_per_g_err" in rows.columns:
                    yerr_col = rows["power_density_w_per_g_err"] * config.KG_TO_GRAM
                _errorbar_geometric_layer(
                    axis,
                    x_mass,
                    y_rho,
                    layer="midground",
                    label=legend_label,
                    color=category_color,
                    alpha=category_alpha,
                    xerr_col=xerr_col,
                    yerr_col=yerr_col,
                    delicate=True,
                )
            else:
                _scatter_geometric_layer(
                    axis,
                    x_mass,
                    y_rho,
                    layer="midground",
                    label=legend_label,
                    color=category_color,
                    alpha=category_alpha,
                )
            continue

        marker_alpha = (
            config.PLOT_MARKER_ALPHA_WHITE_DWARFS_UNIFIED
            if mode == "unified" and category == config.CATEGORY_CATACLYSMIC_VARIABLES
            else None
        )

        if show_errors:
            xerr_col = rows["mass_kg_err"] if "mass_kg_err" in rows.columns else None
            if xerr_col is None and "mass_g_err" in rows.columns:
                xerr_col = rows["mass_g_err"] / config.KG_TO_GRAM
            yerr_col = (
                rows["power_density_w_per_kg_err"]
                if "power_density_w_per_kg_err" in rows.columns
                else None
            )
            if yerr_col is None and "power_density_w_per_g_err" in rows.columns:
                yerr_col = rows["power_density_w_per_g_err"] * config.KG_TO_GRAM
            _errorbar_series(
                axis,
                x_mass,
                y_rho,
                color=config.COMPACT_CATEGORY_COLORS[category],
                label=legend_label,
                zorder=6,
                delicate=True,
                xerr_col=xerr_col,
                yerr_col=yerr_col,
            )
        else:
            _scatter_series(
                axis,
                x_mass,
                y_rho,
                color=config.COMPACT_CATEGORY_COLORS[category],
                label=legend_label,
                zorder=6,
                alpha=marker_alpha,
            )


def _plot_wd_dubus_uncertainties(
    axis: Axes,
    compact_results: pd.DataFrame,
) -> None:
    """WD-only panel with Dubus (2018) MC 68% mass and Ṁ uncertainties."""
    rows = compact_results[
        (compact_results["category"] == config.CATEGORY_CATACLYSMIC_VARIABLES)
        & (compact_results["track"] == "gravitational")
    ]
    if rows.empty:
        return

    x_arr = _mass_kg_from_frame(rows)
    y_arr = _rho_w_per_kg_from_frame(rows)
    legend_label = (
        rf"Cataclysmic Variables (White Dwarfs) — Dubus et al. (2018) "
        rf"($n={len(rows)}$)"
    )
    _errorbar_geometric_layer(
        axis,
        x_arr,
        y_arr,
        layer="midground",
        label=legend_label,
        color=config.COLOR_WHITE_DWARFS,
        alpha=1.0,
        xerr_col=rows["mass_kg_err"] if "mass_kg_err" in rows.columns else None,
        y_lo_col=(
            rows["power_density_w_per_kg_lo"]
            if "power_density_w_per_kg_lo" in rows.columns
            else None
        ),
        y_hi_col=(
            rows["power_density_w_per_kg_hi"]
            if "power_density_w_per_kg_hi" in rows.columns
            else None
        ),
        delicate=True,
    )


def create_domain_figure(
    mode: FigureMode,
    compact_results: pd.DataFrame,
    yso_results: pd.DataFrame,
    biology_samples: pd.DataFrame | None = None,
) -> Figure:
    """Build one ApJ-compliant figure for a specific domain or the unified master."""
    if biology_samples is None:
        biology_samples = generate_biological_scatter_samples()
    _apply_apj_style()

    mass_limits, rho_limits = _axis_limits_for_mode(mode)
    figure_size = config.MASTER_FIGURE_SIZE if mode == "unified" else config.DOMAIN_FIGURE_SIZE
    figure, axis = plt.subplots(figsize=figure_size)
    _configure_axes(axis, mass_limits, rho_limits)
    if mode in {"unified", "biology"}:
        _add_chaisson_living_references(axis, mass_limits, rho_limits)
    if mode != "wd_uncertainties":
        _add_van_duin_bound(axis, rho_limits)

    show_yso_errors = mode != "unified"
    # Compact scatter matches unified on overlay panels; error bars only on wd_uncertainties.
    show_compact_errors = False

    # Geometric decoupling draw order: background → mid-ground → foreground
    if mode in {"unified", "yso"}:
        _plot_yso_scatter(axis, yso_results, show_errors=show_yso_errors)
    if mode in {"unified", "compact"}:
        _plot_compact_scatter(
            axis, compact_results, show_errors=show_compact_errors, mode=mode
        )
    if mode == "wd_uncertainties":
        _plot_wd_dubus_uncertainties(axis, compact_results)
    if mode in {"unified", "biology"}:
        _plot_von_duin_biology_scatter(axis, biology_samples, mode=mode)

    _apply_apj_legend(axis, mode)
    figure.tight_layout(pad=0.8)

    _enforce_viewport(
        axis,
        mass_limits,
        rho_limits,
        lock_autoscale=(mode == "unified"),
    )
    _finalize_log_axes(axis)
    audit_figure_geometry(figure)
    return figure


def _configure_generic_log_axes(
    axis: Axes,
    x_limits: tuple[float, float],
    y_limits: tuple[float, float],
    xlabel: str,
    ylabel: str,
) -> None:
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlim(x_limits[0], x_limits[1])
    axis.set_ylim(y_limits[0], y_limits[1])
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)
    _finalize_axes(axis)


def create_unified_master_figure(
    compact_results: pd.DataFrame,
    yso_results: pd.DataFrame,
    biology_samples: pd.DataFrame | None = None,
) -> Figure:
    return create_domain_figure(
        mode="unified",
        compact_results=compact_results,
        yso_results=yso_results,
        biology_samples=biology_samples,
    )


def _clear_existing_figures() -> None:
    """Remove stale figure outputs before regenerating (PDF only)."""
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for path in config.FIGURES_DIR.glob("*.pdf"):
        path.unlink()
    for path in config.FIGURES_DIR.glob("*.png"):
        path.unlink()
    panels_dir = config.FIGURES_DIR / "panels"
    if panels_dir.exists():
        for path in panels_dir.glob("*"):
            if path.is_file():
                path.unlink()
        panels_dir.rmdir()


def _save_figure_pdf(figure: Figure, pdf_path: Path) -> Path:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(pdf_path, bbox_inches="tight", pad_inches=0.05)
    plt.close(figure)
    return pdf_path


def save_all_figures(
    compact_results: pd.DataFrame,
    yso_results: pd.DataFrame,
    biology_samples: pd.DataFrame | None = None,
) -> dict[str, Path]:
    """
    Export five ApJ publication figures (vector PDF only).

    Unified master: scatter only. Zoom panels: error bars only when datasets supply them.
    """
    _clear_existing_figures()

    domain_specs: list[tuple[FigureMode, Path]] = [
        ("unified", config.FIGURE_UNIFIED_MASTER_PDF),
        ("biology", config.FIGURE_BIOLOGY_PDF),
        ("yso", config.FIGURE_YSO_PDF),
        ("compact", config.FIGURE_COMPACT_OBJECTS_PDF),
        ("wd_uncertainties", config.FIGURE_WD_DUBUS_UNCERTAINTIES_PDF),
    ]

    saved: dict[str, Path] = {}
    for mode, pdf_path in domain_specs:
        figure = create_domain_figure(
            mode=mode,
            compact_results=compact_results,
            yso_results=yso_results,
            biology_samples=biology_samples,
        )
        out_path = _save_figure_pdf(figure, pdf_path)
        saved[f"{mode}_pdf"] = out_path
        if mode == "compact":
            saved["compact_objects_pdf"] = out_path

    return saved


def save_unified_master_figure(
    figure: Figure,
    pdf_path: Path | None = None,
) -> dict[str, Path]:
    return {"pdf": _save_figure_pdf(figure, pdf_path or config.FIGURE_UNIFIED_MASTER_PDF)}


# ---------------------------------------------------------------------------
# Legacy aliases
# ---------------------------------------------------------------------------


def create_master_power_density_figure(
    compact_results: pd.DataFrame,
    yso_results: pd.DataFrame,
    biological_baseline: dict[str, pd.DataFrame | dict[str, float]] | None = None,
) -> Figure:
    biology = (
        biological_baseline["combined"]
        if biological_baseline is not None
        else generate_biological_scatter_samples()
    )
    return create_unified_master_figure(compact_results, yso_results, biology)


def save_master_figure(
    figure: Figure,
    pdf_path: Path | None = None,
) -> dict[str, Path]:
    return save_unified_master_figure(figure, pdf_path=pdf_path)


# Backward-compatible audit alias
audit_figure_scatter_only = audit_figure_geometry
