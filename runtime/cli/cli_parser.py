from __future__ import annotations

import argparse
from pathlib import Path


VALID_MODES = ("creative_writing", "acf_lite", "narrative", "authority", "utility", "hybrid")
VALID_GRIT = ("low", "medium", "high", "extreme")
VALID_LENGTHS = ("short", "medium", "long")
VALID_PLATFORMS = ("none", "linkedin", "twitter", "instagram", "facebook", "youtube", "reddit")
VALID_VOICE_PROFILES = ("tanya_lawson_v1",)


def non_empty_topic(value: str) -> str:
    topic = value.strip()
    if not topic:
        raise argparse.ArgumentTypeError("--topic cannot be empty.")
    return topic


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_writer.py",
        description="Run the World Class Writing System v7 generator from the command line.",
    )
    parser.add_argument("--topic", type=non_empty_topic, required=True, help="Topic or prompt focus for the run.")
    parser.add_argument("--mode", choices=VALID_MODES, default="narrative", help="Writing mode.")
    parser.add_argument("--grit", choices=VALID_GRIT, default="medium", help="Grit intensity.")
    parser.add_argument("--platform", choices=VALID_PLATFORMS, default="none", help="Platform target.")
    parser.add_argument("--length", choices=VALID_LENGTHS, default="long", help="Requested output length.")
    parser.add_argument(
        "--voice_profile",
        choices=VALID_VOICE_PROFILES,
        default="tanya_lawson_v1",
        help="Voice profile to apply.",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("runs/local_cli_run"),
        help="Directory where run artifacts will be saved.",
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Validate inputs and write the normalized run config without generating output.",
    )
    return parser


def parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)
