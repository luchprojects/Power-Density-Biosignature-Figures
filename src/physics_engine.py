"""
Physics engine for power-density calculations and coordinate conversions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

import config

TrackType = Literal["gravitational", "nuclear"]
PhiSourceType = Literal["tabulated_erd", "computed_from_mdot"]


@dataclass(frozen=True)
class PowerDensityResult:
    name: str
    category: str
    mass_kg: float
    mass_g: float
    mdot_kg_s: float
    radius_m: float
    eta: float
    luminosity_w: float
    power_density_w_per_kg: float
    power_density_w_per_g: float
    track: TrackType
    phi_source: PhiSourceType


def gravitational_efficiency(mass_kg: float, radius_m: float) -> float:
    if mass_kg <= 0.0 or radius_m <= 0.0:
        raise ValueError("mass_kg and radius_m must be positive.")
    return (config.GRAVITATIONAL_CONSTANT * mass_kg) / ((config.SPEED_OF_LIGHT ** 2) * radius_m)


def accretion_luminosity_watts(mdot_kg_s: float, eta: float) -> float:
    if mdot_kg_s < 0.0 or eta < 0.0:
        raise ValueError("mdot_kg_s and eta must be non-negative.")
    return eta * mdot_kg_s * (config.SPEED_OF_LIGHT ** 2)


def power_density_from_luminosity(luminosity_w: float, mass_kg: float) -> float:
    if mass_kg <= 0.0 or luminosity_w < 0.0:
        raise ValueError("Invalid luminosity or mass.")
    return luminosity_w / mass_kg


def w_per_kg_to_w_per_g(value_w_per_kg: float) -> float:
    return value_w_per_kg / config.KG_TO_GRAM


def erg_per_s_per_g_to_w_per_g(value_erg_s_g: float) -> float:
    return value_erg_s_g * config.ERG_TO_JOULE


def solar_mass_to_kg(mass_msun: float) -> float:
    return mass_msun * config.SOLAR_MASS


def kg_to_grams(mass_kg: float) -> float:
    return mass_kg * config.KG_TO_GRAM


def msun_per_year_to_kg_per_s(mdot_msun_yr: float) -> float:
    return mdot_msun_yr * config.SOLAR_MASS_PER_YEAR_TO_KG_PER_S


def grams_per_second_to_kg_per_s(mdot_g_s: float) -> float:
    return mdot_g_s * config.GRAM_TO_KG


def solar_radius_to_m(radius_rsun: float) -> float:
    return radius_rsun * config.SOLAR_RADIUS


def white_dwarf_radius_meters(mass_msun: float) -> float:
    radius_rsun = (
        config.DEFAULT_WHITE_DWARF_RADIUS_SOLAR
        * (mass_msun ** config.WHITE_DWARF_RADIUS_MASS_EXPONENT)
    )
    return solar_radius_to_m(radius_rsun)


def neutron_star_radius_meters() -> float:
    return config.DEFAULT_NEUTRON_STAR_RADIUS_M


def stellar_black_hole_radius_meters(mass_msun: float) -> float:
    return solar_radius_to_m(config.DEFAULT_STELLAR_MASS_BLACK_HOLE_RADIUS_SOLAR * mass_msun)


def schwarzschild_radius_meters(mass_msun: float) -> float:
    mass_kg = solar_mass_to_kg(mass_msun)
    return 2.0 * config.GRAVITATIONAL_CONSTANT * mass_kg / (config.SPEED_OF_LIGHT ** 2)


def infer_default_radius_meters(category: str, mass_msun: float) -> float:
    if category == config.CATEGORY_CATACLYSMIC_VARIABLES:
        return white_dwarf_radius_meters(mass_msun)
    if category == config.CATEGORY_NEUTRON_STARS:
        return neutron_star_radius_meters()
    if category == config.CATEGORY_TRANSIENT_BLACK_HOLES:
        return stellar_black_hole_radius_meters(mass_msun)
    if category == config.CATEGORY_SUPERMASSIVE_BLACK_HOLES:
        return schwarzschild_radius_meters(mass_msun)
    raise ValueError(f"Unknown compact-object category: {category}")


def resolve_accretion_rate_kg_s(row: pd.Series) -> float | None:
    if pd.notna(row.get("mdot_kg_s")):
        return float(row["mdot_kg_s"])
    if pd.notna(row.get("mdot_g_s")):
        return grams_per_second_to_kg_per_s(float(row["mdot_g_s"]))
    if pd.notna(row.get("mdot_msun_yr")):
        return msun_per_year_to_kg_per_s(float(row["mdot_msun_yr"]))
    return None


def reported_power_density_w_per_g(row: pd.Series) -> float | None:
    if pd.notna(row.get("erd_erg_s_g")):
        return erg_per_s_per_g_to_w_per_g(float(row["erd_erg_s_g"]))
    if pd.notna(row.get("power_density_reported_wkg")):
        return w_per_kg_to_w_per_g(float(row["power_density_reported_wkg"]))
    return None


def compute_compact_object_tracks(row: pd.Series) -> list[PowerDensityResult]:
    category = str(row["category"])
    name = str(row["name"])
    mass_msun = float(row["mass_msun"])
    mass_kg = solar_mass_to_kg(mass_msun)
    mass_g = kg_to_grams(mass_kg)

    reported_w_g = reported_power_density_w_per_g(row)
    mdot_kg_s = resolve_accretion_rate_kg_s(row)

    if pd.notna(row.get("radius_m")):
        radius_m = float(row["radius_m"])
    elif pd.notna(row.get("radius_rsun")):
        radius_m = solar_radius_to_m(float(row["radius_rsun"]))
    else:
        radius_m = infer_default_radius_meters(category, mass_msun)

    results: list[PowerDensityResult] = []

    if mdot_kg_s is not None:
        eta_grav = gravitational_efficiency(mass_kg, radius_m)
        luminosity_grav = accretion_luminosity_watts(mdot_kg_s, eta_grav)
        density_kg = power_density_from_luminosity(luminosity_grav, mass_kg)
        density_g = w_per_kg_to_w_per_g(density_kg)
        if reported_w_g is not None:
            density_g = reported_w_g
            density_kg = reported_w_g * config.KG_TO_GRAM
            luminosity_grav = density_kg * mass_kg
            phi_source: PhiSourceType = "tabulated_erd"
            eta_value = float("nan")
        else:
            phi_source = "computed_from_mdot"
            eta_value = eta_grav
        results.append(
            PowerDensityResult(
                name=name,
                category=category,
                mass_kg=mass_kg,
                mass_g=mass_g,
                mdot_kg_s=mdot_kg_s,
                radius_m=radius_m,
                eta=eta_value,
                luminosity_w=luminosity_grav,
                power_density_w_per_kg=density_kg,
                power_density_w_per_g=density_g,
                track="gravitational",
                phi_source=phi_source,
            )
        )

        if category == config.CATEGORY_CATACLYSMIC_VARIABLES:
            eta_nuclear = config.WHITE_DWARF_NUCLEAR_EFFICIENCY
            luminosity_nuclear = accretion_luminosity_watts(mdot_kg_s, eta_nuclear)
            density_nuclear = power_density_from_luminosity(luminosity_nuclear, mass_kg)
            results.append(
                PowerDensityResult(
                    name=name,
                    category=category,
                    mass_kg=mass_kg,
                    mass_g=mass_g,
                    mdot_kg_s=mdot_kg_s,
                    radius_m=radius_m,
                    eta=eta_nuclear,
                    luminosity_w=luminosity_nuclear,
                    power_density_w_per_kg=density_nuclear,
                    power_density_w_per_g=w_per_kg_to_w_per_g(density_nuclear),
                    track="nuclear",
                    phi_source="computed_from_mdot",
                )
            )
    elif reported_w_g is not None:
        density_kg = reported_w_g * config.KG_TO_GRAM
        results.append(
            PowerDensityResult(
                name=name,
                category=category,
                mass_kg=mass_kg,
                mass_g=mass_g,
                mdot_kg_s=float("nan"),
                radius_m=radius_m,
                eta=float("nan"),
                luminosity_w=density_kg * mass_kg,
                power_density_w_per_kg=density_kg,
                power_density_w_per_g=reported_w_g,
                track="gravitational",
                phi_source="tabulated_erd",
            )
        )

    if not results:
        raise ValueError(f"Row '{name}' has neither mdot nor reported ERD.")

    return results


def compute_all_compact_results(dataframe: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for _, row in dataframe.iterrows():
        for result in compute_compact_object_tracks(row):
            records.append(
                {
                    "name": result.name,
                    "category": result.category,
                    "track": result.track,
                    "mass_kg": result.mass_kg,
                    "mass_g": result.mass_g,
                    "mass_msun": result.mass_kg / config.SOLAR_MASS,
                    "mdot_kg_s": result.mdot_kg_s,
                    "radius_m": result.radius_m,
                    "eta": result.eta,
                    "luminosity_w": result.luminosity_w,
                    "power_density_w_per_kg": result.power_density_w_per_kg,
                    "power_density_w_per_g": result.power_density_w_per_g,
                    "phi_source": result.phi_source,
                }
            )
    return pd.DataFrame.from_records(records)


def attach_dubus_wd_uncertainties(
    compact_results: pd.DataFrame,
    dubus_table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge Dubus (2018) MC 68% intervals onto gravitational-track WD rows.

    X: symmetric M1 uncertainty. Y: Ṁ interval propagated to Φ_m at fixed η
    (consistent with the plotted point, which uses tabulated ERD when present).
    """
    result = compact_results.copy()
    for column in (
        "mass_kg_err",
        "power_density_w_per_kg_lo",
        "power_density_w_per_kg_hi",
        "dubus_table",
    ):
        if column not in result.columns:
            if column == "dubus_table":
                result[column] = pd.Series([pd.NA] * len(result), dtype="string")
            else:
                result[column] = np.nan

    dubus_by_name = dubus_table.set_index("name")
    mask = (
        (result["category"] == config.CATEGORY_CATACLYSMIC_VARIABLES)
        & (result["track"] == "gravitational")
    )

    for idx, row in result.loc[mask].iterrows():
        name = str(row["name"])
        if name not in dubus_by_name.index:
            continue
        dubus_row = dubus_by_name.loc[name]
        if isinstance(dubus_row, pd.DataFrame):
            dubus_row = dubus_row.iloc[0]

        mass_msun_err = dubus_row.get("mass_msun_err")
        mass_kg = float(row["mass_kg"])
        mdot_kg_s = float(row["mdot_kg_s"])
        phi = float(row["power_density_w_per_kg"])

        if pd.notna(mass_msun_err) and float(mass_msun_err) > 0:
            mass_kg_err = float(mass_msun_err) * config.SOLAR_MASS
            result.at[idx, "mass_kg_err"] = mass_kg_err
        else:
            mass_kg_err = 0.0

        mdot_lo_g_s = dubus_row.get("mdot_g_s_lo")
        mdot_hi_g_s = dubus_row.get("mdot_g_s_hi")
        dubus_table = dubus_row.get("dubus_table")
        if pd.notna(dubus_table):
            result.at[idx, "dubus_table"] = str(dubus_table)

        if pd.isna(mdot_lo_g_s) or pd.isna(mdot_hi_g_s) or mdot_kg_s <= 0:
            continue

        mdot_lo_kg_s = grams_per_second_to_kg_per_s(float(mdot_lo_g_s))
        mdot_hi_kg_s = grams_per_second_to_kg_per_s(float(mdot_hi_g_s))
        mass_plus = max(mass_kg + mass_kg_err, mass_kg * 1.0e-6)
        mass_minus = max(mass_kg - mass_kg_err, mass_kg * 1.0e-6)

        phi_lo = phi * (mdot_lo_kg_s / mdot_kg_s) * (mass_kg / mass_plus)
        phi_hi = phi * (mdot_hi_kg_s / mdot_kg_s) * (mass_kg / mass_minus)
        if phi_lo > phi_hi:
            phi_lo, phi_hi = phi_hi, phi_lo

        result.at[idx, "power_density_w_per_kg_lo"] = phi_lo
        result.at[idx, "power_density_w_per_kg_hi"] = phi_hi

    return result


def compute_yso_power_density(yso_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Compute YSO power density using Somers (2020) SPOTS-corrected stellar masses.

    Phi_m = L_acc / M_star  with M_star from the Somers inflation of the
    Baraffe+2015 spotless isochrone mass (when available).
    """
    working = yso_dataframe.copy()

    if "mass_msun_somers" in working.columns:
        mass_msun = working["mass_msun_somers"].astype(float)
    else:
        mass_msun = working["mass_msun"].astype(float)

    working["mass_msun"] = mass_msun
    working["mass_kg"] = solar_mass_to_kg(mass_msun)
    working["mass_g"] = kg_to_grams(working["mass_kg"])
    working["lacc_w"] = (10.0 ** working["log_lacc"]) * config.SOLAR_LUMINOSITY
    working["power_density_w_per_kg"] = working["lacc_w"] / working["mass_kg"]
    working["power_density_w_per_g"] = w_per_kg_to_w_per_g(working["power_density_w_per_kg"])
    working["mass_calibration"] = working.get(
        "mass_calibration",
        pd.Series("somers_2020_spots", index=working.index),
    )
    return working


def somers_spots_mass_inflation_factor(spot_coverage_fraction: float) -> float:
    """
    Inflation of pre-MS mass due to starspots (Somers et al. 2020, ApJ 912, 40).

    Spotless isochrone masses underestimate true masses when spots are present.
    At the SPOTS benchmark f_spot = 0.17, typical inflation is ~15--25%.
    """
    f_spot = float(np.clip(spot_coverage_fraction, 0.0, 0.85))
    if f_spot <= 0.0:
        return 1.0
    # Empirical fit to Somers (2020) SPOTS pre-MS tracks (Fig. 12; Sec. 5.2).
    return 1.0 + 0.88 * f_spot / (1.0 - 0.5 * f_spot)


def compute_somers_spots_mass_msun(
    mass_spotless_msun: float,
    *,
    teff_k: float | None = None,
    spot_coverage_fraction: float | None = None,
) -> float:
    """
    Apply Somers (2020) SPOTS spot correction to a Baraffe+2015 spotless mass.

    Teff is retained for provenance and future isochrone interpolation; the
    current implementation uses the published SPOTS inflation factor at the
    configured spot covering fraction.
    """
    if mass_spotless_msun <= 0.0:
        raise ValueError("mass_spotless_msun must be positive.")
    f_spot = (
        config.YSO_CONTROL.spot_coverage_fraction
        if spot_coverage_fraction is None
        else spot_coverage_fraction
    )
    _ = teff_k  # reserved for future SPOTS isochrone lookup
    return mass_spotless_msun * somers_spots_mass_inflation_factor(f_spot)
