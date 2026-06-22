"""
Main entry point for the Power Density biosignature figure engine.

Run from the project folder:  python main.py
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Pipeline modules live in src/
_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT / "src"))

import config
import data_loader
import dubus_wd_uncertainties
import von_duin_biology
import physics_engine
import plotter
import provenance


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate publication-grade power-density figures."
    )
    parser.add_argument(
        "--compact-csv",
        type=Path,
        default=config.COMPACT_OBJECTS_CSV,
        help="Compact-object master CSV path",
    )
    parser.add_argument(
        "--mdots-dat",
        type=Path,
        default=config.MANARA_MDOTS_DAT,
        help="YSO mdots_forclement.dat path",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def run_pipeline(
    compact_csv: Path | None = None,
    mdots_dat: Path | None = None,
) -> dict[str, Path]:
    logger = logging.getLogger(__name__)

    logger.info("Assembling compact-object master table if needed...")
    compact_raw = data_loader.load_compact_objects(compact_csv)
    summary = data_loader.summarize_dataset(compact_raw)
    logger.info("Compact-object counts:\n%s", summary.to_string(index=False))

    logger.info("Computing compact-object power densities...")
    compact_results = physics_engine.compute_all_compact_results(compact_raw)
    dubus_table = dubus_wd_uncertainties.load_dubus_wd_uncertainties()
    compact_results = physics_engine.attach_dubus_wd_uncertainties(
        compact_results, dubus_table
    )
    compact_export = config.PROCESSED_COMPACT_CSV
    compact_results.to_csv(compact_export, index=False)
    logger.info("Exported %d compact track rows to %s", len(compact_results), compact_export)

    logger.info("Loading YSO control (Somers 2020 SPOTS masses; Alcalá+2017 / Manara+2017 filter)...")
    yso_raw = data_loader.load_mdots_forclement(mdots_dat, rebuild=True)
    yso_results = physics_engine.compute_yso_power_density(yso_raw)
    yso_export = config.PROCESSED_YSO_CSV
    yso_results.to_csv(yso_export, index=False)
    logger.info(
        "Prepared %d YSO control points (f_spot=%.2f).",
        len(yso_results),
        config.YSO_CONTROL.spot_coverage_fraction,
    )

    logger.info("Loading van Duin (2024) ERD compilation (Section I biological systems)...")
    biology_samples = von_duin_biology.combined_biology_table()
    biology_samples.to_csv(config.PROCESSED_BIOLOGY_CSV, index=False)
    biology_summary = von_duin_biology.segment_summary(biology_samples)
    logger.info("Biology segment counts:\n%s", biology_summary.to_string(index=False))

    logger.info("Writing data tracking ledger...")
    ledger_path = provenance.write_tracking_ledger()
    logger.info("Tracking ledger -> %s", ledger_path)

    logger.info("Rendering five ApJ/MNRAS publication figures (PDF)...")
    saved = plotter.save_all_figures(
        compact_results=compact_results,
        yso_results=yso_results,
        biology_samples=biology_samples,
    )

    manifest_path = provenance.write_provenance_manifest(
        compact_results=compact_results,
        yso_results=yso_results,
        biology_results=biology_samples,
        saved_figures=saved,
    )
    logger.info("Provenance manifest -> %s", manifest_path)

    try:
        import importlib.util

        script = config.SCRIPTS_DIR / "build_figure_reference_doc.py"
        spec = importlib.util.spec_from_file_location("build_figure_reference_doc", script)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            doc_path = mod.build_document_from_pipeline(
                compact_results=compact_results,
                yso_results=yso_results,
                biology_results=biology_samples,
            )
            logger.info("Figure reference document -> %s", doc_path)
    except ImportError:
        logger.warning("python-docx not installed; skipping Word document export.")
    except Exception as exc:
        logger.warning("Word document export failed: %s", exc)

    for label, path in saved.items():
        logger.info("Saved %s -> %s", label, path)

    return saved


def main() -> int:
    args = parse_arguments()
    configure_logging(verbose=args.verbose)

    try:
        run_pipeline(
            compact_csv=args.compact_csv,
            mdots_dat=args.mdots_dat,
        )
    except Exception as exc:
        logging.getLogger(__name__).error("Pipeline failed: %s", exc)
        if args.verbose:
            raise
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
