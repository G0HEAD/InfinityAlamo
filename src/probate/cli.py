from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from probate.config import load_config
from probate.pipeline import run_from_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="InfinityAlamo pipeline")
    parser.add_argument("--config", default="config/counties.yaml")
    parser.add_argument("--date", help="Run for specific date YYYY-MM-DD")
    parser.add_argument("--yesterday", action="store_true")
    parser.add_argument("--today", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    tz = ZoneInfo(config.run.timezone)

    if args.date:
        target_date = date.fromisoformat(args.date)
    elif args.today:
        target_date = datetime.now(tz).date()
    else:
        target_date = datetime.now(tz).date() - timedelta(days=1)

    run_from_config(args.config, target_date)


if __name__ == "__main__":
    main()
