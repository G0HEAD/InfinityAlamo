from __future__ import annotations

import importlib
from typing import Iterable

from probate.config import CountyConfig
from probate.connectors.base import BaseConnector


def load_connectors(counties: Iterable[CountyConfig]) -> list[BaseConnector]:
    connectors: list[BaseConnector] = []
    for county in counties:
        if not county.enabled:
            continue
        module = importlib.import_module(f"probate.connectors.{county.connector}")
        connector_class = getattr(module, "Connector")
        connector = connector_class(county)
        connector.validate_config()
        connectors.append(connector)
    return connectors
