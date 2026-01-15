from __future__ import annotations

import datetime as dt
from pathlib import Path

import click

from probate.config import load_config


@click.command()
@click.option("--config", "config_path", default="config/counties.yaml", show_default=True)
@click.option("--date", "run_date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option("--yesterday", "use_yesterday", is_flag=True, default=False)
@click.option("--today", "use_today", is_flag=True, default=False)
def main(config_path: str, run_date: dt.datetime | None, use_yesterday: bool, use_today: bool) -> None:
    """Run the probate pipeline for a given date."""
    config = load_config(Path(config_path))
    resolved_date = _resolve_date(run_date, use_yesterday, use_today, config.run.default_mode)
    click.echo(f"Loaded {len(config.counties)} counties; running for {resolved_date}")


def _resolve_date(
    run_date: dt.datetime | None, use_yesterday: bool, use_today: bool, default_mode: str
) -> dt.date:
    today = dt.date.today()
    if run_date:
        return run_date.date()
    if use_today:
        return today
    if use_yesterday or default_mode == "yesterday":
        return today - dt.timedelta(days=1)
    return today


if __name__ == "__main__":
    main()
