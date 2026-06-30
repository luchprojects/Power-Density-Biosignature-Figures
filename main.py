"""
Generate the three power-density publication figures.

Run from the project folder:  python main.py
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT / "src"))

import config
import data_loader
import dubus_wd_uncertainties
import von_duin_biology
import physics_engine
import plotter


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate publication power-density figures (PDF + PNG)."
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
        help="YSO Manara et al. 2022 data path",
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

    logger.info("Loading compact-object table...")
    compact_raw = data_loader.load_compact_objects(compact_csv)
    compact_results = physics_engine.compute_all_compact_results(compact_raw)
    dubus_table = dubus_wd_uncertainties.load_dubus_wd_uncertainties()
    compact_results = physics_engine.attach_dubus_wd_uncertainties(
        compact_results, dubus_table
    )

    logger.info("Loading SMBH table...")
    smbH_raw = data_loader.load_supermassive_black_holes()
    smbH_results = physics_engine.compute_all_compact_results(smbH_raw)

    logger.info("Loading YSO control sample...")
    yso_raw = data_loader.load_mdots_forclement(mdots_dat)
    yso_results = physics_engine.compute_yso_power_density(yso_raw)

    logger.info("Loading biology reference sample...")
    biology_samples = von_duin_biology.combined_biology_table()

    logger.info("Rendering figures...")
    saved = plotter.save_all_figures(
        compact_results=compact_results,
        yso_results=yso_results,
        biology_samples=biology_samples,
        smbH_results=smbH_results,
    )

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
